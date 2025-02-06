import pygame
import random
import math
from utilities import scale_image

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
        self.menu = Menu(self.screen_width // 2 - 100, 250)
        self.roads = Roads('map2.png', 0) # D:/CarRacing/Maps/map.png
        self.road_contour = pygame.image.load('map2_contour.png')
        self.road_contour_mask = pygame.mask.from_surface(self.road_contour)
        self.finish_location = (125, 500)
        self.finish = Obstacles('finish.png', *self.finish_location)
        self.finish.image = scale_image(self.finish.image, 0.5)
        self.finish_mask = pygame.mask.from_surface(self.finish.image)

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

    def run(self):
        self.background.draw(self.screen)
        self.menu.draw(self.screen)
        while self.running:
            self.roads.draw(self.screen) # Розкоментуй і зявиться карта і після цього нище напиши: self.car.draw(self.screen)
            self.finish.draw(self.screen)
            self.car.draw(self.screen)
            self.update_car()
            pygame.display.update()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
            
            if self.car.collide(self.road_contour_mask) != None:
                self.car.bounce()


            finish_collision_point = self.car.collide(self.finish_mask, *self.finish_location)
            self.car.cross_finish(finish_collision_point)
            
        pygame.quit()

    

         
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
        self.prev_x = x
        self.prev_y = y
        self.images = self.load_images("D:/CarRacing/")
        self.current_image = random.choice(self.images)
        self.rect = self.current_image.get_rect(center=(x, y))
        self.rotation_intensity = 2.3
        self.rotation_direction = 0
        self.speed = speed
        self.max_speed = 5
        self.acceleration = 0.1
        self.max_backward_speed = -1
    
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
        car_mask = pygame.mask.from_surface(self.current_image)
        width, height = car_mask.get_size()
        offset = (int(self.rect.centerx - x - width // 2), int(self.rect.centery - y - height // 2))
        point_of_intersection = mask.overlap(car_mask, offset)
        return point_of_intersection

    def bounce(self):
        self.speed = -0.5 * self.speed
        if self.speed > 0:
            self.drive_backward()
        else:
            self.drive_forward()

    def cross_finish(self, finish_collision_point):
        if finish_collision_point == None:
            self.prev_x = self.x
            self.prev_y = self.y
        else:
            if finish_collision_point[1] == 0:
                self.x = self.prev_x
                self.y = self.prev_y
            else:
                print("finish")
        


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
    def __init__(self, imagePath, x, y):
        self.image = pygame.image.load(imagePath)
        self.x = x
        self.y = y

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

class Bots(Cars):
    def __init__(self, x, y, speed):
        super().__init__(x, y, speed)

if __name__ == "__main__":
    game = GameSys()
    game.run()
