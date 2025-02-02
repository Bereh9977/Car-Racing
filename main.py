import pygame
import random
import math

pygame.init()

class GameSys:
    def __init__(self):
        self.running = True
        self.screen_width = 700
        self.screen_height = 700
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('Car Racing')
        self.background = Background('backgroundMenu.png', 0) # D:/CarRacing/Background/backgroundMenu.png
        self.car = Cars(100, 350, 0)
        self.menu = Menu(self.screen_width // 2 - 100, 250)
        self.roads = Roads('map.png', 0) # D:/CarRacing/Maps/map.png

    def get_key_input(self):
        keys = pygame.key.get_pressed()
        rotation_direction = 0
        move_forward = False
            
        if keys[pygame.K_d]:
                rotation_direction = -1
        elif keys[pygame.K_a]:
                rotation_direction = 1
        
        if keys[pygame.K_w]:
            move_forward = True

        return rotation_direction, move_forward

    def run(self):
        while self.running:
            self.screen.fill((255, 255, 255)) # optimize
            self.background.draw(self.screen) # optimize
            # self.car.draw(self.screen)
            self.menu.draw(self.screen) # optimize
            self.roads.draw(self.screen) # Розкоментуй і зявиться карта і після цього нище напиши: self.car.draw(self.screen)
            self.car.draw(self.screen)
            pygame.display.update()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
            
            rotation_direction, move_forward = self.get_key_input()

            self.car.rotation_direction = rotation_direction
            self.car.rotate()
            if move_forward:
                self.car.drive_forward()

         
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
        self.images = self.load_images("D:/course2/SEM2/CICD/Cars/")
        self.current_image = random.choice(self.images)
        self.rect = self.current_image.get_rect(center=(x, y))
        self.rotation_intensity = 3
        self.rotation_direction = 0
        self.speed = speed
        self.max_speed = 3.3
        self.acceleration = 0.1
    
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
        self.drive()

    def drive(self):
        angle_value = math.radians(self.angle)
        vertical_shift = self.speed * math.cos(angle_value)
        horizontal_shift = self.speed * math.sin(angle_value)
        self.y -= vertical_shift 
        self.x -= horizontal_shift
        self.rect.center = (self.x, self.y)


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

if __name__ == "__main__":
    game = GameSys()
    game.run()
