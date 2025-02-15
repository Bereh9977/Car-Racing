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
        self.car = Cars(400, 997, 0, 0, 0, 'car1.png', 'wasd')
        self.bot = Bots(400, 992, 0, 0, 0, [])
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
        self.modes_page = ModesMenu(100, 100)
        self.choosing_map = False
        self.choosing_car = False
        self.choosing_mode = False
        self.map_choice = '0'
        self.mode_choice = '0'
        self.car1 = Cars(400, 997, 0, 0.5, 0, 'car1.png', 'wasd')
        self.car2 = Cars(500, 997, 0, 0.5, 0, 'car2.png', 'arrows')
        
    def run(self):
        self.show_menu()
        self.show_modes()
        if (self.running!= False):
            self.menu.countdown(self.countdown_images, self.screen, self.roads, self.car, self.car1, self.car2, self.bot, self.screen_width, self.screen_height, self.mode_choice)

        while self.running:
            self.roads.draw(self.screen)

            if self.mode_choice == 'single':
                self.car.draw(self.screen)
                self.car.update_car(self.obs, self.map_choice)
                self.bot.draw(self.screen)  # Малюємо бота

            else:
                self.car1.draw(self.screen)
                self.car1.update_car(self.obs, self.map_choice)
                self.car2.draw(self.screen)
                self.car2.update_car(self.obs, self.map_choice)

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

            cars = [self.car, self.car1, self.car2]

            for car in cars:
                if car.collide(self.road_contour_mask):
                    car.bounce()

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
                        self.choosing_mode = True
                        self.show_modes()


    def show_maps(self):
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
                        self.choose_maps(self.map_choice)

    def choose_maps(self, map_choice):
        print(f"Selected map: {map_choice}")
        self.roads = Roads(f"{map_choice}.jpg", 0)
        self.choosing_map = False
        if self.mode_choice == 'single':
            self.create_objects_single(map_choice)
        else:
            self.create_objects_doubles(map_choice)

    def show_cars(self):
        if self.mode_choice == 'doubles':
            self.choosing_car = False
            self.choosing_map = True
            self.show_maps()
        
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
        self.show_maps()       

    def show_modes(self):
        while self.choosing_mode:
            self.screen.blit(self.background, (0, 0))  
            self.modes_page.draw(self.screen)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.choosing_mode = False
                    pygame.quit()
                    return

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.mode_choice = self.modes_page.check_click(event.pos, self.mode_choice)
                    if self.mode_choice:
                        self.choose_modes()

    def choose_modes(self):
        print(f"Selected mode: {self.mode_choice}")
        self.choosing_mode = False
        self.choosing_car = True
        self.image = 'car1.png'
        self.show_cars()

    def create_objects_single(self, map_choice):
        if map_choice == 'winter':
            self.car = Cars(1350, 250, 0, 0.75, 270, self.image, 'wasd')
            self.bot = Bots(1350, 287, 0, 0.67, 270, [(1654, 265), (1774, 309), (1822, 391), (1807, 657), 
            (1721, 723), (1575, 681), (1539, 550), (1450, 468), (1317, 500), (1273, 607), (1197, 701), (1036, 739), 
            (990, 815), (956, 929), (890, 990), (497, 1010), (184, 981), (138, 868), (139, 739), (162, 631),
            (225, 564), (384, 550), (637, 549), (727, 485), (739, 365), (644, 289), (268, 285)])
            self.road_contour = pygame.image.load('winter_edge.png')                       
        elif map_choice == 'summer':
            self.car = Cars(1745, 945, 0, 0.5, 52, self.image, 'wasd')
            self.bot = Bots(1755, 925, 0, 0.48, 52, [(1491, 749), (1344, 634), (1243, 555), (1200, 474), (1236, 383), 
            (1308, 282), (1376, 185), (1366, 109), (1293, 62), (1203, 92), (1106, 121), (1024, 90), (944, 110), 
            (858, 163), (759, 132), (671, 144), (591, 228), (492, 381), (475, 475), (541, 545), (695, 643), 
            (792, 598), (796, 505), (764, 401), (812, 328), (903, 332), (938, 378), (934, 446), (901, 525), 
            (942, 606), (1064, 700), (1112, 768), (1102, 847), (1028, 898), (965, 875), (891, 816), (808, 757), 
            (719, 740), (643, 809), (583, 881), (523, 918), (440, 909), (362, 887), (306, 917), (208, 1032)])
            self.road_contour = pygame.image.load('summer_edge.png')
        elif map_choice == 'beach':
            self.car = Cars(95, 990, 0, 0.75, 270, self.image, 'wasd')
            self.bot = Bots(95, 950, 0, 0.67, 270, [(336, 962), (489, 945), (547, 826), (490, 706), (329, 661), 
            (268, 540), (347, 413), (619, 413), (709, 504), (714, 918), (767, 989), (901, 1005), (973, 921), 
            (1005, 660), (1125, 596), (1248, 530), (1293, 407), (1428, 347), (1529, 414), (1566, 534), 
            (1703, 602), (1808, 671), (1822, 767), (1780, 855), (1657, 894), (1575, 946), (1541, 1028)])
            self.road_contour = pygame.image.load('beach_edge.png')
        elif map_choice == 'champions_field':
            self.car = Cars(342, 730, 0, 0.85, 180, self.image, 'wasd')
            self.bot = Bots(372, 730, 0, 0.87, 180, [(376, 853), (458, 908), (557, 952), (706, 931), (861, 943), 
            (1140, 925), (1368, 950), (1499, 884), (1556, 767), (1541, 560), (1565, 337), (1526, 216), 
            (1413, 154), (1200, 158), (927, 136), (661, 154), (441, 162), (355, 282), (342, 428), (340, 700)])
            self.road_contour = pygame.image.load('champions_field_edge.png')
        elif map_choice == 'map2':
            self.car = Cars(200, 487, 0, 0.78, 180, self.image, 'wasd')
            self.bot = Bots(240, 487, 0, 0.68, 180, [(275, 808), (424, 880), (782, 899), (1061, 951), 
            (1296, 888), (1479, 715), (1518, 516), (1512, 264), (1352, 135), (1090, 126), 
            (954, 148), (898, 233), (972, 320), (1086, 375), (1217, 491), (1187, 601), (963, 650), 
            (654, 603), (664, 410), (658, 252), (522, 142), (340, 194), (276, 301), (239, 514)])
            self.road_contour = pygame.image.load('map2_contour.png')
        else:
            self.car = Cars(160, 365, 0, 0.84, 180, self.image, 'wasd')
            self.bot = Bots(120, 365, 0, 0.7, 180, [(166, 629), (161, 861), (280, 970), 
            (560, 845), (697, 674), (995, 685), (1225, 561), (1569, 519), (1742, 413), 
            (1665, 242), (1362, 245), (943, 219), (686, 87), (401, 71), (184, 158), (98, 386)])
            self.road_contour = pygame.image.load('map3_contour.png')        

        self.road_contour_mask = pygame.mask.from_surface(self.road_contour)


    def create_objects_doubles(self, map_choice):
        if map_choice == 'winter':
            self.car1 = Cars(1350, 250, 0, 0.75, 270, self.image, 'wasd')
            self.car2 = Cars(1350, 287, 0, 0.75, 270, self.image, 'arrows')
            self.road_contour = pygame.image.load('winter_edge.png')                       
        elif map_choice == 'summer':
            self.car1 = Cars(1745, 945, 0, 0.5, 52, self.image, 'wasd')
            self.car2 = Cars(1755, 925, 0, 0.5, 52, self.image, 'arrows')
            self.road_contour = pygame.image.load('summer_edge.png')
        elif map_choice == 'beach':
            self.car1 = Cars(95, 990, 0, 0.75, 270, self.image, 'wasd')
            self.car2 = Cars(95, 950, 0, 0.75, 270, self.image, 'arrows')
            self.road_contour = pygame.image.load('beach_edge.png')
        elif map_choice == 'champions_field':
            self.car1 = Cars(342, 650, 0, 0.85, 180, self.image, 'wasd')
            self.car2 = Cars(347, 650, 0, 0.85, 180, self.image, 'arrows')
            self.road_contour = pygame.image.load('champions_field_edge.png')
        elif map_choice == 'map2':
            self.car1 = Cars(200, 487, 0, 0.78, 180, self.image, 'wasd')
            self.car2 = Cars(240, 487, 0, 0.78, 180, self.image, 'arrows')
            self.road_contour = pygame.image.load('map2_contour.png')
        else:
            self.car1 = Cars(160, 365, 0, 0.84, 180, self.image, 'wasd')
            self.car2 = Cars(120, 365, 0, 0.84, 180, self.image, 'arrows')
            self.road_contour = pygame.image.load('map3_contour.png')        

        self.road_contour_mask = pygame.mask.from_surface(self.road_contour)

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

    def countdown(self, countdown_images, screen, roads, car, car1, car2, bot, screen_width, screen_height, mode_choice):
        for img in countdown_images:
            screen.fill((0, 0, 0))
            roads.draw(screen)

            if mode_choice == 'single':
                car.draw(screen)
                bot.draw(screen)

            else:
                car1.draw(screen)
                car2.draw(screen)

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
    def __init__(self, x, y, speed, max_speed, angle, current_image, controls):
        self.angle = angle
        self.x = x  
        self.y = y  
        self.image = self.load_image(f"D:/course2/SEM2/CICD/Cars/{current_image}")
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
        # Змінюємо offset, щоб врахувати позицію автомобіля
        car_mask = pygame.mask.from_surface(self.current_image)
        width, height = car_mask.get_size()
        offset = (int(self.rect.centerx - x - width // 2), int(self.rect.centery - y - height // 2))
        point_of_intersection = mask.overlap(car_mask, offset)
        return point_of_intersection

    def bounce(self):
        # Зміна швидкості на протилежну
            self.speed = -0.65 * self.speed

            if self.speed > 0:
                self.drive_backward()  # Відскок назад
            else:
                self.drive_forward()  # Відскок вперед

    def update_car(self, obs, map_choice):
        self.check_freeze()  # Перевіряємо, чи закінчився час заморозки
        self.check_spin()  # Перевіряємо, чи закінчилося обертання

        if self.frozen:
            return  # Блокуємо рух, поки машина заморожена

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
            elif map_choice == "beach" or "map3":
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
        self.banana2 = [(50, 954), (79, 737), (136, 497), (424, 50), 
                        (781, 165), (1240, 315), (1379, 173), (1547, 262), 
                        (1684, 456), (1345, 606), (1043, 563), (844, 665)]
        self.snowflakes_rand = random.sample(self.snowflakes, 4)
        self.banana_rand = random.sample(self.banana, 4)
        self.banana2_rand = random.sample(self.banana2, 4)
        self.snowflake_rects = [pygame.Rect(x, y, self.image.get_width(), self.image.get_height()) for x, y in self.snowflakes_rand]
        self.banana_rects = [pygame.Rect(x, y, self.image2.get_width(), self.image2.get_height()) for x, y in self.banana_rand]
        self.banana2_rects = [pygame.Rect(x, y, self.image2.get_width(), self.image2.get_height()) for x, y in self.banana2_rand]
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
        return False  # Якщо зіткнення не було

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

class ConfigurationMenu(ABC):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.font = pygame.font.Font("D:/course2/SEM2/CICD/Fonts/AveriaSansLibre-Bold.ttf", 36)
        self.title_font = pygame.font.Font("D:/course2/SEM2/CICD/Fonts/AveriaSansLibre-Bold.ttf", 56)
  
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
        
        self.image_map3 = self.load_image("map3_preview.png")
        self.image_map2 = self.load_image("map2_preview.png")
        self.image_beach = self.load_image("beach_preview.png")
        self.image_winter = self.load_image("winter_preview.png")
        self.image_summer = self.load_image("summer_preview.png")
        self.image_champions_field = self.load_image("champions_field_preview.png")
        
        self.map3_rect = self.image_map3.get_rect(topleft=(x, y + 130))
        self.map2_rect = self.image_map2.get_rect(topleft=(x, y + 550))
        self.beach_rect = self.image_beach.get_rect(topleft=(x + 600, y + 130))
        self.winter_rect = self.image_winter.get_rect(topleft=(x + 600, y + 550))
        self.summer_rect = self.image_summer.get_rect(topleft=(x + 1200, y + 130))
        self.champions_field_rect = self.image_champions_field.get_rect(topleft=(x + 1200, y + 550))

    def draw(self, screen):
        screen.blit(self.image_map3, self.map3_rect.topleft)
        screen.blit(self.image_map2, self.map2_rect.topleft)
        screen.blit(self.image_beach, self.beach_rect.topleft)
        screen.blit(self.image_winter, self.winter_rect.topleft)
        screen.blit(self.image_summer, self.summer_rect.topleft)
        screen.blit(self.image_champions_field, self.champions_field_rect.topleft)

        self.draw_text("Select a map:", self.beach_rect.centerx, self.y, screen, self.title_font)
        self.draw_text("Tidal Heatwave", self.map3_rect.centerx, self.map3_rect.top - 30, screen)
        self.draw_text("Meadow Rush", self.map2_rect.centerx, self.map2_rect.top - 30, screen)
        self.draw_text("Palm Paradise", self.beach_rect.centerx, self.beach_rect.top - 30, screen)
        self.draw_text("Frozen Tides", self.winter_rect.centerx, self.winter_rect.top - 30, screen)
        self.draw_text("Evergreen Escape", self.summer_rect.centerx, self.summer_rect.top - 30, screen)
        self.draw_text("Champions Field", self.champions_field_rect.centerx, self.champions_field_rect.top - 30, screen)

    def check_click(self, pos):
        if self.map3_rect.collidepoint(pos):
            return 'map3'
        elif self.map2_rect.collidepoint(pos):
            return 'map2'
        elif self.beach_rect.collidepoint(pos):
            return 'beach'
        elif self.winter_rect.collidepoint(pos):
            return 'winter'
        elif self.summer_rect.collidepoint(pos):
            return 'summer'
        elif self.champions_field_rect.collidepoint(pos):
            return 'champions_field'
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
    
class ModesMenu(ConfigurationMenu):
    def __init__(self, x, y):
        super().__init__(x, y)

        self.image_single = self.load_image("single.png")        
        self.image_doubles = self.load_image("doubles.png")

        self.single_rect = self.image_single.get_rect(topleft=(x - 70, y + 250))
        self.doubles_rect = self.image_doubles.get_rect(topleft=(x + 890, y + 250))

    def draw(self, screen):
        screen.blit(self.image_single, self.single_rect.topleft)
        screen.blit(self.image_doubles, self.doubles_rect.topleft)

        self.draw_text("Select the game mode:", self.x + 855, self.y + 50, screen, self.title_font)
        self.draw_text("Single", self.single_rect.centerx, self.single_rect.top - 30, screen)
        self.draw_text("Doubles", self.doubles_rect.centerx, self.doubles_rect.top - 30, screen)

    def check_click(self, pos, mode_choice):
        if self.single_rect.collidepoint(pos):
            mode_choice = 'single'
            return mode_choice
        elif self.doubles_rect.collidepoint(pos):
            mode_choice = 'doubles'
            return mode_choice
        
        return None

if __name__ == "__main__":
    game = GameSys()
    game.run()