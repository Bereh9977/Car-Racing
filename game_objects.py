import pygame
import random
import math
import time
from utilities import scale_image
from music import overlay_music_in_loop
import os

class Cars:
    def __init__(self, x, y, speed, max_speed, angle, current_image, controls):
        self.angle = angle
        self.x = x  
        self.y = y  
        self.prev_coordinates = (x, y)
        self.starting_position = (x, y)  
        self.starting_angle = angle
        self.image = self.load_image(f"D:/CarRacing/{current_image}")
        self.current_image = scale_image(self.image, 0.5)
        self.rect = self.current_image.get_rect(center=(x, y))
        self.rotation_intensity = 0.6
        self.rotation_direction = 0
        self.speed = speed
        self.max_speed = max_speed
        self.acceleration = 0.01
        self.max_backward_speed = -0.4
        self.freeze_time = 0  # Час, коли машина замерзла
        self.ice_image = pygame.image.load('ice-cube.png')  # Завантажуємо зображення льоду
        self.show_ice = False  # Флаг для показу льоду
        self.ice_time = 0  # Час початку показу льоду
        self.spinning = False  # Чи машина обертається
        self.spin_time = 0  # Час початку обертання
        self.spin_duration = 1  # Тривалість обертання (в секундах)
        self.spin_speed = 5  # Швидкість обертання (градусів за кадр)
        self.frozen = False
        self.controls = controls
    
    def load_image(self, base_path):
        return pygame.image.load(f"{base_path}")
    
    def check_freeze(self):
        if self.frozen and time.time() - self.freeze_time >= 1:  # Чекаємо 1 секунду
            self.frozen = False  # Відновлюємо рух

    def check_spin(self):
        if self.spinning and time.time() - self.spin_time >= self.spin_duration:
            self.spinning = False  # Закінчити обертання

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.current_image, self.angle)
        new_rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, new_rect.topleft)

        # Накласти лід, якщо машина заморожена
        if self.show_ice:
            screen.blit(self.ice_image, self.rect.topleft)  # Накладаємо лід на машину
            if pygame.time.get_ticks() - self.ice_time >= 1000:  # Якщо пройшла 1 секунда
                self.show_ice = False  # Сховати лід

    def get_drive_direction(self):
        drive_direction = None
        keys = pygame.key.get_pressed()

        if self.controls == 'wasd':
            if keys[pygame.K_w]:
                drive_direction = 'forward'
            elif keys[pygame.K_s]:
                drive_direction = 'backward'
        elif self.controls == 'arrows':
            if keys[pygame.K_UP]:
                drive_direction = 'forward'
            elif keys[pygame.K_DOWN]:
                drive_direction = 'backward'
        return drive_direction


    def get_rotation_direction(self, drive_direction):
        keys = pygame.key.get_pressed()
        rotation_direction = 0

        if self.controls == 'wasd':
            if (drive_direction == 'forward' or self.speed > 0):
                if keys[pygame.K_d]:
                    rotation_direction = -1
                elif keys[pygame.K_a]:
                    rotation_direction = 1
            elif (drive_direction == 'backward' or self.speed < 0):
                if keys[pygame.K_d]:
                    rotation_direction = 1
                elif keys[pygame.K_a]:
                    rotation_direction = -1

        elif self.controls == 'arrows':
            if (drive_direction == 'forward' or self.speed > 0):
                if keys[pygame.K_RIGHT]:
                    rotation_direction = -1
                elif keys[pygame.K_LEFT]:
                    rotation_direction = 1
            elif (drive_direction == 'backward' or self.speed < 0):
                if keys[pygame.K_RIGHT]:
                    rotation_direction = 1
                elif keys[pygame.K_LEFT]:
                    rotation_direction = -1

        return rotation_direction

    def rotate(self):
        self.angle += self.rotation_intensity * self.rotation_direction

    def drive_forward(self):
        self.speed = min(self.speed + self.acceleration, self.max_speed)
        self.drive_forward_shift()

    def drive_forward_shift(self):
        angle_value = math.radians(self.angle)
        vertical_shift = self.speed * math.cos(angle_value)
        horizontal_shift = self.speed * (-math.sin(angle_value))
        self.y -= vertical_shift 
        self.x += horizontal_shift
        self.rect.center = (self.x, self.y)

    def drive_backward(self):
        self.speed = max(self.speed - self.acceleration, self.max_backward_speed)
        self.drive_backward_shift()
    
    def drive_backward_shift(self):
        angle_value = math.radians(self.angle)
        vertical_shift = self.speed * (-math.cos(angle_value))
        horizontal_shift = self.speed * math.sin(angle_value)
        self.y += vertical_shift 
        self.x -= horizontal_shift
        self.rect.center = (self.x, self.y)

    def reduce_speed_forward(self):
        self.speed = max(self.speed - self.acceleration / 4, 0)
        self.drive_forward_shift()

    def reduce_speed_backward(self):
        self.speed = min(self.speed + self.acceleration / 4, 0)
        self.drive_backward_shift()

    def collide(self, mask, x=0, y=0):
        """
        Перевіряє зіткнення автомобіля з заданою маскою.

        :param mask: Маска об'єкта, з яким перевіряється зіткнення.
        :param x: Зміщення по осі X (за замовчуванням 0).
        :param y: Зміщення по осі Y (за замовчуванням 0).
        :return: Координати точки зіткнення або None, якщо зіткнення немає.
        """
        car_mask = pygame.mask.from_surface(self.current_image)
        width, height = car_mask.get_size()
        offset = (int(self.rect.centerx - x - width // 2), int(self.rect.centery - y - height // 2))
        point_of_intersection = mask.overlap(car_mask, offset)
        return point_of_intersection

    def bounce(self):
        """
        Виконує відскок автомобіля після зіткнення, змінюючи напрямок руху.

        Швидкість змінюється на протилежну з коефіцієнтом загасання 0.65.
        Якщо автомобіль рухався вперед, після відскоку він рухається назад, і навпаки.
        """
        self.speed = -0.65 * self.speed

        if self.speed > 0:
            self.drive_backward()  # Відскок назад
        else:
            self.drive_forward()  # Відскок вперед

    def cross_finish(self, finish_collision_point, required_side):
        """
        Перевіряє, чи перетнув автомобіль фінішну лінію з правильної сторони.

        :param finish_collision_point: Координати точки зіткнення з фінішною лінією.
        :param required_side: Сторона, з якої має бути перетнута лінія ("top" або "bottom").
        :return: True, якщо автомобіль коректно перетнув фініш, інакше False.
        """
        if finish_collision_point is None:
            self.prev_coordinates = self.x, self.y
            return False
        else:
            collision_y = finish_collision_point[1]

            if (required_side == "top" and collision_y == 0) or (required_side == "bottom" and collision_y > 0):
                return True
            else:
                self.x, self.y = self.prev_coordinates
                return False
    
    def reset(self):
        """
        Скидає позицію автомобіля до початкових координат та швидкості.

        Після скидання автомобіль повертається на стартову позицію та перестає рухатися.
        """
        self.x, self.y = self.starting_position
        self.angle = self.starting_angle
        self.speed = 0.01

    
    def obstakles_feaches(self, obs, map_choice):
        if obs.check_collision_obstackles(self.rect, map_choice):  # Якщо машина торкається об'єкта
            if map_choice == "winter":
                self.frozen = True
                overlay_music_in_loop("D:/CarRacing/soundeffects/ice_sound.mp3")
                self.freeze_time = time.time()
                self.show_ice = True  # Показати лід
                self.ice_time = pygame.time.get_ticks()  # Час початку накладання льоду
                obs.show_snowflakes = False
                return
            elif map_choice == "beach" or map_choice == "map3":
                self.spinning = True  # Почати обертання
                overlay_music_in_loop("D:/CarRacing/soundeffects/spinning.mp3")
                self.spin_time = time.time()  # Запам'ятати час початку
                return
            elif map_choice == "map2":  
            # Якщо поворот ще не активовано, ініціалізуємо його
                if not hasattr(self, "sand_turning") or time.time() - self.sand_turn_start >= 1.5: 
                    self.sand_turning = random.choice([-1, 1])  # Випадковий напрямок повороту
                    self.sand_turn_start = time.time()  # Час початку повороту
                else:
                    self.angle += self.sand_turning * 0.5  # Плавний поворот (0.5 градуса за кадр)
    
    def update_car(self, obs, map_choice, score, mode_choice = 'single'):
        self.check_freeze()  # Перевіряємо, чи закінчився час заморозки
        self.check_spin()  # Перевіряємо, чи закінчилося обертання

        if self.frozen:
            return  # Блокуємо рух, поки машина заморожена

        if self.spinning:
            self.angle += self.spin_speed  # Плавне обертання
            return             
        
        # Перевірка на зіштовхнення з монетками
        if mode_choice == 'single':
            score.check_collision(self.rect)
        self.obstakles_feaches(obs, map_choice)      
        drive_direction = self.get_drive_direction()
        rotation_direction = self.get_rotation_direction(drive_direction)
        self.rotation_direction = rotation_direction
        self.rotate()
        moved = False

        if drive_direction == 'forward':
            moved = True
            self.drive_forward()
        elif drive_direction == 'backward':
            moved = True
            self.drive_backward()

        if not moved:
            if self.speed > 0:
                self.reduce_speed_forward()
            elif self.speed < 0:
                self.reduce_speed_backward()
            else:
                pass

class Bots(Cars):
    def __init__(self, x, y, speed, max_speed, angle, points):
        available_cars = [
            "car1.png", "car2.png", "car3.png", "car4.png", "car5.png"
        ]
        current_image = random.choice(available_cars)
        controls = 'wasd'
        super().__init__(x, y, speed, max_speed, angle, current_image, controls)

        self.target_y = 400  # Цільова координата Y
        self.current_point = 0
        self.points = points

    def draw_points(self, screen):
        for point in self.points:
            pygame.draw.circle(screen, (255, 0, 0), point, 5)  # Малюємо кульки червоним кольором

    def calculate_angle(self):
        target_x, target_y = self.points[self.current_point]
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        if y_diff == 0:
            desired_radian_angle = math.pi / 2
        else:
            desired_radian_angle = math.atan(x_diff / y_diff)

        if target_y > self.y:
            desired_radian_angle += math.pi

        difference_in_angle = self.angle - math.degrees(desired_radian_angle)
        if difference_in_angle >= 180:
            difference_in_angle -= 360

        if difference_in_angle > 0:
            self.angle -= min(self.rotation_intensity, abs(difference_in_angle))
        else:
            self.angle += min(self.rotation_intensity, abs(difference_in_angle))

    def update_points(self):
        target = self.points[self.current_point]
        rect = pygame.Rect(
            self.x, self.y, self.current_image.get_width(), self.current_image.get_height())
        if rect.collidepoint(*target):
            self.current_point += 1

    def move(self):
        if self.current_point >= len(self.points):
            return

        self.calculate_angle()
        self.update_points()
        if self.controls == 'wasd':
            super().drive_forward()    

    def reset(self):
        self.x, self.y = self.starting_position
        self.angle = self.starting_angle
        self.speed = 0
        self.current_point = 0

class Roads:
    def __init__(self, imagePath, animSpeed):
        self.image = pygame.image.load(imagePath)
        self.x = 0
        self.y = 0
        self.anim_speed = animSpeed

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

class Obstacles:
    def __init__(self, x, y, imagePath, imagePath2, imagePath3):
        self.image = pygame.image.load(imagePath)
        self.image2 = pygame.image.load(imagePath2)
        self.image3 = pygame.image.load(imagePath3)
        self.snowflakes = [(539, 1025), (607, 577), (96, 780), (1588, 285), 
                           (1395, 434), (1269, 657), (1679, 746), (628, 244), 
                           (248, 1024), (1137, 708), (1821, 492), (360, 302)]  # Координати сніжинок
        self.banana = [(1069, 555), (850, 1019), (1262, 522), (1632, 599),
                        (1586, 854), (552, 851), (343, 919), (356, 690),
                        (216, 481), (285, 505), (661, 887), (1610, 925)]
        self.banana2 = [(100, 900), (79, 737), (136, 497), (424, 50), 
                        (781, 165), (1240, 280), (1379, 173), (1547, 262), 
                        (1684, 456), (1345, 580), (1043, 563), (844, 665)]
        self.sand = [(545, 805), (1329, 791), (1282, 469), (533, 503),
                     (308, 196), (716, 651), (244, 715), (987, 193),
                     (923, 610), (457, 867), (1256, 536), (187, 340)]
        self.snowflakes_rand = random.sample(self.snowflakes, 4)
        self.banana_rand = random.sample(self.banana, 4)
        self.banana2_rand = random.sample(self.banana2, 4)
        self.sand_rand = random.sample(self.sand, 4)
        self.snowflake_rects = [pygame.Rect(x, y, self.image.get_width(), self.image.get_height()) for x, y in self.snowflakes_rand]
        self.banana_rects = [pygame.Rect(x, y, self.image2.get_width(), self.image2.get_height()) for x, y in self.banana_rand]
        self.banana2_rects = [pygame.Rect(x, y, self.image2.get_width(), self.image2.get_height()) for x, y in self.banana2_rand]
        self.sand_rects = [pygame.Rect(x, y, self.image3.get_width(), self.image3.get_height()) for x, y in self.sand_rand]
        self.show_snowflakes = True
        self.show_banana = True

    def draw_obstackles(self, screen, map_choice):
        if map_choice == "winter":
            for i, (x, y) in enumerate(self.snowflakes_rand):
                screen.blit(self.image, (x, y))
                self.snowflake_rects[i].topleft = (x, y)  # Оновлюємо позицію
        elif map_choice =='beach':
            for i, (x, y) in enumerate(self.banana_rand):
                screen.blit(self.image2, (x, y))
                self.banana_rects[i].topleft = (x, y)
        elif map_choice =='map3':
            for i, (x, y) in enumerate(self.banana2_rand):
                screen.blit(self.image2, (x, y))
                self.banana2_rects[i].topleft = (x, y)
        elif map_choice =='map2':
            for i, (x, y) in enumerate(self.sand_rand):
                screen.blit(self.image3, (x, y))
                self.sand_rects[i].topleft = (x, y)

    def check_collision_obstackles(self, car_rect, map_choice):
        if map_choice == "winter":
            for i, rect in enumerate(self.snowflake_rects):
                if rect.colliderect(car_rect):
                    # Якщо зіткнення, видалити сніжинку
                    self.snowflakes_rand.pop(i)
                    self.snowflake_rects.pop(i)
                    return True  # Зіткнення відбулося
        elif map_choice =='beach':
            for i, rect in enumerate(self.banana_rects):
                if rect.colliderect(car_rect):
                    self.banana_rand.pop(i)
                    self.banana_rects.pop(i)
                    return True
        elif map_choice =='map3':
            for i, rect in enumerate(self.banana2_rects):
                if rect.colliderect(car_rect):
                    self.banana2_rand.pop(i)
                    self.banana2_rects.pop(i)
                    return True
        elif map_choice =='map2':
            for i, rect in enumerate(self.sand_rects):
                if rect.colliderect(car_rect):
                    return True
        return False  # Якщо зіткнення не було
    
class Score:
    """
    Клас для керування очками гравця та монетами у грі.

    Відповідає за розміщення монет на карті, підрахунок очок,
    збереження та завантаження очок із файлу, а також їхнє відображення на екрані.
    """

    def __init__(self, image_path, map_choice="none", file_path="score.txt", car_file_path="purchased_cars.txt", map_file_path="purchased_maps.txt"):
        """
        Ініціалізує об'єкт очок та монет.

        :param image_path: Шлях до зображення монети.
        :param map_choice: Назва карти для визначення можливих розташувань монет.
                           Якщо "none", монети будуть розміщені випадково.
        :param file_path: Шлях до файлу для збереження очок.
        """
        self.image = scale_image(pygame.image.load(image_path), 0.07)
        self.file_path = file_path
        self.car_purchased = False  # Додаємо змінну, яка відстежує покупку
        self.map_purchased = False  
        self.car_file_path = car_file_path
        self.map_file_path = map_file_path
        self.buy_price = 3000
        self.buy_price2 = 5000
        self.buy_prices = {"car": 3000, "map": 5000}  # Ціна для машин і карт
        
        # Визначення можливих позицій монет для кожної карти
        self.coin_positions = {
            "winter": [(515, 286), (630, 580), (219, 521), (179, 904), (605, 1009), 
                       (881, 909), (1166, 632), (1377, 463), (1761, 583), (1712, 260)],
            "beach": [(385, 932), (193, 521), (549, 366), (708, 702), (825, 1032), 
                      (950, 610), (1263, 549), (1383, 310), (1620, 521), (1588, 835)],
            "map3": [(40, 503), (190, 748), (488, 941), (766, 594), (1283, 586), 
                     (1772, 371), (1577, 157), (1180, 295), (744, 91), (117, 156)],
            "map2": [(162, 218), (165, 748), (564, 945), (1170, 849), (1540, 707), 
                     (1441, 287), (1228, 22), (1056, 367), (582, 590), (538, 86)],
            "summer": [(373, 869), (716, 686), (1003, 608), (923, 296), (462, 479), 
                       (648, 176), (1008, 64), (1311, 247), (1165, 525), (1568, 776)],
            "champions_field": [(376, 914), (711, 905), (1145, 960), (1494, 746), (1567, 391), 
                                (1404, 84), (1103, 158), (765, 132), (320, 199), (391, 521)],
            "none": [(random.randint(100, 1800), random.randint(100, 900)) for _ in range(5)]
        }

        # Вибираємо 5 випадкових монет із доступних позицій або всі, якщо їх менше
        available_positions = self.coin_positions.get(map_choice, [])
        self.coins = random.sample(available_positions, min(5, len(available_positions)))

        # Створення об'єктів Rect для перевірки зіткнень
        self.coin_rects = [pygame.Rect(x, y, self.image.get_width(), self.image.get_height()) for x, y in self.coins]

        self.last_score = -1
        self.font = pygame.font.Font("D:/CarRacing/AveriaSansLibre-Bold.ttf", 36)
        self.score_pos = (1700, 10)  # Збереження позиції

        # Завантаження очок із файлу
        self.load_score()

    def load_score(self):
        """
        Завантажує очки з файлу. Якщо файл не існує або пошкоджений, встановлює 0.
        """
        try:
            with open(self.file_path, "r") as file:
                self.current_score = int(file.read().strip())
        except (FileNotFoundError, ValueError):
            self.current_score = 0

    def save_score(self):
        """
        Зберігає поточну кількість очок у файл.
        """
        with open(self.file_path, "w") as file:
            file.write(str(self.current_score))

    def draw_coins(self, screen):
        """
        Малює монети на екрані.
d
        :param screen: Поверхня Pygame, на якій відображається гра.
        """
        for i, (x, y) in enumerate(self.coins):
            screen.blit(self.image, (x, y))
            self.coin_rects[i].topleft = (x, y)

    def check_collision(self, car_rect):
        """
        Перевіряє, чи автомобіль зіткнувся з монетою. Якщо так, монета видаляється та додаються очки.

        :param car_rect: Прямокутник (pygame.Rect), що представляє колізію автомобіля.
        :return: True, якщо зіткнення було, False інакше.
        """
        for i, rect in enumerate(self.coin_rects):
            if rect.colliderect(car_rect):
                self.coins.pop(i)
                self.coin_rects.pop(i)
                overlay_music_in_loop("D:/CarRacing/soundeffects/coin_collect.mp3")
                self.add_score(100)
                return True
        return False

    def load_purchases(self, file_path):
        """Завантажує куплені авто або карти"""
        if not os.path.exists(file_path):
            return set()
        with open(file_path, "r") as file:
            return set(file.read().splitlines())

    def save_purchases(self, file_path, purchases):
        """Зберігає куплені авто або карти"""
        with open(file_path, "w") as file:
            file.write("\n".join(purchases))

    def purchase_item(self, item_name, item_type):
        """
        Універсальний метод покупки для машин і карт.

        :param item_name: Назва авто або карти.
        :param item_type: Тип ("car" або "map").
        :return: True, якщо покупка вдала, інакше False.
        """
        if item_type not in self.buy_prices:
            return False  # Некоректний тип товару

        file_path = self.car_file_path if item_type == "car" else self.map_file_path
        purchased_items = self.load_purchases(file_path)
        price = self.buy_prices[item_type]

        if self.current_score >= price and item_name not in purchased_items:
            purchased_items.add(item_name)
            self.current_score -= price
            self.save_score()
            self.save_purchases(file_path, purchased_items)
            return True
        return False

    def add_score(self, amount):
        """
        Додає вказану кількість очок та зберігає оновлений рахунок.

        :param amount: Кількість очок для додавання.
        """
        self.current_score += amount
        self.save_score()

    def subtract_score(self, amount):
        """
        Віднімає вказану кількість очок та зберігає оновлений рахунок.

        :param amount: Кількість очок для віднімання.
        """
        self.current_score -= amount
        self.save_score()

    def clear_score(self):
        """
        Обнуляє рахунок гравця та зберігає зміни у файлі.
        """
        self.current_score = 0
        self.save_score()

    def draw_score(self, screen):
        """
        Відображає поточну кількість очок у правому верхньому куті екрана.

        :param screen: Поверхня Pygame, на якій відображається гра.
        """
        if self.current_score != self.last_score:
             self.last_score = self.current_score
             self.score_text = self.font.render(f"Score: {self.current_score}", True, (255, 255, 255))

        screen.blit(self.score_text, self.score_pos)

    def is_item_purchased(self, item_name, item_type):
        """
        Перевіряє, чи куплений товар (авто або карта).

        :param item_name: Назва авто або карти.
        :param item_type: Тип ("car" або "map").
        :return: True, якщо куплено, False інакше.
        """
        file_path = self.car_file_path if item_type == "car" else self.map_file_path
        purchased_items = self.load_purchases(file_path)
        return item_name in purchased_items

    def check_buy_click(self, pos, item_name, buy_rect, item_type):
        """
        Обробляє клік по кнопці покупки (універсальний метод для авто і карт).

        :param pos: Координати кліку.
        :param item_name: Назва авто або карти.
        :param buy_rect: Прямокутник кнопки покупки.
        :param item_type: Тип товару ("car" або "map").
        :return: True, якщо покупка вдала, інакше False.
        """
        if buy_rect.collidepoint(pos) and not self.is_item_purchased(item_name, item_type):
            return self.purchase_item(item_name, item_type)
        return False

class Finish:
    """
    Клас Finish представляє фінішну лінію у грі. Відповідає за відстеження проходження 
    фінішу машинами, підрахунок кіл та виведення результатів.
    """

    def __init__(self, imagePath, x, y, angle, scale_value, required_side="top", required_circles=1):
        """
        Ініціалізує об'єкт фінішу.

        :param imagePath: Шлях до зображення фінішної лінії.
        :param x: Початкова координата X.
        :param y: Початкова координата Y.
        :param angle: Кут повороту фінішної лінії.
        :param scale_value: Масштабування зображення.
        :param required_side: Сторона, з якої необхідно перетнути фініш (за замовчуванням "top").
        :param required_circles: Кількість необхідних кіл для завершення гонки.
        """
        self.image = scale_image(pygame.image.load(imagePath), scale_value)
        self.x = x
        self.y = y
        self.angle = angle
        self.required_side = required_side
        self.required_circles = required_circles
        self.car1_wins, self.car2_wins = 0, 0

    def draw(self, screen):
        """
        Малює фінішну лінію на екрані.

        :param screen: Екран, на якому відображається фініш.
        """
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        self.mask = pygame.mask.from_surface(rotated_image)
        screen.blit(rotated_image, (self.x, self.y))

    def crossed(self, screen, aspect_ratio, car1, car2, score = None):
        """
        Визначає, чи перетнула машина фінішну лінію, та підраховує кола.

        :param screen: Екран для відображення результатів.
        :param aspect_ratio: Співвідношення сторін екрану.
        :param car1: Об'єкт першої машини.
        :param car2: Об'єкт другої машини.
        :return: True, якщо гонка завершена, інакше False.
        """

        if self.car1_wins + self.car2_wins == self.required_circles:
            if self.car1_wins > self.car2_wins:
                self.show_result(screen, aspect_ratio, 'Car 1 Wins!', "D:/CarRacing/soundeffects/car1_win.mp3")
                self.credit_prize(score, 200)
            elif self.car1_wins < self.car2_wins:
                self.show_result(screen, aspect_ratio, 'Car 2 Wins!', "D:/CarRacing/soundeffects/car2_win.mp3")
            else:
                self.show_result(screen, aspect_ratio, 'It\'s a Tie!', "D:/CarRacing/soundeffects/tie.mp3")
                self.credit_prize(score, 100)
            return True

        else:
            car1_collision_point = car1.collide(self.mask, self.x, self.y)
            car2_collision_point = car2.collide(self.mask, self.x, self.y)
            if car1.cross_finish(car1_collision_point, self.required_side):
                if self.car1_wins == 0: 
                    overlay_music_in_loop("D:/CarRacing/soundeffects/car1_win_pt1.mp3") 
                self.car1_wins += 1
                self.display_circle_number(screen, aspect_ratio)
                car1.reset()
                car2.reset()
                time.sleep(4)
        
            elif car2.cross_finish(car2_collision_point, self.required_side):
                if self.car2_wins == 0: 
                    overlay_music_in_loop("D:/CarRacing/soundeffects/car2_win_pt1.mp3")
                self.car2_wins += 1
                self.display_circle_number(screen, aspect_ratio)
                car1.reset()
                car2.reset()
                time.sleep(4)
            return False

    def credit_prize(self, score, amount):
        if score != None:
            score.add_score(amount)

    def display_circle_number(self, screen, aspect_ratio):
        """
        Відображає поточний номер кола на екрані.

        :param screen: Екран, на якому відображається номер кола.
        :param aspect_ratio: Співвідношення сторін екрану.
        """
        font = pygame.font.Font("D:/CarRacing/AveriaSansLibre-Bold.ttf", 72)
        text = font.render(f"Circle #{self.car1_wins + self.car2_wins} out of {self.required_circles} done!", True, (255, 0, 0))
        text_rect = text.get_rect(center=(aspect_ratio[0] // 2, aspect_ratio[1] // 2))
        screen.blit(text, text_rect)
        pygame.display.update()
        time.sleep(1)

    def show_result(self, screen, aspect_ratio, message, musicPath):
        """
        Відображає фінальний результат гонки на екрані.

        :param screen: Екран, на якому відображається результат.
        :param aspect_ratio: Співвідношення сторін екрану.
        :param message: Текст повідомлення про переможця.
        """
        font = pygame.font.Font("D:/CarRacing/AveriaSansLibre-Bold.ttf", 72)
        text = font.render(message, True, (255, 0, 0))
        text_rect = text.get_rect(center=(aspect_ratio[0] // 2, aspect_ratio[1] // 2))
        screen.blit(text, text_rect)
        pygame.display.update()
        overlay_music_in_loop(musicPath)
        time.sleep(5)
        
class Finish:
    """
    Клас Finish представляє фінішну лінію у грі. Відповідає за відстеження проходження 
    фінішу машинами, підрахунок кіл та виведення результатів.
    """

    def __init__(self, imagePath, x, y, angle, scale_value, required_side="top", required_circles=1):
        """
        Ініціалізує об'єкт фінішу.

        :param imagePath: Шлях до зображення фінішної лінії.
        :param x: Початкова координата X.
        :param y: Початкова координата Y.
        :param angle: Кут повороту фінішної лінії.
        :param scale_value: Масштабування зображення.
        :param required_side: Сторона, з якої необхідно перетнути фініш (за замовчуванням "top").
        :param required_circles: Кількість необхідних кіл для завершення гонки.
        """
        self.image = scale_image(pygame.image.load(imagePath), scale_value)
        self.x = x
        self.y = y
        self.angle = angle
        self.required_side = required_side
        self.required_circles = required_circles
        self.car1_wins, self.car2_wins = 0, 0

    def draw(self, screen):
        """
        Малює фінішну лінію на екрані.

        :param screen: Екран, на якому відображається фініш.
        """
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        self.mask = pygame.mask.from_surface(rotated_image)
        screen.blit(rotated_image, (self.x, self.y))

    def crossed(self, screen, aspect_ratio, car1, car2, score = None):
        """
        Визначає, чи перетнула машина фінішну лінію, та підраховує кола.

        :param screen: Екран для відображення результатів.
        :param aspect_ratio: Співвідношення сторін екрану.
        :param car1: Об'єкт першої машини.
        :param car2: Об'єкт другої машини.
        :return: True, якщо гонка завершена, інакше False.
        """

        if self.car1_wins + self.car2_wins == self.required_circles:
            if self.car1_wins > self.car2_wins:
                self.show_result(screen, aspect_ratio, 'Car 1 Wins!', "D:/CarRacing/soundeffects/car1_win.mp3")
                self.credit_prize(score, 200)
            elif self.car1_wins < self.car2_wins:
                self.show_result(screen, aspect_ratio, 'Car 2 Wins!', "D:/CarRacing/soundeffects/car2_win.mp3")
            else:
                self.show_result(screen, aspect_ratio, 'It\'s a Tie!', "D:/CarRacing/soundeffects/tie.mp3")
                self.credit_prize(score, 100)
            return True

        else:
            car1_collision_point = car1.collide(self.mask, self.x, self.y)
            car2_collision_point = car2.collide(self.mask, self.x, self.y)
            if car1.cross_finish(car1_collision_point, self.required_side):
                if self.car1_wins == 0: 
                    overlay_music_in_loop("D:/CarRacing/soundeffects/car1_win_pt1.mp3") 
                self.car1_wins += 1
                self.display_circle_number(screen, aspect_ratio)
                car1.reset()
                car2.reset()
                time.sleep(4)
        
            elif car2.cross_finish(car2_collision_point, self.required_side):
                if self.car2_wins == 0: 
                    overlay_music_in_loop("D:/CarRacing/soundeffects/car2_win_pt1.mp3")
                self.car2_wins += 1
                self.display_circle_number(screen, aspect_ratio)
                car1.reset()
                car2.reset()
                time.sleep(4)
            return False

    def credit_prize(self, score, amount):
        if score != None:
            score.add_score(amount)

    def display_circle_number(self, screen, aspect_ratio):
        """
        Відображає поточний номер кола на екрані.

        :param screen: Екран, на якому відображається номер кола.
        :param aspect_ratio: Співвідношення сторін екрану.
        """
        font = pygame.font.Font("D:/CarRacing/AveriaSansLibre-Bold.ttf", 72)
        text = font.render(f"Circle #{self.car1_wins + self.car2_wins} out of {self.required_circles} done!", True, (255, 0, 0))
        text_rect = text.get_rect(center=(aspect_ratio[0] // 2, aspect_ratio[1] // 2))
        screen.blit(text, text_rect)
        pygame.display.update()
        time.sleep(1)

    def show_result(self, screen, aspect_ratio, message, musicPath):
        """
        Відображає фінальний результат гонки на екрані.

        :param screen: Екран, на якому відображається результат.
        :param aspect_ratio: Співвідношення сторін екрану.
        :param message: Текст повідомлення про переможця.
        """
        font = pygame.font.Font("D:/CarRacing/AveriaSansLibre-Bold.ttf", 72)
        text = font.render(message, True, (255, 0, 0))
        text_rect = text.get_rect(center=(aspect_ratio[0] // 2, aspect_ratio[1] // 2))
        screen.blit(text, text_rect)
        pygame.display.update()
        overlay_music_in_loop(musicPath)
        time.sleep(5)