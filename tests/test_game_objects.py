import unittest
from unittest.mock import Mock, patch
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game_objects import Cars


class TestCarsDraw(unittest.TestCase):
    def test_draw_calls_pygame_functions(self):
        car = Cars(100, 150, (255, 0, 0), "img/car.png", 50, 70)

        mock_screen = Mock()

        with patch('game_objects.pygame.draw.rect') as mock_draw_rect:
            car.draw(mock_screen)

            mock_draw_rect.assert_called_once_with(mock_screen, car.color, car.rect)

            mock_screen.blit.assert_called_once_with(car.image, (car.x, car.y))


if __name__ == '__main__':
    unittest.main()
