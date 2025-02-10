import pygame
import random
import math
from utilities import scale_image
import time


pygame.init()

class GameSys:
    def __init__(self):
        self.running = True
        self.screen_width = 1920
        self.screen_height = 1080
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('Car Racing')
        self.background = pygame.image.load('summer_blur.png')
        self.car = Cars(400, 997, 0, 0)
        self.bot = Bots(400, 992, 0, 0)
        self.menu = Menu(800, 450)
        self.roads = Roads('winter.jpg', 0)
        self.road_contour = pygame.image.load('winter_edge.png')
        self.road_contour_mask = pygame.mask.from_surface(self.road_contour)
        self.countdown_images = [
            pygame.image.load('3.png'),
            scale_image(pygame.image.load('2.png'), 2),
            pygame.image.load('1.png'),
            pygame.image.load('GO.png')
        ]
        self.in_menu = True
        self.maps_page = MapsMenu(100, 100)
        self.choosing_map = False


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

    def run(self):
        self.show_menu()
        self.show_maps()
        self.countdown()
        # self.background.draw(self.screen)
        self.menu.draw(self.screen)
        self.maps_page.draw(self.screen)
        while self.running:
            self.roads.draw(self.screen)  # Розкоментуй і зявиться карта і після цього нище напиши: self.car.draw(self.screen)
            self.car.draw(self.screen)
            self.car.update_car()
            self.bot.draw(self.screen)  # Малюємо бота

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

    def countdown(self):
        for img in self.countdown_images:
            self.screen.fill((0, 0, 0))  
            self.roads.draw(self.screen)  
            self.car.draw(self.screen)  
            self.bot.draw(self.screen)  

            img_rect = img.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(img, img_rect)  

            pygame.display.update()  
            time.sleep(1) 

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

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Ліва кнопка миші
                    if self.menu.start_rect.collidepoint(event.pos):
                        self.in_menu = False  # Вихід з меню
                        self.choosing_map = True  # Вмикаємо вибір карти
                        self.show_maps()  # Переходимо до меню карт


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
                    map_choice = self.maps_page.check_click(event.pos)
                    if map_choice:
                        self.choose_maps(map_choice)

    def choose_maps(self, map_choice):
        print(f"Selected map: {map_choice}")
        self.roads = Roads(f"{map_choice}.jpg", 0)
        self.choosing_map = False
        if map_choice == 'winter':
            self.car = Cars(1350, 250, 0, 270)
            self.bot = Bots(1350, 287, 0, 270)
            self.road_contour = pygame.image.load('winter_edge.png')                       
        elif map_choice == 'summer':
            self.car = Cars(1745, 945, 0, 52)
            self.bot = Bots(1755, 925, 0, 52)
            self.road_contour = pygame.image.load('summer_edge.png')
        elif map_choice == 'beach':
            self.car = Cars(95, 990, 0, 270)
            self.bot = Bots(95, 950, 0, 270)
            self.road_contour = pygame.image.load('beach_edge.png')
        else:
            self.car = Cars(330, 730, 0, 0)
            self.bot = Bots(360, 730, 0, 0)
            self.road_contour = pygame.image.load('champions_field_edge.png')

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
    
class Background:
    def __init__(self, imagePath, animSpeed):
        self.image = pygame.image.load(imagePath)
        self.x = 0
        self.y = 0
        self.anim_speed = animSpeed

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

class Cars:
    def __init__(self, x, y, speed, angle):
        self.angle = angle
        self.x = x  
        self.y = y  
        self.images = self.load_images("D:/course2/SEM2/CICD/Cars/")
        self.current_image = scale_image(random.choice(self.images), 0.5)
        self.rect = self.current_image.get_rect(center=(x, y))
        self.rotation_intensity = 0.5
        self.rotation_direction = 0
        self.speed = speed
        self.max_speed = 0.5
        self.acceleration = 0.01
        self.max_backward_speed = -0.3
    
    def load_images(self, base_path):
        return [pygame.image.load(f"{base_path}car{i}.png") for i in range(1, 6)]
    
    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.current_image, self.angle)
        new_rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, new_rect.topleft)

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
    
    def update_car(self):
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
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Bots(Cars):
    def __init__(self, x, y, speed, angle):
        super().__init__(x, y, speed, angle)
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

class MapsMenu:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
        self.image_winter = self.load_image("winter.png", (400, 225))
        self.image_summer = self.load_image("summer.png", (400, 225))
        self.image_beach = self.load_image("beach.png", (400, 225))
        self.image_champions_field = self.load_image("champions_field.png", (400, 225))
        
        self.winter_rect = self.image_winter.get_rect(topleft=(x, y))
        self.summer_rect = self.image_summer.get_rect(topleft=(x + 600, y))
        self.beach_rect = self.image_beach.get_rect(topleft=(x, y + 400))
        self.champions_field_rect = self.image_champions_field.get_rect(topleft=(x + 600, y + 400))

    def load_image(self, path, size):
        img = pygame.image.load(path)
        return pygame.transform.scale(img, size)

    def draw(self, screen):
        screen.blit(self.image_winter, self.winter_rect.topleft)
        screen.blit(self.image_summer, self.summer_rect.topleft)
        screen.blit(self.image_beach, self.beach_rect.topleft)
        screen.blit(self.image_champions_field, self.champions_field_rect.topleft)

    def check_click(self, pos):
        if self.winter_rect.collidepoint(pos):
            return 'winter'
        elif self.summer_rect.collidepoint(pos):
            return 'summer'
        elif self.beach_rect.collidepoint(pos):
            return 'beach'
        elif self.champions_field_rect.collidepoint(pos):
            return 'champions_field'
        return None

if __name__ == "__main__":
    game = GameSys()
    game.run()