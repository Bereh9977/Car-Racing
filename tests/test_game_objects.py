import pytest
import pygame
from pygame import Rect
from game_objects import Cars, Score, Finish

@pytest.fixture
def score():
    return Score("img/coin.png", "winter")

@pytest.fixture
def finish():
    finish = Finish('img/finish.png', 275, 230, 90, 0.308, "bottom")
    finish.mask = pygame.mask.from_surface(finish.image)
    return finish

@pytest.fixture
def car():
    pygame.init()
    return Cars(0, 0, 0, 0, 0, 'img/car1.png', 'wasd')

@pytest.fixture
def screen():
    return pygame.Surface((1920, 1080))


# Тест для Car.collide
def test_car_collide(car):
    car2 = Cars(0, 0, 0, 0, 0, 'img/car1.png', 'wasd')  # Перетин
    car2_mask = pygame.mask.from_surface(car2.current_image)
    
    assert car.collide(car2_mask) is not None
    assert car.collide(car2_mask, 100, 100) is None

# Тест для Cars.bounce
def test_bounce(car):
    car.speed = 5.0
    car.bounce()
    assert car.speed == pytest.approx(-3.25, rel=0.01), "Швидкість повинна змінити знак і зменшитись у -0.65 разів"

# Тест для Cars.cross_finish
def test_cross_finish(car, finish):
    collision_point = (10, 5)  # Коректне перетинання знизу
    result = car.cross_finish(collision_point, finish.required_side)
    assert result is True, "Повинен повернути True при коректному перетині знизу"

# Тест для Score.check_collision
def test_score_check_collision(mocker, car, score):
    mock_music = mocker.patch("game_objects.overlay_music_in_loop", autospec=True)
    # Використовуємо координати першої монети для "winter": (515, 286)
    car.rect = Rect(0, 0, 3000, 3000)
    score.current_score = 0
    result = score.check_collision(car.rect)
    assert result is True, "Повинен повернути True при зіткненні з монетою"
    assert score.current_score == 100, "Очки повинні додатися"
    mock_music.assert_called_once_with("soundeffects/coin_collect.mp3")

# Тест для Finish.crossed
@pytest.mark.parametrize("car1_wins, car2_wins, expected", [
    (2, 1, True),   # Car1 перемагає
    (1, 2, True),   # Car2 перемагає
    (0, 0, False),  # Гонка не завершена
])
def test_finish_crossed(mocker, finish, screen, car1_wins, car2_wins, expected):
    car1 = mocker.Mock(spec=Cars)
    car2 = mocker.Mock(spec=Cars)
    finish.car1_wins = car1_wins
    finish.car2_wins = car2_wins
    finish.required_circles = car1_wins + car2_wins if expected else 3
    car1.collide = mocker.Mock(return_value=None)
    car2.collide = mocker.Mock(return_value=None)
    car1.cross_finish = mocker.Mock(return_value=False)
    car2.cross_finish = mocker.Mock(return_value=False)
    mocker.patch('time.sleep')  # Mock time.sleep
    mocker.patch.object(finish, 'show_result'), mocker.patch.object(finish, 'credit_prize')
    result = finish.crossed(screen, (1920, 1080), car1, car2)
    assert result == expected, f"Очікувалось {expected} для {car1_wins} перемог Car1 і {car2_wins} перемог Car2"


if __name__ == "__main__":
    pytest.main(["-v"])