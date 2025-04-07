import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from menus import MapsMenu, Menu


class TestMapsMenu(unittest.TestCase):
    def setUp(self):
        self.maps_menu = MapsMenu(0, 0, 0)
        self.maps_menu.state = None
        self.maps_menu.text = ['Map1', 'Map2']
        self.maps_menu.map_buttons = [MagicMock(), MagicMock()]
        self.maps_menu.map_buttons[0].collidepoint.return_value = False
        self.maps_menu.map_buttons[1].collidepoint.return_value = False

    def test_check_click_no_collision(self):
        pos = (0, 0)
        self.maps_menu.check_click(pos)
        self.assertNotIn(self.maps_menu.state, ['Map1', 'Map2'])

    def test_check_click_collision(self):
        pos = (100, 100)
        self.maps_menu.map_buttons[1].collidepoint.return_value = True
        self.maps_menu.check_click(pos)
        self.assertEqual(self.maps_menu.state, 'Map2')


class TestMenu(unittest.TestCase):
    def test_countdown(self):
        menu = Menu(0, 0)
        with patch('time.sleep', return_value=None): 
            with patch('pygame.font.Font') as MockFont:
                mock_font_instance = MagicMock()
                MockFont.return_value = mock_font_instance
                mock_font_instance.render.return_value = MagicMock()

                with patch('pygame.display.update'), \
                     patch('pygame.display.get_surface') as mock_get_surface:

                    mock_surface = MagicMock()
                    mock_get_surface.return_value = mock_surface

                    menu.countdown()

                    # 3 рази малює: 3, 2, 1
                    self.assertEqual(mock_font_instance.render.call_count, 3)


if __name__ == '__main__':
    unittest.main()
