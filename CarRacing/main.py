import pygame
import random
import os

pygame.init()

class GameSys:
    def __init__(self):
        self.running = True
        self.screen = pygame.display.set_mode((700, 700))
        pygame.display.set_caption('Car Racing')
        self.background = Background('D:/CarRacing/Backgrounds/image.png', 0)
        self.car = Cars(350, 350, 1)

    def run(self):
        while self.running:
            self.screen.fill((255, 255, 255))
            self.background.draw(self.screen)
            self.car.draw(self.screen)
            pygame.display.update()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.car.rotate(-45)
                    elif event.key == pygame.K_d:
                        self.car.rotate(45)
                elif event.type == pygame.KEYUP:
                    # логіка стоп
                    if event.key == pygame.K_a or event.key == pygame.K_d:
                        pass
            
            # Keep the car moving
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:  # Move up
                self.car.move("up")
            if keys[pygame.K_s]:  # Move down
                self.car.move("down")
            if keys[pygame.K_a]:  # Move left
                self.car.move("left")
            if keys[pygame.K_d]:  # Move right
                self.car.move("right")

#class Menu:
    
class Background:
    def __init__(self, imagePath, animSpeed):
        self.image = pygame.image.load(imagePath)
        self.x = 0
        self.y = 0
        self.anim_speed = animSpeed

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

#class Score:

#class Roads:

#class Obstacles:

class Cars:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.angle = 0
        self.images = self.load_images("D:/CarRacing/Cars/Car1")
        self.current_image = self.get_image_for_angle(self.angle)

    def load_images(self, base_path):
        images = {
            (0, 45): [],
            (45, 90): [],
            (90, 180): [],
            (180, 270): [],
            (270, 360): []
        }

        for angle_range in images.keys():
            folder_name = f"{angle_range[0]} - {angle_range[1]}"
            folder_path = os.path.join(base_path, folder_name)

            if os.path.exists(folder_path):
                for file in os.listdir(folder_path):
                    if file.endswith(".png"):
                        images[angle_range].append(pygame.image.load(os.path.join(folder_path, file)))

        return images

    def get_image_for_angle(self, angle):
        """ Вибирає правильне зображення залежно від кута """
        for angle_range, imgs in self.images.items():
            if angle_range[0] <= angle < angle_range[1] and imgs:
                return random.choice(imgs) 
        return None  

    def rotate(self, angle):
        self.angle = (self.angle + angle) % 360
        self.current_image = self.get_image_for_angle(self.angle)

    def move(self, direction):
        if direction == "up":
            self.y -= self.speed
        elif direction == "down":
            self.y += self.speed
        elif direction == "left":
            self.x -= self.speed
        elif direction == "right":
            self.x += self.speed

    def draw(self, screen):
        if self.current_image:
            screen.blit(self.current_image, (self.x, self.y))

#class Bots:

game = GameSys()
game.run()
