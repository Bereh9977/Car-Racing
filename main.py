import pygame
import random
import math
from utilities import scale_image
import time
from abc import ABC, abstractmethod

pygame.init()

class GameSys:
    def __init__(self):
        self.running = True
        self.screen_width = 1920
        self.screen_height = 1080
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('Car Racing')
        self.background = pygame.image.load('garage_blur.png')
        # self.car = Cars(400, 997, 0, 0, 'car1.png')
        self.bot = Bots(400, 992, 0, 0)
        self.menu = Menu(800, 450)
        self.roads = Roads('winter.jpg', 0)
        self.obs = Obstacles(0, 0, 'snowflake.png','banana.png')
        self.road_contour = pygame.image.load('winter_edge.png')
        self.road_contour_mask = pygame.mask.from_surface(self.road_contour)
        self.countdown_images = [
            pygame.image.load('3.png'),
            scale_image(pygame.image.load('2.png'), 2),
            pygame.image.load('1.png'),
            pygame.image.load('GO.png')
        ]
        self.in_menu = True
        self.maps_page = MapsMenu(80, 100)
        self.cars_page = CarsMenu(90, 100)
        self.choosing_map = False
        self.choosing_car = False
        self.map_choice = '0'

    def run(self):
        self.show_menu()
        self.show_cars()
        if (self.running!= False):
            self.menu.countdown(self.countdown_images, self.screen, self.roads, self.car, self.bot, self.screen_width, self.screen_height)

        while self.running:
            self.roads.draw(self.screen)  # Розкоментуй і зявиться карта і після цього нище напиши: self.car.draw(self.screen)
            self.car.draw(self.screen)
            self.car.update_car(self.obs, self.map_choice)
            self.bot.draw(self.screen)  # Малюємо бота
            self.obs.draw_obstackles(self.screen, self.map_choice)

            # Малюємо кульки через метод draw_points у Bots
            # self.bot.draw_points(self.screen)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                # elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # Клік правою кнопкою миші
                #     mouse_x, mouse_y = event.pos
                #     self.bot.points.append((mouse_x, mouse_y))  # Додаємо точку до списку кульок
                #     # Збираємо координати кульок у одному рядку
                #     points_str = ", ".join([f"({x}, {y})" for x, y in self.bot.points])

            if self.car.collide(self.road_contour_mask) != None:
                self.car.bounce()

            self.bot.move()

        # print(points_str)
        pygame.quit()    

    def show_menu(self):
        while self.in_menu:
            self.screen.blit(self.background, (0, 0))  
            self.menu.draw(self.screen)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.in_menu = False
                    pygame.quit()
                    return

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.menu.start_rect.collidepoint(event.pos):
                        self.in_menu = False
                        self.choosing_car = True
                        self.show_cars()


    def show_maps(self, image):
        while self.choosing_map:
            self.screen.blit(self.background, (0, 0))  
            self.maps_page.draw(self.screen)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.choosing_map = False
                    pygame.quit()
                    return

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.map_choice = self.maps_page.check_click(event.pos)
                    if self.map_choice:
                        self.choose_maps(self.map_choice, image)

    def choose_maps(self, map_choice, image):
        print(f"Selected map: {map_choice}")
        self.roads = Roads(f"{map_choice}.jpg", 0)
        self.choosing_map = False
        if map_choice == 'winter':
            self.car = Cars(1350, 250, 0, 270, image)
            self.bot = Bots(1350, 287, 0, 270)
            self.road_contour = pygame.image.load('winter_edge.png')                       
        elif map_choice == 'summer':
            self.car = Cars(1745, 945, 0, 52, image)
            self.bot = Bots(1755, 925, 0, 52)
            self.road_contour = pygame.image.load('summer_edge.png')
        elif map_choice == 'beach':
            self.car = Cars(95, 990, 0, 270, image)
            self.bot = Bots(95, 950, 0, 270)
            self.road_contour = pygame.image.load('beach_edge.png')
        elif map_choice == 'champions_field':
            self.car = Cars(330, 730, 0, 0, image)
            self.bot = Bots(360, 730, 0, 0)
            self.road_contour = pygame.image.load('champions_field_edge.png')
        elif map_choice == 'map2':
            self.car = Cars(95, 990, 0, 270, image)
            self.bot = Bots(95, 950, 0, 270)
            self.road_contour = pygame.image.load('map2_contour.png')
        else:
            self.car = Cars(95, 990, 0, 270, image)
            self.bot = Bots(95, 950, 0, 270)
            self.road_contour = pygame.image.load('map3_contour.png')

        self.road_contour_mask = pygame.mask.from_surface(self.road_contour)

    def show_cars(self):
        while self.choosing_car:
            self.screen.blit(self.background, (0, 0))  
            self.cars_page.draw(self.screen)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.choosing_car = False
                    pygame.quit()
                    return

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    car_choice = self.cars_page.check_click(event.pos)
                    if car_choice:
                        self.choose_cars(car_choice)

    def choose_cars(self, car_choice):
        print(f"Selected car: {car_choice}")
        self.choosing_car = False
        if car_choice == 'car1':
            self.image = 'car1.png'
        elif car_choice == 'car2':
            self.image = 'car2.png'
        elif car_choice == 'car3':
            self.image = 'car3.png'
        elif car_choice == 'car4':
            self.image = 'car4.png'
        else:
            self.image = 'car5.png'

        self.choosing_map = True
        self.show_maps(self.image)
         
