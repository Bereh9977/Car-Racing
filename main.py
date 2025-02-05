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
        self.background = Background('backgroundMenu.png', 0) # D:/CarRacing/Background/backgroundMenu.png
        self.car = Cars(275, 460, 0) 
        self.bot = Bots(215, 460, 0)  
        self.menu = Menu(self.screen_width // 2 - 100, 250)
        self.roads = Roads('map2.png', 0) # D:/CarRacing/Maps/map.png
        self.road_contour = pygame.image.load('map2_contour.png')
        self.road_contour_mask = pygame.mask.from_surface(self.road_contour)
        self.countdown_images = [
            pygame.image.load('3.png'),
            scale_image(pygame.image.load('2.png'), 2),
            pygame.image.load('1.png'),
            pygame.image.load('GO.png')
        ]

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

        return rotation_direction

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
        self.background.draw(self.screen)
        self.menu.draw(self.screen)

        # Запускаємо зворотний відлік перед гонкою
        self.countdown()

        while self.running:
            self.roads.draw(self.screen)
            self.car.draw(self.screen)
            self.bot.draw(self.screen)
            self.update_car()

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    
            if self.car.collide(self.road_contour_mask) is not None:
                self.car.bounce()

    def update_car(self):
        drive_direction = self.get_drive_direction()
        rotation_direction = self.get_rotation_direction(drive_direction)        
        self.car.rotation_direction = rotation_direction
        self.car.rotate()
        moved = False

        if drive_direction == 'forward':
            moved = True
            self.car.drive_forward()
        elif drive_direction == 'backward':
            moved = True
            self.car.drive_backward()

        if not moved:
            if self.car.speed > 0:
                self.car.reduce_speed_forward()
            elif self.car.speed < 0:
                self.car.reduce_speed_backward()
            else:
                pass       
         
class Menu:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.imageStart = self.load_image("startButton.png", (200, 80)) # D:/CarRacing/ButtonsImages/startButton.png
        self.imageOptions = self.load_image("optionButton.png", (200, 80)) # D:/CarRacing/ButtonsImages/optionButton.png

        self.start_rect = self.imageStart.get_rect(topleft=(x, y))
        self.options_rect = self.imageOptions.get_rect(topleft=(x, y + 100))

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
        
        # car_mask = pygame.mask.from_surface(rotated_image)
        # width, height = car_mask.get_size()

        # for y in range(height):
        #     for x in range(width):
        #         if car_mask.get_at((x, y)):  # Якщо піксель перекривається з маскою (1)
        #     # Враховуємо обертання при розрахунку координат пікселів
        #             pos_x = self.rect.centerx + x - width // 2
        #             pos_y = self.rect.centery + y - height // 2
        #             pygame.draw.rect(screen, (255, 0, 0), (pos_x, pos_y, 1, 1))  # Червоний піксель
        #         else:
        #             pos_x = self.rect.centerx + x - width // 2
        #             pos_y = self.rect.centery + y - height // 2
        #             pygame.draw.rect(screen, (0, 0, 0), (pos_x, pos_y, 1, 1))

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

if __name__ == "__main__":
    game = GameSys()
    game.run()