# test_main.py
import pytest
import pygame
from pygame import Surface
from main import GameSys  # Імпорт класу GameSys з main.py

@pytest.fixture
def game_sys(mocker):
    pygame.init()
    game = GameSys()
    game.screen = Surface((1920, 1080))  # Додаємо screen
    game.background = Surface((1920, 1080))  # Додаємо background
    game.menu = mocker.Mock()
    game.menu.menu_back_rect = pygame.Rect(350, 450, 100, 50)
    game.menu.imageOptions = Surface((100, 50))
    game.menu.menu_back_bnt = Surface((100, 50))
    game.running = True  # Ініціалізуємо running
    return game

def test_handle_pause_continue_game(mocker, game_sys):
    # Мокуємо pygame.event.get і pygame.display.flip через mocker
    mock_event_get = mocker.patch('pygame.event.get')
    mock_event_get.side_effect = [[mocker.Mock(type=pygame.KEYDOWN, key=pygame.K_ESCAPE)], []]
    mocker.patch('pygame.display.flip')

    result = game_sys.handle_pause()
    assert result is True, "Гра повинна продовжитись при натисканні ESC"

def test_handle_pause_exit_to_menu(mocker, game_sys):
    # Мокуємо pygame.event.get і pygame.display.flip через mocker
    mock_event_get = mocker.patch('pygame.event.get')
    mock_event_get.side_effect = [[mocker.Mock(type=pygame.MOUSEBUTTONDOWN, button=1, pos=(375, 475))], []]
    mocker.patch('pygame.display.flip')

    result = game_sys.handle_pause()
    assert result is False, "Гра повинна повернути False при виході в головне меню"

def test_handle_pause_quit_game(mocker, game_sys):
    # Мокуємо pygame.event.get, pygame.display.flip і builtins.quit через mocker
    mock_event_get = mocker.patch('pygame.event.get')
    mock_event_get.side_effect = [[mocker.Mock(type=pygame.QUIT)], []]
    mocker.patch('pygame.display.flip')
    mocker.patch('builtins.quit')

    result = game_sys.handle_pause()
    assert result is False, "Гра повинна повернути False при закритті"
    assert game_sys.running is False, "Прапорець running має бути False"

if __name__ == "__main__":
    pytest.main(["-v"])