class Menu:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.imageStart = self.load_image("start.png", (289, 143))
        self.imageOptions = self.load_image("options.png", (289, 143))
        self.start_rect = self.imageStart.get_rect(topleft=(x, y))
        self.options_rect = self.imageOptions.get_rect(topleft=(x, y + 200))

    def load_image(self, path, size):
        img = pygame.image.load(path)
        return pygame.transform.scale(img, size)

    def draw(self, screen):
        screen.blit(self.imageStart, self.start_rect.topleft)
        screen.blit(self.imageOptions, self.options_rect.topleft)

    def countdown(self, countdown_images, screen, roads, car, bot, screen_width, screen_height):
        for img in countdown_images:
            screen.fill((0, 0, 0))
            roads.draw(screen)
            car.draw(screen)
            bot.draw(screen)

            img_rect = img.get_rect(center=(screen_width // 2, screen_height // 2))
            screen.blit(img, img_rect)

            pygame.display.update()
            time.sleep(1)      
    
class Background:
    def __init__(self, imagePath, animSpeed):
        self.image = pygame.image.load(imagePath)
        self.x = 0
        self.y = 0
        self.anim_speed = animSpeed

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

class Cars:
    def __init__(self, x, y, speed, angle, current_image):
        self.angle = angle
        self.x = x  
        self.y = y  
        self.image = self.load_image(f"D:/course2/SEM2/CICD/Cars/{current_image}")
        self.current_image = scale_image(self.image, 0.5)
        self.rect = self.current_image.get_rect(center=(x, y))
        self.rotation_intensity = 0.5
        self.rotation_direction = 0
        self.speed = speed
        self.max_speed = 0.5
        self.acceleration = 0.01
        self.max_backward_speed = -0.3
        self.freeze_time = 0  # Час, коли машина замерзла
        self.ice_image = pygame.image.load('ice-cube.png')  # Завантажуємо зображення льоду
        self.show_ice = False  # Флаг для показу льоду
        self.ice_time = 0  # Час початку показу льоду
        self.spinning = False  # Чи машина обертається
        self.spin_time = 0  # Час початку обертання
        self.spin_duration = 1  # Тривалість обертання (в секундах)
        self.spin_speed = 5  # Швидкість обертання (градусів за кадр)
        self.frozen = False
    
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
        if keys[pygame.K_w]:
            drive_direction = 'forward'
        elif keys[pygame.K_s]:
            drive_direction = 'backward'
        return drive_direction


    def get_rotation_direction(self):
        keys = pygame.key.get_pressed()
        rotation_direction = 0
        drive_direction = self.get_drive_direction()

        if (drive_direction == 'forward' or self.car.speed > 0):
            if keys[pygame.K_d]:
              rotation_direction = -1
            elif keys[pygame.K_a]:
              rotation_direction = 1
        
        elif (drive_direction == 'backward' or self.car.speed < 0):
            if keys[pygame.K_d]:
              rotation_direction = 1
            elif keys[pygame.K_a]:
              rotation_direction = -1

        return rotation_direction, drive_direction

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
        # Змінюємо offset, щоб врахувати позицію автомобіля
        car_mask = pygame.mask.from_surface(self.current_image)
        width, height = car_mask.get_size()
        offset = (int(self.rect.centerx + x - width // 2), int(self.rect.centery + y - height // 2))
        point_of_intersection = mask.overlap(car_mask, offset)
        return point_of_intersection

    def bounce(self):
        # Зміна швидкості на протилежну
            self.speed = -0.95 * self.speed

            if self.speed > 0:
                self.drive_backward()  # Відскок назад
            else:
                self.drive_forward()  # Відскок вперед

    def get_drive_direction(self):
        drive_direction = None
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            drive_direction = 'forward'
        elif keys[pygame.K_s]:
            drive_direction = 'backward'
        return drive_direction


    def get_rotation_direction(self, drive_direction):
        keys = pygame.key.get_pressed()
        rotation_direction = 0

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

        return rotation_direction
    
    def update_car(self, obs, map_choice):
        self.check_freeze()  # Перевіряємо, чи закінчився час заморозки
        self.check_spin()  # Перевіряємо, чи закінчилося обертання

        if self.spinning:
            self.angle += self.spin_speed  # Плавне обертання
            return 

        if obs.check_collision_obstackles(self.rect, map_choice):  # Якщо машина торкається об'єкта
            if map_choice == "winter":
                self.frozen = True
                self.freeze_time = time.time()
                self.show_ice = True  # Показати лід
                self.ice_time = pygame.time.get_ticks()  # Час початку накладання льоду
                obs.show_snowflakes = False
                return
            elif map_choice == "beach":
                self.spinning = True  # Почати обертання
                self.spin_time = time.time()  # Запам'ятати час початку
                return

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

class Score:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Roads:
    def __init__(self, imagePath, animSpeed):
        self.image = pygame.image.load(imagePath)
        self.x = 0
        self.y = 0
        self.anim_speed = animSpeed

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

class Obstacles:
    def __init__(self, x, y, imagePath, imagePath2):
        self.image = pygame.image.load(imagePath)
        self.image2 = pygame.image.load(imagePath2)
        self.snowflakes = [(539, 1025), (607, 577), (96, 780), (1588, 285), 
                           (1395, 434), (1269, 657), (1679, 746), (628, 244), 
                           (248, 1024), (1137, 708), (1821, 492), (360, 302)]  # Координати сніжинок
        self.banana = [(1069, 555), (850, 1019), (1262, 522), (1632, 599),
                        (1586, 854), (552, 851), (343, 919), (356, 659),
                        (216, 481), (275, 505), (661, 887), (1610, 913)]
        self.snowflakes_rand = random.sample(self.snowflakes, 4)
        self.banana_rand = random.sample(self.banana, 4)
        self.snowflake_rects = [pygame.Rect(x, y, self.image.get_width(), self.image.get_height()) for x, y in self.snowflakes_rand]
        self.banana_rects = [pygame.Rect(x, y, self.image.get_width(), self.image.get_height()) for x, y in self.banana_rand]
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
        return False  # Якщо зіткнення не було

class Bots(Cars):
    def __init__(self, x, y, speed, angle):
        available_cars = [
            "car1.png", "car2.png", "car3.png", "car4.png", "car5.png"
        ]
        current_image = random.choice(available_cars)

        super().__init__(x, y, speed, angle, current_image)

        self.target_y = 400  # Цільова координата Y
        self.current_point = 0
        self.points = [(613, 983), (845, 983), (928, 945), (967, 841), 
        (1045, 805), (1124, 769), (1160, 685), (1240, 648), (1299, 676), 
        (1325, 731), (1361, 799), (1437, 818), (1494, 780), (1515, 694), 
        (1506, 566), (1449, 518), (1248, 505), (1139, 489), (1096, 428), 
        (1104, 248), (1104, 157), (1063, 108), (985, 100), (939, 138), 
        (925, 192), (919, 346), (908, 431), (868, 477), (721, 480), (560, 477), 
        (503, 517), (482, 585), (482, 711), (520, 759), (592, 774)]  # Список для кульок

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
        super().drive_forward()    

class ConfigurationMenu(ABC):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.font = pygame.font.Font("D:/course2/SEM2/CICD/Fonts/AveriaSansLibre-Bold.ttf", 36)
        self.title_font = pygame.font.Font("D:/course2/SEM2/CICD/Fonts/AveriaSansLibre-Bold.ttf", 48)
  
    def load_image(self, path):
        return pygame.image.load(path)

    def draw_text(self, text, x, y, screen, font = None):
        if font is None:
            font = self.font
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(x, y))
        screen.blit(text_surface, text_rect)

    @abstractmethod
    def draw():
        pass

    @abstractmethod
    def check_click():
        pass         

class MapsMenu(ConfigurationMenu):
    def __init__(self, x, y):
        super().__init__(x, y)
        
        self.image_winter = self.load_image("winter_preview.png")
        self.image_summer = self.load_image("summer_preview.png")
        self.image_map2 = self.load_image("map2_preview.png")
        self.image_champions_field = self.load_image("champions_field_preview.png")
        self.image_beach = self.load_image("beach_preview.png")
        self.image_map3 = self.load_image("map3_preview.png")
        
        self.winter_rect = self.image_winter.get_rect(topleft=(x, y + 130))
        self.summer_rect = self.image_summer.get_rect(topleft=(x + 600, y + 130))
        self.map2_rect = self.image_map2.get_rect(topleft=(x, y + 550))
        self.champions_field_rect = self.image_champions_field.get_rect(topleft=(x + 600, y + 550))
        self.beach_rect = self.image_beach.get_rect(topleft=(x + 1200, y + 130))
        self.map3_rect = self.image_map3.get_rect(topleft=(x + 1200, y + 550))

    def draw(self, screen):
        screen.blit(self.image_winter, self.winter_rect.topleft)
        screen.blit(self.image_summer, self.summer_rect.topleft)
        screen.blit(self.image_beach, self.beach_rect.topleft)
        screen.blit(self.image_champions_field, self.champions_field_rect.topleft)
        screen.blit(self.image_map2, self.map2_rect.topleft)
        screen.blit(self.image_map3, self.map3_rect.topleft)

        self.draw_text("Select a map:", self.summer_rect.centerx, self.y, screen, self.title_font)
        self.draw_text("Frozen Tides", self.winter_rect.centerx, self.winter_rect.top - 30, screen)
        self.draw_text("Evergreen Escape", self.summer_rect.centerx, self.summer_rect.top - 30, screen)
        self.draw_text("Palm Paradise", self.beach_rect.centerx, self.beach_rect.top - 30, screen)
        self.draw_text("Champions Field", self.champions_field_rect.centerx, self.champions_field_rect.top - 30, screen)
        self.draw_text("Meadow Rush", self.map2_rect.centerx, self.map2_rect.top - 30, screen)
        self.draw_text("Tidal Heatwave", self.map3_rect.centerx, self.map3_rect.top - 30, screen)

    def check_click(self, pos):
        if self.winter_rect.collidepoint(pos):
            return 'winter'
        elif self.summer_rect.collidepoint(pos):
            return 'summer'
        elif self.beach_rect.collidepoint(pos):
            return 'beach'
        elif self.champions_field_rect.collidepoint(pos):
            return 'champions_field'
        elif self.map2_rect.collidepoint(pos):
            return 'map2'
        elif self.map3_rect.collidepoint(pos):
            return 'map3'
        return None

class CarsMenu(ConfigurationMenu):
    def __init__(self, x, y):
        super().__init__(x, y)
        
        self.image_car1 = self.load_image("car1_preview.png")
        self.image_car2 = self.load_image("car2_preview.png")
        self.image_car3 = self.load_image("car3_preview.png")
        self.image_car4 = self.load_image("car4_preview.png")
        self.image_car5 = self.load_image("car5_preview.png")
        
        self.car1_rect = self.image_car1.get_rect(topleft=(x, y + 100))
        self.car2_rect = self.image_car2.get_rect(topleft=(x + 600, y + 100))
        self.car3_rect = self.image_car3.get_rect(topleft=(x + 300, y + 550))
        self.car4_rect = self.image_car4.get_rect(topleft=(x + 900, y + 550))
        self.car5_rect = self.image_car5.get_rect(topleft=(x + 1200, y + 100))

    def draw(self, screen):
        screen.blit(self.image_car1, self.car1_rect.topleft)
        screen.blit(self.image_car2, self.car2_rect.topleft)
        screen.blit(self.image_car3, self.car3_rect.topleft)
        screen.blit(self.image_car4, self.car4_rect.topleft)
        screen.blit(self.image_car5, self.car5_rect.topleft)

        self.draw_text("Select a car:", self.car2_rect.centerx, self.y - 10, screen, self.title_font)
        self.draw_text("Ferrari 458 Challenge", self.car1_rect.centerx, self.car1_rect.top - 30, screen)
        self.draw_text("Mclaren P1 Sports", self.car2_rect.centerx, self.car2_rect.top - 30, screen)
        self.draw_text("Ford Mustang Shelby", self.car3_rect.centerx, self.car3_rect.top - 30, screen)
        self.draw_text("Subaru Impreza WRX STI", self.car4_rect.centerx, self.car4_rect.top - 30, screen)
        self.draw_text("Dodge Viper GTS", self.car5_rect.centerx, self.car5_rect.top - 30, screen)

    def check_click(self, pos):
        if self.car1_rect.collidepoint(pos):
            return 'car1'
        elif self.car2_rect.collidepoint(pos):
            return 'car2'
        elif self.car3_rect.collidepoint(pos):
            return 'car3'
        elif self.car4_rect.collidepoint(pos):
            return 'car4'
        elif self.car5_rect.collidepoint(pos):
            return 'car5'
        return None

if __name__ == "__main__":
    game = GameSys()
    game.run()