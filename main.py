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
        self.background = pygame.image.load('backgroundMenu.png')
        self.car = Cars(275, 460, 0)
        self.bot = Bots(215, 460, 0)
        self.menu = Menu(self.screen_width // 2 - 165, 350)
        self.roads = Roads('map2.png', 0)
        self.road_contour = pygame.image.load('map2_contour.png')
        self.road_contour_mask = pygame.mask.from_surface(self.road_contour)
        self.countdown_images = [
            pygame.image.load('3.png'),
            scale_image(pygame.image.load('2.png'), 2),
            pygame.image.load('1.png'),
            pygame.image.load('GO.png')
        ]
        self.in_menu = True  

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

    def run(self):
        if not self.menu.show(self.screen, self.background):
            self.running = False
            pygame.quit()
            return        
        self.countdown()

        while self.running:
            self.roads.draw(self.screen)
            self.car.draw(self.screen)
            self.bot.draw(self.screen)
            self.car.update_car()

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    
            if self.car.collide(self.road_contour_mask) is not None:
                self.car.bounce()
            
            self.bot.move()    
         
class Menu:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.imageStart = scale_image(self.load_image("startButton.png", (200, 80)), 1.5)
        self.imageOptions = scale_image(self.load_image("optionButton.png", (200, 80)), 1.5)
        self.start_rect = self.imageStart.get_rect(topleft=(x, y))
        self.options_rect = self.imageOptions.get_rect(topleft=(x, y + 150))

    def load_image(self, path, size):
        img = pygame.image.load(path)
        return pygame.transform.scale(img, size)

    def draw(self, screen):
        screen.blit(self.imageStart, self.start_rect.topleft)
        screen.blit(self.imageOptions, self.options_rect.topleft)

    def show_options_screen(self, screen):
        font = pygame.font.Font(None, 50)  # шрифт 50
        text = font.render("Options. press ESC, to back.", True, (255, 255, 255))

        in_options = True
        while in_options:
            screen.fill((0, 0, 0))  
            screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, screen.get_height() // 2))

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit() 
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    in_options = False  

    def show(self, screen, background):
        in_menu = True
        while in_menu:
            screen.blit(background, (0, 0))
            self.draw(screen)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False  

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.start_rect.collidepoint(event.pos):
                        in_menu = False  # Вихід із меню та початок гри
                    elif self.options_rect.collidepoint(event.pos):
                        self.show_options_screen(screen)  # Відкриваємо екран налаштувань
        return True  
    
class Background:
    def __init__(self, imagePath, animSpeed):
        self.image = pygame.image.load(imagePath)
        self.x = 0
        self.y = 0
        self.anim_speed = animSpeed

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

class Cars:
    def __init__(self, x, y, speed):
        self.angle = 0
        self.x = x  
        self.y = y  
        self.images = self.load_images("D:/CarRacing/")
        self.current_image = scale_image(random.choice(self.images), 0.5)
        self.rect = self.current_image.get_rect(center=(x, y))
        self.rotation_intensity = 4
        self.rotation_direction = 0
        self.speed = speed
        self.max_speed = 5
        self.acceleration = 0.1
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
        self.speed = -0.5 * self.speed
        
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
    def __init__(self, x, y, speed):
        super().__init__(x, y, speed)
        self.target_y = 400  # Цільова координата Y
        self.angle = 270
        self.current_point = 0
        # self.points = [(613, 983), (845, 983), (928, 945), (967, 841), 
        # (1045, 805), (1124, 769), (1160, 685), (1240, 648), (1299, 676), 
        # (1325, 731), (1361, 799), (1437, 818), (1494, 780), (1515, 694), 
        # (1506, 566), (1449, 518), (1248, 505), (1139, 489), (1096, 428), 
        # (1104, 248), (1104, 157), (1063, 108), (985, 100), (939, 138), 
        # (925, 192), (919, 346), (908, 431), (868, 477), (721, 480), (560, 477), 
        # (503, 517), (482, 585), (482, 711), (520, 759), (592, 774)]  # Список для кульок
        self.points = [(217, 261), (413, 139), (647, 228), (641, 582), (925, 647), 
        (1236, 555), (1182, 401), (948, 196), (1194, 96), (1478, 207), 
        (1534, 540), (1382, 922), (933, 925), (562, 914), (281, 882), 
        (235, 683), (211, 461)]  # Список для кульок  

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

if __name__ == "__main__":
    game = GameSys()
    game.run()