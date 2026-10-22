import pygame
from abc import ABC, abstractmethod
from music import overlay_music_in_loop, start_music, stop_music
from utilities import center_of, load_set_from_file, save_lines_to_file
from settings import FONT_PATH, WHITE, BUTTON_SOUND, PURCHASE_SOUND, PURCHASED_CARS_FILE, PURCHASED_MAPS_FILE
import re
import time


class Menu:
    """
    Клас Menu представляє головне меню гри.
    Відповідає за відображення кнопок, зворотний відлік та опції гри.
    """
    KEY_BINDINGS = [
        ('Key bindings:', (835, 200)),
        ('ESC - pause the game', (770, 265)),
        ('M - turn music on/off', (772, 315)),
        ('N - play the next audio track', (720, 365)),
    ]

    AVATAR_SIZE = 120
    PLAYER_ROW_LEFT = 250
    PLAYER_ROW_CENTER_Y = 400
    PLAYER_ROW_RIGHT = 250
    BOT_ROW_CENTER_Y = 230

    def __init__(self, x, y, username="Yahtzee", score_file="score.txt", avatar_path="img/user_icon.png", avatar_bot_path="img/bot_icon.png"):
        """
        Ініціалізує об'єкт головного меню.

        :param x: Координата X центру меню.
        :param y: Координата Y центру меню.
        """
        self.x = x
        self.y = y
        self.imageStart = self.load_image("img/start.png", (289, 143))  # Кнопка "Старт"
        self.imageOptions = self.load_image("img/options.png", (289, 143))  # Кнопка "Опції"
        self.imageBack = self.load_image("img/back.png", (288, 103))  # Кнопка "Назад"
        self.leadorboard = self.load_image("img/leaderboard_new.png", (1234, 817))  # Таблиця лідерів
        self.rating_btn = self.load_image("img/rating_btn.png", (287, 141))  # Кнопка "Рейтинг"
        self.menu_back_bnt = self.load_image("img/menu_btn.png", (232, 83))  # Кнопка повернення в меню
        self.on_music = self.load_image("img/on_music.png", (288, 103))  # Кнопка увімкнення музики
        self.off_music = self.load_image("img/off_music.png", (287, 103))  # Кнопка вимкнення музики
        self.leadorboard_rect = self.leadorboard.get_rect(topleft=(x - 460, y - 400))  # Прямокутник таблиці лідерів
        self.start_rect = self.imageStart.get_rect(topleft=(x, y - 75))  # Прямокутник кнопки "Старт"
        self.options_rect = self.imageOptions.get_rect(topleft=(x, y + 275))  # Прямокутник кнопки "Опції"
        self.back_rect = self.imageBack.get_rect(topleft=(x, y + 400))  # Прямокутник кнопки "Назад" (опції)
        self.back_rect2 = self.imageBack.get_rect(topleft=(x, y + 500))  # Прямокутник кнопки "Назад" (рейтинг)
        self.rating_btn_rect = self.rating_btn.get_rect(topleft=(x, y + 100))  # Прямокутник кнопки "Рейтинг"
        self.menu_back_rect = self.menu_back_bnt.get_rect(topleft=(x - 790, y - 440))  # Прямокутник повернення в меню
        self.on_music_rect = self.on_music.get_rect(topleft=(x, y))  # Прямокутник кнопки увімкнення музики
        self.off_music_rect = self.off_music.get_rect(topleft=(x, y + 140))  # Прямокутник кнопки вимкнення музики

        # Параметри повзунка гучності
        self.slider_x = self.off_music_rect.x
        self.slider_y = self.off_music_rect.y + self.off_music_rect.height + 50
        self.slider_width = 288
        self.slider_height = 10
        self.slider_knob_radius = 10
        self.volume = 0.5  # Початкова гучність (0.0 - 1.0)
        self.knob_x = self.slider_x + int(self.volume * self.slider_width)  # Позиція повзунка
        self.dragging = False  # Прапорець перетягування повзунка

        self.username = username
        self.score_file = score_file
        self.avatar = self.load_image(avatar_path, (self.AVATAR_SIZE, self.AVATAR_SIZE))
        self.avatar_bot = self.load_image(avatar_bot_path, (self.AVATAR_SIZE, self.AVATAR_SIZE))
        self.rating_font = pygame.font.Font(FONT_PATH, 48)

    def load_image(self, path, size):
        """
        Завантажує та масштабує зображення.

        :param path: Шлях до файлу зображення.
        :param size: Кортеж із шириною та висотою для масштабування.
        :return: Масштабоване зображення Pygame.
        """
        img = pygame.image.load(path)
        return pygame.transform.scale(img, size)

    def draw(self, screen):
        """
        Малює головне меню на екрані.

        :param screen: Поверхня Pygame для відображення.
        """
        screen.blit(self.imageStart, self.start_rect.topleft)
        screen.blit(self.imageOptions, self.options_rect.topleft)
        screen.blit(self.rating_btn, self.rating_btn_rect.topleft)

    def countdown(self, countdown_images, screen, roads, car, car1, car2, bot, aspect_ratio, mode_choice):
        """
        Відображає зворотний відлік перед початком гри.

        :param countdown_images: Список зображень для відліку (3, 2, 1, GO).
        :param screen: Поверхня Pygame для відображення.
        :param roads: Об'єкт класу Roads для малювання дороги.
        :param car: Автомобіль для одиночного режиму.
        :param car1: Перший автомобіль для двогравцевого режиму.
        :param car2: Другий автомобіль для двогравцевого режиму.
        :param bot: Бот для одиночного режиму.
        :param aspect_ratio: Розмір екрану (ширина, висота).
        :param mode_choice: Режим гри ('single' або 'doubles').
        """
        overlay_music_in_loop("soundeffects/321go.mp3")  # Відтворення звуку відліку
        racers = (car, bot) if mode_choice == 'single' else (car1, car2)
        for img in countdown_images:
            screen.fill((0, 0, 0))  # Очищення екрану
            roads.draw(screen)  # Малювання дороги
            for racer in racers:
                racer.draw(screen)
            img_rect = img.get_rect(center=center_of(aspect_ratio))
            screen.blit(img, img_rect)
            pygame.display.update()
            time.sleep(1)  # Затримка 1 секунда між зображеннями

    def render_key_bindings(self):
        font = pygame.font.Font(FONT_PATH, 36)
        rendered = []
        for text, topleft in self.KEY_BINDINGS:
            surface = font.render(text, True, WHITE)
            rendered.append((surface, surface.get_rect(topleft=topleft)))
        return rendered

    def draw_options(self, screen, background, key_bindings):
        screen.fill((0, 0, 0))
        screen.blit(background, (0, 0))
        screen.blit(self.imageBack, self.back_rect)
        screen.blit(self.on_music, self.on_music_rect)
        screen.blit(self.off_music, self.off_music_rect)
        for surface, rect in key_bindings:
            screen.blit(surface, rect)

        # Малювання повзунка гучності
        pygame.draw.rect(screen, (200, 200, 200), (self.slider_x, self.slider_y, self.slider_width, self.slider_height))
        pygame.draw.circle(screen, (59, 59, 59), (self.knob_x, self.slider_y + self.slider_height // 2), self.slider_knob_radius)
        pygame.display.update()

    def is_on_slider_knob(self, pos):
        return abs(pos[0] - self.knob_x) < self.slider_knob_radius * 2 and \
            self.slider_y - self.slider_knob_radius < pos[1] < self.slider_y + self.slider_knob_radius

    def handle_options_click(self, pos):
        if self.on_music_rect.collidepoint(pos):
            overlay_music_in_loop(BUTTON_SOUND)
            start_music()  # Увімкнення музики
        if self.off_music_rect.collidepoint(pos):
            overlay_music_in_loop(BUTTON_SOUND)
            stop_music()  # Вимкнення музики
        if self.back_rect.collidepoint(pos):
            overlay_music_in_loop(BUTTON_SOUND)
            return True
        if self.is_on_slider_knob(pos):
            self.dragging = True
        return False

    def update_volume(self, mouse_x):
        self.knob_x = max(self.slider_x, min(mouse_x, self.slider_x + self.slider_width))
        self.volume = (self.knob_x - self.slider_x) / self.slider_width
        pygame.mixer.music.set_volume(self.volume)  # Оновлення гучності

    def show_options(self, screen, background):
        """
        Відображає меню налаштувань гри.

        :param screen: Поверхня Pygame для відображення.
        :param background: Фонове зображення.
        """
        options_active = True
        key_bindings = self.render_key_bindings()

        while options_active:
            self.draw_options(screen, background, key_bindings)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    options_active = False
                    pygame.quit()
                    exit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.handle_options_click(event.pos):
                            options_active = False
                            return
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.dragging = False
                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging:
                        self.update_volume(event.pos[0])

    def load_score(self):
        """
        Читає очки гравця з файлу.
        """
        with open(self.score_file, "r") as file:
            self.current_score = int(file.read().strip())
        return self.current_score

    def draw_player_row(self, screen, name_surface, score_surface):
        """
        Малює рядок гравця на таблиці лідерів: іконка, ім'я та очки.

        :param screen: Поверхня Pygame для відображення.
        :param name_surface: Готовий рендер імені.
        :param score_surface: Готовий рендер очок.
        """
        board = self.leadorboard_rect
        center_y = board.top + self.PLAYER_ROW_CENTER_Y

        avatar_rect = self.avatar.get_rect(midleft=(board.left + self.PLAYER_ROW_LEFT, center_y))
        name_rect = name_surface.get_rect(midleft=(avatar_rect.right + 30, center_y))
        score_rect = score_surface.get_rect(midright=(board.right - self.PLAYER_ROW_RIGHT, center_y))

        screen.blit(self.avatar, avatar_rect)
        screen.blit(name_surface, name_rect)
        screen.blit(score_surface, score_rect)

    def draw_bot_row(self, screen, name_surface, score_surface):
        """
        Малює рядок бота на таблиці лідерів: іконка, ім'я та очки.

        :param screen: Поверхня Pygame для відображення.
        :param name_surface: Готовий рендер імені.
        :param score_surface: Готовий рендер очок.
        """
        board = self.leadorboard_rect
        center_y = board.top + self.BOT_ROW_CENTER_Y

        avatar_bot_rect = self.avatar_bot.get_rect(midleft=(board.left + self.PLAYER_ROW_LEFT, center_y))
        name_rect = name_surface.get_rect(midleft=(avatar_bot_rect.right + 30, center_y))
        score_rect = score_surface.get_rect(midright=(board.right - self.PLAYER_ROW_RIGHT, center_y))

        screen.blit(self.avatar_bot, avatar_bot_rect)
        screen.blit(name_surface, name_rect)
        screen.blit(score_surface, score_rect)

    def show_rating(self, screen, background):
        """
        Відображає таблицю лідерів із іконкою, ім'ям та очками гравця.

        :param screen: Поверхня Pygame для відображення.
        :param background: Фонове зображення.
        """
        # Очки читаємо один раз при відкритті екрана, а не щокадру
        name_surface = self.rating_font.render(self.username, True, WHITE)
        score_surface_player = self.rating_font.render(str(self.load_score()), True, WHITE)
        score_surface_bot = self.rating_font.render(str(10000), True, WHITE)

        rating_active = True
        while rating_active:
            screen.fill((0, 0, 0))
            screen.blit(background, (0, 0))
            screen.blit(self.imageBack, self.back_rect2)
            screen.blit(self.leadorboard, self.leadorboard_rect)
            self.draw_player_row(screen, name_surface, score_surface_player)
            self.draw_bot_row(screen, name_surface, score_surface_bot)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    rating_active = False
                    pygame.quit()
                    exit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.back_rect2.collidepoint(event.pos):
                        overlay_music_in_loop(BUTTON_SOUND)
                        return


class ConfigurationMenu(ABC):
    """
    Абстрактний базовий клас для конфігураційних меню (карти, машини, режими).
    """
    def __init__(self, x, y):
        """
        Ініціалізує базові параметри конфігураційного меню.

        :param x: Координата X центру меню.
        :param y: Координата Y центру меню.
        """
        self.x = x
        self.y = y
        self.font = pygame.font.Font(FONT_PATH, 36)  # Шрифт для тексту
        self.title_font = pygame.font.Font(FONT_PATH, 56)  # Шрифт для заголовків

    def load_image(self, path):
        """
        Завантажує зображення.

        :param path: Шлях до файлу зображення.
        :return: Завантажене зображення Pygame.
        """
        return pygame.image.load(path)

    def draw_text(self, text, x, y, screen, font=None):
        """
        Малює текст на екрані.

        :param text: Текст для відображення.
        :param x: Координата X центру тексту.
        :param y: Координата Y центру тексту.
        :param screen: Поверхня Pygame для відображення.
        :param font: Шрифт (за замовчуванням None, використовується self.font).
        """
        if font is None:
            font = self.font
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=(x, y))
        screen.blit(text_surface, text_rect)

    def draw_labels(self, screen, labels):
        for text, rect in labels:
            self.draw_text(text, rect.centerx, rect.top - 30, screen)

    def try_purchase(self, item_name, item_type, purchased_items, save):
        if self.score.purchase_item(item_name, item_type):
            overlay_music_in_loop(PURCHASE_SOUND)
            purchased_items.add(item_name)
            save()

    @staticmethod
    def find_clicked(pos, buttons):
        for rect, value in buttons:
            if rect.collidepoint(pos):
                return value
        return None

    @abstractmethod
    def draw(self):
        """Абстрактний метод для малювання меню."""
        pass

    @abstractmethod
    def check_click(self):
        """Абстрактний метод для обробки кліків."""
        pass


class MapsMenu(ConfigurationMenu):
    """
    Клас MapsMenu представляє меню вибору карт.
    """
    def __init__(self, x, y, score, file_path=PURCHASED_MAPS_FILE):
        """
        Ініціалізує меню вибору карт.

        :param x: Координата X центру меню.
        :param y: Координата Y центру меню.
        :param score: Об'єкт класу Score для управління очками.
        :param file_path: Шлях до файлу з купленими картами.
        """
        super().__init__(x, y)
        self.file_path = file_path
        self.score = score
        self.purchased_maps = self.load_purchased_maps()
        self.image_map3 = self.load_image("img/map3_preview.png")
        self.image_map2 = self.load_image("img/map2_preview.png")
        self.image_beach = self.load_image("img/beach_preview.png")
        self.image_winter = self.load_image("img/winter_preview.png")
        self.image_summer = self.load_image("img/summer_preview.png")
        self.image_champions_field = self.load_image("img/champions_field_preview.png")
        self.image_beach_lock = self.load_image("img/beach_lock.png")
        self.image_winter_lock = self.load_image("img/winter_lock.png")
        self.image_summer_lock = self.load_image("img/summer_lock.png")
        self.image_champions_field_lock = self.load_image("img/champions_field_lock.png")
        self.buy_image = self.load_image("img/5000.png")
        self.map3_rect = self.image_map3.get_rect(topleft=(x, y + 90))
        self.map2_rect = self.image_map2.get_rect(topleft=(x, y + 550))
        self.beach_rect = self.image_beach.get_rect(topleft=(x + 600, y + 90))
        self.winter_rect = self.image_winter.get_rect(topleft=(x + 600, y + 550))
        self.summer_rect = self.image_summer.get_rect(topleft=(x + 1200, y + 90))
        self.champions_field_rect = self.image_champions_field.get_rect(topleft=(x + 1200, y + 550))
        self.buy_image_rect = self.buy_image.get_rect(topleft=(x + 750, y + 410))
        self.buy_image_rect2 = self.buy_image.get_rect(topleft=(x + 1350, y + 410))
        self.buy_image_rect3 = self.buy_image.get_rect(topleft=(x + 1350, y + 870))
        self.buy_image_rect4 = self.buy_image.get_rect(topleft=(x + 750, y + 870))

    def load_purchased_maps(self):
        """
        Завантажує список куплених карт із файлу.

        :return: Множина назв куплених карт.
        """
        return load_set_from_file(self.file_path)

    def save_purchased_maps(self):
        """Зберігає список куплених карт у файл."""
        save_lines_to_file(self.file_path, self.purchased_maps)

    def purchase_map(self, map_name):
        """
        Додає карту до списку куплених.

        :param map_name: Назва карти.
        """
        if map_name not in self.purchased_maps:
            self.purchased_maps.add(map_name)
            self.save_purchased_maps()

    def free_maps(self):
        return [
            ('map3', self.image_map3, self.map3_rect),
            ('map2', self.image_map2, self.map2_rect),
        ]

    def locked_maps(self):
        return [
            ('beach', self.image_beach, self.image_beach_lock, self.beach_rect),
            ('winter', self.image_winter, self.image_winter_lock, self.winter_rect),
            ('summer', self.image_summer, self.image_summer_lock, self.summer_rect),
            ('champions_field', self.image_champions_field, self.image_champions_field_lock, self.champions_field_rect),
        ]

    def buy_buttons(self):
        return [
            (self.buy_image_rect, 'beach'),
            (self.buy_image_rect2, 'summer'),
            (self.buy_image_rect3, 'champions_field'),
            (self.buy_image_rect4, 'winter'),
        ]

    def draw(self, screen):
        """
        Малює меню вибору карт на екрані.

        :param screen: Поверхня Pygame для відображення.
        """
        for _, image, rect in self.free_maps():
            screen.blit(image, rect.topleft)
        for map_name, image, lock_image, rect in self.locked_maps():
            screen.blit(image if map_name in self.purchased_maps else lock_image, rect.topleft)

        for buy_rect, map_name in self.buy_buttons():
            if map_name not in self.purchased_maps:
                screen.blit(self.buy_image, buy_rect.topleft)

        self.draw_text("Select a map:", self.beach_rect.centerx, self.y - 50, screen, self.title_font)
        self.draw_labels(screen, [
            ("Tidal Heatwave", self.map3_rect),
            ("Meadow Rush", self.map2_rect),
            ("Palm Paradise", self.beach_rect),
            ("Frozen Tides", self.winter_rect),
            ("Evergreen Escape", self.summer_rect),
            ("Champions Field", self.champions_field_rect),
        ])
        self.score.draw_score(screen)

    def check_click(self, pos):
        """
        Обробляє клік миші у меню карт.

        :param pos: Координати кліку (x, y).
        :return: Назва вибраної карти або None.
        """
        map_to_buy = self.find_clicked(pos, self.buy_buttons())
        if map_to_buy:
            self.try_purchase(map_to_buy, "map", self.purchased_maps, self.save_purchased_maps)

        for map_name, _, rect in self.free_maps():
            if rect.collidepoint(pos):
                return map_name
        for map_name, _, _, rect in self.locked_maps():
            if rect.collidepoint(pos) and map_name in self.purchased_maps:
                return map_name
        return None


class CarsMenu(ConfigurationMenu):
    """
    Клас CarsMenu представляє меню вибору автомобілів.
    """
    def __init__(self, x, y, score, file_path=PURCHASED_CARS_FILE):
        """
        Ініціалізує меню вибору автомобілів.

        :param x: Координата X центру меню.
        :param y: Координата Y центру меню.
        :param score: Об'єкт класу Score для управління очками.
        :param file_path: Шлях до файлу з купленими автомобілями.
        """
        super().__init__(x, y)
        self.file_path = file_path
        self.score = score
        self.purchased_cars = self.load_purchased_cars()
        self.image_car1 = self.load_image("img/car1_preview.png")
        self.image_car2 = self.load_image("img/car2_preview.png")
        self.image_car3 = self.load_image("img/car3_preview.png")
        self.image_car4 = self.load_image("img/car4_preview.png")
        self.image_car5 = self.load_image("img/car5_preview.png")
        self.image_car1_lock = self.load_image("img/car1_lock.png")
        self.image_car2_lock = self.load_image("img/car2_lock.png")
        self.image_car3_lock = self.load_image("img/car3_lock.png")
        self.buy_image = self.load_image("img/3000.png")
        self.car1_rect = self.image_car1.get_rect(topleft=(x + 1200, y + 60))
        self.car2_rect = self.image_car2.get_rect(topleft=(x + 600, y + 60))
        self.car3_rect = self.image_car3.get_rect(topleft=(x + 900, y + 550))
        self.car4_rect = self.image_car4.get_rect(topleft=(x + 300, y + 550))
        self.car5_rect = self.image_car5.get_rect(topleft=(x, y + 60))
        self.buy_image_rect = self.buy_image.get_rect(topleft=(x + 1325, y + 400))
        self.buy_image2_rect = self.buy_image.get_rect(topleft=(x + 725, y + 400))
        self.buy_image3_rect = self.buy_image.get_rect(topleft=(x + 1025, y + 890))

    def load_purchased_cars(self):
        """
        Завантажує список куплених автомобілів із файлу.

        :return: Множина назв куплених автомобілів.
        """
        return load_set_from_file(self.file_path)

    def save_purchased_cars(self):
        """Зберігає список куплених автомобілів у файл."""
        save_lines_to_file(self.file_path, self.purchased_cars)

    def purchase_car(self, car_name):
        """
        Додає автомобіль до списку куплених.

        :param car_name: Назва автомобіля.
        """
        if car_name not in self.purchased_cars:
            self.purchased_cars.add(car_name)
            self.save_purchased_cars()

    def locked_cars(self):
        return [
            ('car1', self.image_car1, self.image_car1_lock, self.car1_rect),
            ('car2', self.image_car2, self.image_car2_lock, self.car2_rect),
            ('car3', self.image_car3, self.image_car3_lock, self.car3_rect),
        ]

    def free_cars(self):
        return [
            ('car4', self.image_car4, self.car4_rect),
            ('car5', self.image_car5, self.car5_rect),
        ]

    def buy_buttons(self):
        return [
            (self.buy_image_rect, 'car1'),
            (self.buy_image2_rect, 'car2'),
            (self.buy_image3_rect, 'car3'),
        ]

    def draw(self, screen):
        """
        Малює меню вибору автомобілів на екрані.

        :param screen: Поверхня Pygame для відображення.
        """
        for car_name, image, lock_image, rect in self.locked_cars():
            screen.blit(image if car_name in self.purchased_cars else lock_image, rect.topleft)
        for _, image, rect in self.free_cars():
            screen.blit(image, rect.topleft)

        for buy_rect, car_name in self.buy_buttons():
            if car_name not in self.purchased_cars:
                screen.blit(self.buy_image, buy_rect.topleft)

        self.draw_text("Select a car:", self.car2_rect.centerx, self.y - 50, screen, self.title_font)
        self.draw_labels(screen, [
            ("Ferrari 458 Challenge", self.car1_rect),
            ("Mclaren P1 Sports", self.car2_rect),
            ("Ford Mustang Shelby", self.car3_rect),
            ("Subaru Impreza WRX STI", self.car4_rect),
            ("Dodge Viper GTS", self.car5_rect),
        ])
        self.score.draw_score(screen)

    def selected_car(self, pos):
        for car_name, _, _, rect in self.locked_cars():
            if rect.collidepoint(pos) and car_name in self.purchased_cars:
                return car_name
        for car_name, _, rect in self.free_cars():
            if rect.collidepoint(pos):
                return car_name
        return None

    def check_click(self, pos):
        """
        Обробляє клік миші у меню автомобілів.

        :param pos: Координати кліку (x, y).
        :return: Назва вибраного автомобіля або None.
        """
        car_to_buy = self.find_clicked(pos, self.buy_buttons())
        if car_to_buy:
            self.try_purchase(car_to_buy, "car", self.purchased_cars, self.save_purchased_cars)

        car_name = self.selected_car(pos)
        if car_name:
            overlay_music_in_loop(BUTTON_SOUND)
        return car_name


class ModesMenu(ConfigurationMenu):
    """
    Клас ModesMenu представляє меню вибору режимів гри.
    """
    def __init__(self, x, y):
        """
        Ініціалізує меню вибору режимів гри.

        :param x: Координата X центру меню.
        :param y: Координата Y центру меню.
        """
        super().__init__(x, y)
        self.image_single = self.load_image("img/single.png")
        self.image_doubles = self.load_image("img/doubles.png")
        self.single_rect = self.image_single.get_rect(topleft=(x - 40, y + 250))
        self.doubles_rect = self.image_doubles.get_rect(topleft=(x + 890, y + 250))

    def draw(self, screen):
        """
        Малює меню вибору режимів на екрані.

        :param screen: Поверхня Pygame для відображення.
        """
        screen.blit(self.image_single, self.single_rect.topleft)
        screen.blit(self.image_doubles, self.doubles_rect.topleft)
        self.draw_text("Select the game mode:", self.x + 855, self.y + 50, screen, self.title_font)
        self.draw_labels(screen, [
            ("Single", self.single_rect),
            ("Doubles", self.doubles_rect),
        ])

    def check_click(self, pos, mode_choice):
        """
        Обробляє клік миші у меню режимів.

        :param pos: Координати кліку (x, y).
        :param mode_choice: Поточний режим гри.
        :return: Новий режим гри або None.
        """
        mode = self.find_clicked(pos, [(self.single_rect, 'single'), (self.doubles_rect, 'doubles')])
        if mode:
            overlay_music_in_loop(BUTTON_SOUND)
        return mode
