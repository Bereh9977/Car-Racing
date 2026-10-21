import pygame
from game_objects import Cars, Bots, Roads, Obstacles, Finish, Score
from menus import Menu, MapsMenu, CarsMenu, ModesMenu
from music import overlay_music_in_loop, next_track, mute_music, music_playing
from utilities import scale_image
from maps_config import get_map_config
from settings import (SCREEN_SIZE, WINDOW_TITLE, FPS, FONT_PATH, WHITE, MENU_BACKGROUND,
                      FINISH_IMAGE, COIN_IMAGE, BUTTON_SOUND, CAR_IMAGES, DEFAULT_CAR_IMAGE, CARSCENE_MAP2, AUDIO_MAP2, CARSCENE_WINTER, AUDIO_WINTER)
import cv2

pygame.init()

def is_left_click(event):
    return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1


class GameSys:
    """
    Основний клас гри, що управляє логікою гри, відображенням та взаємодією з гравцем.

    Цей клас ініціалізує всі об'єкти гри (машини, боти, дороги, меню тощо),
    управляє основним циклом гри та обробляє введення користувача.
    """
    def __init__(self):
        """Ініціалізація основних параметрів гри."""
        self.running = True  # Прапорець для роботи основного циклу гри
        self.aspect_ratio = SCREEN_SIZE  # Роздільна здатність екрану
        self.screen = pygame.display.set_mode(self.aspect_ratio)  # Створення вікна гри
        pygame.display.set_caption(WINDOW_TITLE)  # Заголовок вікна
        self.background = pygame.image.load(MENU_BACKGROUND)  # Фон для меню
        self.car = Cars(400, 997, 0, 0, 0, CAR_IMAGES['car1'], 'wasd')  # Основна машина для одиночного режиму
        self.bot = Bots(400, 992, 0, 0, 0, [])  # Бот для одиночного режиму
        self.menu = Menu(800, 450)  # Головне меню
        self.roads = Roads('img/winter.jpg', 'img/winter_edge.png')  # Дороги (карта)
        self.obs = Obstacles('img/snowflake.png', 'img/banana.png', 'img/sand.png')  # Перешкоди
        self.countdown_images = self.load_countdown_images()  # Зображення для зворотного відліку
        self.in_menu = True  # Прапорець перебування в меню
        self.score = Score(COIN_IMAGE)  # Об'єкт для підрахунку очок
        self.maps_page = MapsMenu(80, 100, self.score)  # Меню вибору карт
        self.cars_page = CarsMenu(90, 100, self.score)  # Меню вибору машин
        self.modes_page = ModesMenu(100, 100)  # Меню вибору режимів
        self.choosing_map = False  # Прапорець вибору карти
        self.choosing_car = False  # Прапорець вибору машини
        self.choosing_mode = False  # Прапорець вибору режиму
        self.map_choice = '0'  # Обрана карта
        self.mode_choice = '0'  # Обраний режим
        self.car1 = Cars(400, 997, 0, 0.5, 0, DEFAULT_CAR_IMAGE, 'wasd')  # Перша машина для двогравцевого режиму
        self.car2 = Cars(500, 997, 0, 0.5, 0, DEFAULT_CAR_IMAGE, 'arrows')  # Друга машина для двогравцевого режиму
        self.pause_font = pygame.font.Font(FONT_PATH, 36)  # Шрифт для тексту паузи
        self.pause_text = self.pause_font.render('Paused', True, WHITE)  # Текст паузи
        self.pause_rect = self.pause_text.get_rect(center=(self.aspect_ratio[0]//2 - 15, self.aspect_ratio[1]//2))  # Позиція тексту паузи

    @staticmethod
    def load_countdown_images():
        return [
            pygame.image.load('img/3.png'),
            scale_image(pygame.image.load('img/2.png'), 2),
            pygame.image.load('img/1.png'),
            pygame.image.load('img/GO.png')
        ]

    def run(self):
        """
        Основний цикл гри.

        Цей метод запускає гру, відображає меню, оновлює екран та обробляє події.
        """
        new_game = True  # Прапорець для запуску нової гри
        clock = pygame.time.Clock()  # Об'єкт для регулювання FPS
        while self.running:
            if new_game:
                self.start_new_game()
                new_game = False  # Вимикаємо прапорець нової гри після запуску

            self.draw_track()

            if self.mode_choice == 'single':
                new_game = self.update_single()
            else:
                new_game = self.update_doubles()

            pygame.display.update()  # Оновлення екрану

            if self.handle_game_events():
                new_game = True  # Повернення до меню

            self.handle_road_collisions()
            self.bot.move()  # Рух бота
            clock.tick(FPS)  # Обмеження FPS

        pygame.quit()  # Завершення роботи Pygame

    def start_new_game(self):
        self.in_menu = True  # Повернення в меню перед новою грою
        self.show_menu()  # Відображення головного меню
        if self.map_choice == "map2":
            self.show_catscene(CARSCENE_MAP2, AUDIO_MAP2) # ffmpeg -i video/begin_winter.mp4 -vn -acodec libmp3lame -q:a 2 video/begin_winter.mp3
        if self.map_choice == "winter":
            self.show_catscene(CARSCENE_WINTER, AUDIO_WINTER)
        self.menu.countdown(self.countdown_images, self.screen, self.roads, self.car, self.car1, self.car2, self.bot, self.aspect_ratio, self.mode_choice)  # Зворотний відлік

    def show_catscene(self, video_path, audio_path):
        """Відтворення відеокатсцени перед початком гонки."""
        video = cv2.VideoCapture(video_path)
        clock = pygame.time.Clock()
        video_fps = video.get(cv2.CAP_PROP_FPS)

        if not video_fps or video_fps <= 0:
            video_fps = 30

        playing = True
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()
        while playing and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    playing = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        playing = False

            if not playing:
                break

            success, frame = video.read()
            if not success:
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
            frame_surface = pygame.transform.scale(frame_surface, self.screen.get_size())

            self.screen.blit(frame_surface, (0, 0))
            pygame.display.flip()

            clock.tick(video_fps)

        video.release()
        pygame.mixer.music.stop()

    def draw_track(self):
        self.roads.draw(self.screen)  # Відображення доріг
        self.finish.draw(self.screen)  # Відображення фінішу
        self.obs.draw_obstackles(self.screen, self.map_choice)  # Відображення перешкод

    def update_single(self):
        self.score.draw_coins(self.screen)  # Малювання монет
        self.car.draw(self.screen)  # Малювання гравця
        self.car.update_car(self.obs, self.map_choice, self.score)  # Оновлення стану гравця
        self.bot.draw(self.screen)  # Малювання бота
        new_game = self.finish.crossed(self.screen, self.aspect_ratio, self.car, self.bot, self.score)  # Перевірка перетину фінішу
        self.score.draw_score(self.screen)  # Відображення очок
        return new_game

    def update_doubles(self):
        for car in (self.car1, self.car2):
            car.draw(self.screen)
            car.update_car(self.obs, self.map_choice, self.score, self.mode_choice)
        return self.finish.crossed(self.screen, self.aspect_ratio, self.car1, self.car2)  # Перевірка перетину фінішу

    def handle_game_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False  # Закриття гри
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not self.handle_pause():  # Виклик меню паузи
                        return True
                elif event.key == pygame.K_n:
                    if music_playing.is_set():
                        next_track()  # Перемикання треку
                elif event.key == pygame.K_m:
                    mute_music()  # Вимкнення музики
        return False

    def handle_road_collisions(self):
        for car in (self.car, self.car1, self.car2):
            if car.collide(self.roads.contour_mask):
                car.bounce()  # Відштовхування від країв

    def draw_page(self, page):
        self.screen.blit(self.background, (0, 0))
        page.draw(self.screen)
        pygame.display.update()

    def show_menu(self):
        """
        Відображення головного меню гри.

        Цей метод малює меню та обробляє взаємодію з кнопками (старт, опції, рейтинг).
        """
        while self.in_menu:
            self.draw_page(self.menu)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.in_menu = False
                    pygame.quit()
                    exit()
                    return
                elif is_left_click(event):
                    self.handle_main_menu_click(event.pos)

    def handle_main_menu_click(self, pos):
        if self.menu.start_rect.collidepoint(pos):
            overlay_music_in_loop(BUTTON_SOUND)  # Звук кліку
            self.in_menu = False
            self.choosing_mode = True
            self.show_modes()  # Перехід до вибору режиму
        elif self.menu.options_rect.collidepoint(pos):
            overlay_music_in_loop(BUTTON_SOUND)
            self.menu.show_options(self.screen, self.background)  # Відображення налаштувань
        elif self.menu.rating_btn_rect.collidepoint(pos):
            overlay_music_in_loop(BUTTON_SOUND)
            self.menu.show_rating(self.screen, self.background)  # Відображення рейтингу

    def show_maps(self):
        """
        Відображення меню вибору карти.

        Цей метод дозволяє гравцеві обрати карту для гри.
        """
        while self.choosing_map:
            self.draw_page(self.maps_page)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.choosing_map = False
                    pygame.quit()
                    return
                elif is_left_click(event):
                    self.map_choice = self.maps_page.check_click(event.pos)  # Вибір карти
                    if self.map_choice:
                        self.choose_maps(self.map_choice)  # Ініціалізація обраної карти

    def choose_maps(self, map_choice):
        """
        Ініціалізація обраної карти.

        Args:
            map_choice (str): Назва обраної карти.
        """
        print(f"Selected map: {map_choice}")
        self.roads = Roads(f"img/{map_choice}.jpg", f"img/{map_choice}_edge.png")  # Завантаження карти
        self.choosing_map = False
        if self.mode_choice == 'single':
            self.create_objects_single(map_choice)  # Ініціалізація об'єктів для одиночного режиму
        else:
            self.create_objects_doubles(map_choice)  # Ініціалізація об'єктів для двогравцевого режиму

    def show_cars(self):
        """
        Відображення меню вибору машини.

        Цей метод дозволяє обрати машину для одиночного режиму або переходить до вибору карти для двогравцевого.
        """
        if self.mode_choice == 'doubles':
            self.choosing_car = False
            self.choosing_map = True
            self.show_maps()  # У двогравцевому режимі вибір машини пропускається
        while self.choosing_car:
            self.draw_page(self.cars_page)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.choosing_car = False
                    pygame.quit()
                    return
                elif is_left_click(event):
                    car_choice = self.cars_page.check_click(event.pos)  # Вибір машини
                    if car_choice:
                        self.choose_cars(car_choice)  # Ініціалізація обраної машини

    def choose_cars(self, car_choice):
        """
        Ініціалізація обраної машини.

        Args:
            car_choice (str): Назва обраної машини.
        """
        print(f"Selected car: {car_choice}")
        self.choosing_car = False
        self.image = CAR_IMAGES.get(car_choice, DEFAULT_CAR_IMAGE)
        self.choosing_map = True
        self.show_maps()  # Перехід до вибору карти

    def show_modes(self):
        """
        Відображення меню вибору режиму гри (одинарний або двогравцевий).
        """
        while self.choosing_mode:
            self.draw_page(self.modes_page)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.choosing_mode = False
                    pygame.quit()
                    return
                elif is_left_click(event):
                    self.mode_choice = self.modes_page.check_click(event.pos, self.mode_choice)  # Вибір режиму
                    if self.mode_choice:
                        self.choose_modes()  # Ініціалізація режиму

    def choose_modes(self):
        """Ініціалізація обраного режиму гри."""
        print(f"Selected mode: {self.mode_choice}")
        self.choosing_mode = False
        self.choosing_car = True
        self.show_cars()  # Перехід до вибору машини

    def create_finish(self, config):
        self.finish_location = config.finish_location
        self.finish = Finish(FINISH_IMAGE, *self.finish_location, *config.finish_args, **config.finish_kwargs)

    def create_objects_single(self, map_choice):
        """
        Створення об'єктів для одиночного режиму.

        Args:
            map_choice (str): Назва обраної карти.
        """
        config = get_map_config(map_choice)
        self.create_finish(config)
        self.car = Cars(*config.single_car, self.image, 'wasd')
        self.bot = Bots(*config.bot, list(config.bot_points))
        self.score = Score(COIN_IMAGE, map_choice)  # Ініціалізація очок для карти

    def create_objects_doubles(self, map_choice):
        """
        Створення об'єктів для двогравцевого режиму.

        Args:
            map_choice (str): Назва обраної карти.
        """
        config = get_map_config(map_choice)
        car1_position, car2_position = config.doubles_cars
        self.create_finish(config)
        self.car1 = Cars(*car1_position, CAR_IMAGES['car1'], 'wasd')
        self.car2 = Cars(*car2_position, CAR_IMAGES['car2'], 'arrows')

    def handle_pause(self):
        """
        Обробляє стан паузи гри, дозволяючи змінювати налаштування або вийти в головне меню.

        Ця функція викликається, коли гравець натискає ESC під час гри. Вона зупиняє
        основний ігровий цикл та відображає меню паузи. У меню можна:
        - Відкрити налаштування.
        - Вийти в головне меню.
        - Продовжити гру, натиснувши ESC.

        Returns:
            bool: True, якщо гравець продовжує гру.
                  False, якщо гравець виходить у головне меню або закриває гру.
        """
        paused = True
        while paused:
            for event in pygame.event.get():
                if is_left_click(event):
                    if self.menu.options_rect.collidepoint(event.pos):
                        self.menu.show_options(self.screen, self.background)  # Відкриття налаштувань
                    if self.menu.menu_back_rect.collidepoint(event.pos):
                        return False  # Вихід у головне меню
                if event.type == pygame.QUIT:
                    self.running = False
                    quit()
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return True  # Продовження гри

            self.draw_pause_screen()

        return True

    def draw_pause_screen(self):
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.pause_text, self.pause_rect)
        self.screen.blit(self.menu.imageOptions, self.menu.options_rect.topleft)
        self.screen.blit(self.menu.menu_back_bnt, self.menu.menu_back_rect)
        pygame.display.flip()


if __name__ == "__main__":
    """Запуск гри."""
    game = GameSys()
    game.run()
