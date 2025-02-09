import pygame
import random
import math
import os
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

        current_directory = os.path.dirname(__file__)  # Визначення робочої області для шляхів, саме в межах репозиторію
        background_path = os.path.join(current_directory, 'img', 'backgroundMenu.png')
        self.background = pygame.image.load(background_path)

        self.car = Cars(275, 460, 0)
        self.bot = Bots(215, 460, 0)
        self.menu = Menu(self.screen_width // 2 - 165, 350)

        road_path = os.path.join(current_directory, 'img', 'map2.png')
        self.roads = Roads(road_path, 0)

        road_contour_path = os.path.join(current_directory, 'img', 'map2_contour.png')
        self.road_contour = pygame.image.load(road_contour_path)
        self.road_contour_mask = pygame.mask.from_surface(self.road_contour)

        self.countdown_images = [
            scale_image(pygame.image.load(os.path.join(current_directory, 'img', '3.png')), 0.5),
            scale_image(pygame.image.load(os.path.join(current_directory, 'img', '2.png')), 0.9),
            scale_image(pygame.image.load(os.path.join(current_directory, 'img', '1.png')), 0.4),
            pygame.image.load(os.path.join(current_directory, 'img', 'GO.png'))
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
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                    pygame.quit()
                    return
                    
            if self.car.collide(self.road_contour_mask) is not None:
                self.car.bounce()
            
            self.bot.move()    

class Menu:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        current_directory = os.path.dirname(__file__)  # Визначення робочої області для шляхів, саме в межах репозиторію
        self.imageStart = self.load_image(os.path.join(current_directory, 'img', 'startButton.png'))
        self.imageOptions = self.load_image(os.path.join(current_directory, 'img', 'optionButton.png'))

        self.start_rect = self.imageStart.get_rect(topleft=(x - 100, y))
        self.options_rect = self.imageOptions.get_rect(topleft=(x + 20, y + 150))

        self.selected_map = 0  # Змінна для вибору карти
        self.selected_car = 0  # Змінна для вибору машинки

        # Список доступних карт
        self.maps = ['Map1', 'Map2', 'Map3']
        # Список доступних машинок
        self.cars = ['Car1', 'Car2', 'Car3']

    def load_image(self, path):
        img = pygame.image.load(path)
        return img

    def draw(self, screen):
        screen.blit(self.imageStart, self.start_rect.topleft)
        screen.blit(self.imageOptions, self.options_rect.topleft)

    def show_options_screen(self, screen):
        font = pygame.font.Font(None, 50)
        text = font.render("Options. Press ESC to back.", True, (255, 255, 255))

        # Текст для вибору карти та машини
        map_text = font.render(f"Selected Map: {self.maps[self.selected_map]}", True, (255, 255, 255))
        car_text = font.render(f"Selected Car: {self.cars[self.selected_car]}", True, (255, 255, 255))

        in_options = True
        while in_options:
            screen.fill((0, 0, 0))  # Очищаємо екран
            screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, screen.get_height() // 10))

            # Відображення вибору карти та машини
            screen.blit(map_text, (screen.get_width() // 2 - map_text.get_width() // 2, screen.get_height() // 4))
            screen.blit(car_text, (screen.get_width() // 2 - car_text.get_width() // 2, screen.get_height() // 3))

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        in_options = False  # Вихід з опцій
                    elif event.key == pygame.K_UP:
                        self.selected_map = (self.selected_map - 1) % len(self.maps)  # Вибір попередньої карти
                    elif event.key == pygame.K_DOWN:
                        self.selected_map = (self.selected_map + 1) % len(self.maps)  # Вибір наступної карти
                    elif event.key == pygame.K_LEFT:
                        self.selected_car = (self.selected_car - 1) % len(self.cars)  # Вибір попередньої машини
                    elif event.key == pygame.K_RIGHT:
                        self.selected_car = (self.selected_car + 1) % len(self.cars)  # Вибір наступної машини

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
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()  
                        exit()

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.start_rect.collidepoint(event.pos):
                        in_menu = False
                    elif self.options_rect.collidepoint(event.pos):
                        self.show_options_screen(screen)  
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
        
        current_directory = os.path.dirname(__file__) # Визначення робочої області для шляхів, саме в межах репозиторію
        cars_directory = os.path.join(current_directory, 'img', 'cars') 
        
        self.images = self.load_images(cars_directory)
        self.current_image = scale_image(random.choice(self.images), 0.5)
        self.rect = self.current_image.get_rect(center=(x, y))
        self.rotation_intensity = 4
        self.rotation_direction = 0
        self.speed = speed
        self.max_speed = 5
        self.acceleration = 0.1
        self.max_backward_speed = -0.3
    
    def load_images(self, base_path):
        return [pygame.image.load(os.path.join(base_path, f"car{i}.png")) for i in range(1, 6)]
    
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
        car_mask = pygame.mask.from_surface(self.current_image)
        width, height = car_mask.get_size()
        offset = (int(self.rect.centerx + x - width // 2), int(self.rect.centery + y - height // 2))
        point_of_intersection = mask.overlap(car_mask, offset)
        return point_of_intersection

    def bounce(self):
        self.speed = -0.5 * self.speed
        
        if self.speed > 0:
            self.drive_backward()
        else:
            self.drive_forward()
    
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
        self.target_y = 400
        self.angle = 270
        self.current_point = 0
        self.points = [(217, 261), (413, 139), (647, 228), (641, 582), (925, 647), 
        (1236, 555), (1182, 401), (948, 196), (1194, 96), (1478, 207), 
        (1534, 540), (1382, 922), (933, 925), (562, 914), (281, 882), 
        (235, 683), (211, 461)] 

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
