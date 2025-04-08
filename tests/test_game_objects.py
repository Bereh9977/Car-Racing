import unittest
import pygame
from unittest.mock import Mock
from game_objects import Cars

class TestCarDraw(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.screen = Mock()

        # Створюємо фейкове зображення і зберігаємо його
        self.temp_image = pygame.Surface((50, 50))
        pygame.image.save(self.temp_image, "temp_car.png")

        self.car = Cars(
            x=100,
            y=100,
            speed=0,
            max_speed=10,
            angle=0,
            current_image="temp_car.png",
            controls={"up": pygame.K_w, "down": pygame.K_s, "left": pygame.K_a, "right": pygame.K_d}
        )

    def test_draw_without_ice(self):
        self.car.show_ice = False
        self.car.draw(self.screen)
        self.assertTrue(self.screen.blit.called)

    def test_draw_with_ice(self):
        self.car.show_ice = True
        self.car.ice_image = pygame.Surface((50, 50))
        self.car.ice_time = pygame.time.get_ticks() - 500 
        self.car.draw(self.screen)
        self.assertTrue(self.screen.blit.called)
        self.assertTrue(self.car.show_ice)

    def test_draw_ice_timeout(self):
        self.car.show_ice = True
        self.car.ice_image = pygame.Surface((50, 50))
        self.car.ice_time = pygame.time.get_ticks() - 1500  
        self.car.draw(self.screen)
        self.assertFalse(self.car.show_ice)

if __name__ == '__main__':
    unittest.main()