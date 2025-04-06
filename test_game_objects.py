import pytest
import math
from game_objects import Cars, Bots

@pytest.mark.parametrize("speed, angle, initial_x, initial_y, expected_x, expected_y", 
[
    (0, 45, 752, 581, 752, 581),  # швидкість 0
    (2, 0, 314, 83, 314, 83 - 2),  # кут 0
    (1.3, 90, 512, 923, 512 + 1.3 * (-math.sin(math.radians(90))), 923),  # кут 90
    (0.8, 142, 35, 854, 35 + 0.8 * (-math.sin(math.radians(142))), 854 - 0.8 * math.cos(math.radians(142))),  # кут 142
])
def test_drive_forward_shift(speed, angle, initial_x, initial_y, expected_x, expected_y):
    car = Cars(speed=speed, angle=angle, x=initial_x, y=initial_y, 
               max_speed=200, current_image='img/car1.png', controls='wasd')
    car.drive_forward_shift()
    assert car.x == pytest.approx(expected_x, rel=1e-9)
    assert car.y == pytest.approx(expected_y, rel=1e-9)


@pytest.mark.parametrize("speed, angle, initial_x, initial_y, expected_x, expected_y", 
[
    (0, 45, 752, 581, 752, 581),  # швидкість 0
    (-2, 0, 314, 83, 314, 83 + 2),  # кут 0
    (-0.3, 90, 512, 923, 512 + 0.3 * math.sin(math.radians(90)), 923),  # кут 90
    (-0.4, 142, 35, 854, 35 + 0.4 * math.sin(math.radians(142)), 854 - 0.4 * (-math.cos(math.radians(142)))),  # кут 142
])
def test_drive_backward_shift(speed, angle, initial_x, initial_y, expected_x, expected_y):
    car = Cars(speed=speed, angle=angle, x=initial_x, y=initial_y, 
               max_speed=200, current_image='img/car1.png', controls='wasd')
    car.drive_backward_shift()
    assert car.x == pytest.approx(expected_x, rel=1e-9)
    assert car.y == pytest.approx(expected_y, rel=1e-9)



bot_points = [(1140, 925), (1368, 950), (1499, 884), (1556, 767), (1541, 560), (1565, 337), (1526, 216)]

@pytest.mark.parametrize("initial_x, initial_y, current_point, expected_point",
[
    (514, 420, len(bot_points), len(bot_points)), # поточна точка - остання, має бути без зміщення
    (1556, 767, 3, 4)                             # поточна точка з індексом 3, має бути зміщення - стати 4
])
def test_move(initial_x, initial_y, current_point, expected_point):
    bot = Bots(x=initial_x, y=initial_y, speed=0.5, max_speed=0.9, angle=79, points=bot_points)
    bot.current_point = current_point
    bot.move()
    assert bot.current_point == expected_point


@pytest.mark.parametrize("angle, expected_angle, points",
[
    (180, 180.8, [(100, 150), (170, 200)]), # поворот ліворуч: машинка напрямлена вниз; точка нижче, правіше відносно машинки
    (180, 179.2, [(100, 150), (70, 200)]),  # поворот праворуч: машинка напрямлена вниз; точка нижче, лівіше відносно машинки
    (0, 0.8, [(100, 150), (100, 200)]),     # поворот ліворуч: машинка напрямлена вгору; точка нижче машинки
    (270, 270.8, [(100, 150), (70, 50)]),   # поворот ліворуч: машинка напрямлена праворуч; точка вище, лівіше відносно машинки
    (270, 269.2, [(100, 150), (70, 250)])   # поворот праворуч: машинка напрямлена праворуч; точка нижче, лівіше відносно машинки
])
def test_calculate_angle(angle, expected_angle, points):
    bot = Bots(x=100, y=150, speed=0.5, max_speed=0.9, angle=angle, points=points)
    bot.current_point = 1
    bot.calculate_angle()
    assert bot.angle == expected_angle