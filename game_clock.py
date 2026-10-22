import pygame


class FixedTimestep:
    """
    Годинник з фіксованим кроком симуляції.

    Рух машин розраховується кроками однакової тривалості незалежно від FPS,
    тому швидкість гри однакова на всіх комп'ютерах.
    """
    def __init__(self, step_rate, max_frame_time):
        """
        :param step_rate: Кількість кроків симуляції за секунду.
        :param max_frame_time: Максимальний час кадру (в секундах), що враховується за один раз.
        """
        self.step_us = round(1_000_000 / step_rate)
        self.max_frame_us = round(max_frame_time * 1_000_000)
        self.clock = pygame.time.Clock()
        self.accumulator_us = 0

    def reset(self):
        """Скидає накопичений час (після меню, паузи чи зворотного відліку)."""
        self.clock.tick()
        self.accumulator_us = 0

    def tick(self, fps):
        """
        Обмежує FPS і додає час, що минув з попереднього кадру.

        :param fps: Максимальна кількість кадрів за секунду.
        """
        frame_us = round(self.clock.tick(fps) * 1000)
        self.accumulator_us += min(frame_us, self.max_frame_us)

    def steps(self):
        """Повертає кроки симуляції, які потрібно виконати в цьому кадрі."""
        while self.accumulator_us >= self.step_us:
            self.accumulator_us -= self.step_us
            yield
