import pytest
import math
from game_objects import Cars, Bots, Score, Finish, Obstacles
import pygame

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
    car.rect = pygame.Rect(0, 0, 3000, 3000)
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
# BEREH9977 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@pytest.fixture
def obstacles():
    pygame.init()
    return Obstacles("img/snowflake.png", "img/banana.png", "img/sand.png")

@pytest.mark.parametrize("map_choice, obstacle_list_name", [
    ("winter", "snowflake_rects"),
    ("beach", "banana_rects"),
    ("map3", "banana2_rects"),
])
def test_check_collision_with_removal(obstacles, map_choice, obstacle_list_name):
    # Отримуємо перешкоди для певної карти
    obstacle_rects = getattr(obstacles, obstacle_list_name)
    initial_len = len(obstacle_rects)

    # Перевіримо зіткнення — розміщуємо прямокутник поверх однієї з перешкод
    if initial_len > 0:
        test_rect = obstacle_rects[0].copy()
        collided = obstacles.check_collision_obstackles(test_rect, map_choice)
        assert collided is True, f"Має бути зіткнення з {map_choice}"
        assert len(getattr(obstacles, obstacle_list_name)) == initial_len - 1, "Перешкода повинна бути видалена"

def test_check_collision_sand(obstacles):
    map_choice = "map2"
    sand_rects = obstacles.sand_rects
    if sand_rects:
        test_rect = sand_rects[0].copy()
        collided = obstacles.check_collision_obstackles(test_rect, map_choice)
        assert collided is True, "Має бути зіткнення з піском"
        # Пісок не видаляється
        assert len(obstacles.sand_rects) == len(obstacles.sand_rand), "Пісок не повинен зникати після зіткнення"

def test_no_collision(obstacles):
    # Рект, який точно не перетинається з жодною перешкодою
    test_rect = pygame.Rect(0, 0, 10, 10)
    for map_choice in ["winter", "beach", "map2", "map3"]:
        result = obstacles.check_collision_obstackles(test_rect, map_choice)
        assert result is False, f"Не має бути зіткнення для {map_choice}"

@pytest.mark.parametrize("map_choice, expected_attrs", [
    ("winter", {"frozen": True, "show_ice": True}),
    ("beach", {"spinning": True}),
    ("map3", {"spinning": True}),
    ("map2", {"angle_changed": True}),  # спеціальна перевірка на зміну кута
])
def test_obstakles_feaches_behavior(mocker, map_choice, expected_attrs):
    # Ініціалізація Car
    car = Cars(0, 0, 0, 0, 0, 'img/car1.png', 'wasd')

    # Замінюємо music функцію
    mock_music = mocker.patch("game_objects.overlay_music_in_loop")

    # Замінюємо time
    mocker.patch("time.time", return_value=1000)
    mocker.patch("pygame.time.get_ticks", return_value=5000)

    # Мокаємо Obstacles
    obs = mocker.Mock()
    obs.check_collision_obstackles.return_value = True

    # Викликаємо метод
    car.obstakles_feaches(obs, map_choice)

    # Перевірка залежно від карти
    if map_choice == "winter":
        assert car.frozen is True
        assert car.freeze_time == 1000
        assert car.show_ice is True
        assert car.ice_time == 5000
        obs.show_snowflakes = False
        mock_music.assert_called_once_with("soundeffects/ice_sound.mp3")

    elif map_choice in ["beach", "map3"]:
        assert car.spinning is True
        assert car.spin_time == 1000
        mock_music.assert_called_once_with("soundeffects/spinning.mp3")

    elif map_choice == "map2":
        # Ініціалізуємо стан, щоб спрацювало додавання кута
        car.sand_turn_start = 999.0  # Менше ніж 1.5 сек тому
        car.angle = 0
        car.sand_turning = 1
        car.obstakles_feaches(obs, map_choice)
        assert car.angle == 0.9, "Кут повинен змінитися на 0.9 при sand_turning = 1"

@pytest.fixture
def score():
    # Створюємо об'єкт Score для тестів
    score = Score("img/coin.png", "winter")
    score.buy_prices = {'car': 100, 'map': 50}  # ціни для предметів
    score.current_score = 150  # балів достатньо для покупки
    score.car_file_path = "cars.txt"
    score.map_file_path = "maps.txt"
    return score

# Тест для успішної покупки
def test_purchase_item_success(score, mocker):
    # Мокаємо load_purchases і save_purchases
    mocker.patch.object(score, 'load_purchases', return_value=set())  # ще не куплені предмети
    mock_save_purchases = mocker.patch.object(score, 'save_purchases')

    result = score.purchase_item("car1", "car")
    assert result is True, "Покупка повинна бути успішною"
    mock_save_purchases.assert_called_once()  # Перевіряємо, що метод збереження викликано

# Тест для покупки при недостатньому рахунку
def test_purchase_item_not_enough_score(score, mocker):
    score.current_score = 40  # Бали не вистачають
    mocker.patch.object(score, 'load_purchases', return_value=set())
    mock_save_purchases = mocker.patch.object(score, 'save_purchases')

    result = score.purchase_item("car1", "car")
    assert result is False, "Покупка не повинна бути успішною через недостатній рахунок"

# Тест для покупки вже придбаного предмета
def test_purchase_item_already_purchased(score, mocker):
    mocker.patch.object(score, 'load_purchases', return_value={"car1"})  # Предмет вже куплений
    mock_save_purchases = mocker.patch.object(score, 'save_purchases')

    result = score.purchase_item("car1", "car")
    assert result is False, "Покупка не повинна бути успішною, якщо предмет вже куплений"

# Тест для неправильного типу предмета
def test_purchase_item_invalid_type(score, mocker):
    mocker.patch.object(score, 'load_purchases', return_value=set())
    result = score.purchase_item("car1", "invalid_type")  # Неправильний тип
    assert result is False, "Покупка не повинна бути успішною для неправильного типу предмета"

#KLYM !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

@pytest.fixture
def setup_car(tmp_path):
    pygame.init()

    # Створюємо тимчасовий шлях до зображення
    temp_image_path = tmp_path / "temp_car.png"
    temp_image = pygame.Surface((50, 50))
    pygame.image.save(temp_image, str(temp_image_path))

    car = Cars(
        x=100,
        y=100,
        speed=0,
        max_speed=10,
        angle=0,
        current_image=str(temp_image_path),
        controls={"up": pygame.K_w, "down": pygame.K_s, "left": pygame.K_a, "right": pygame.K_d}
    )

    screen = pygame.Surface((800, 600))  # Реальна поверхня замість мока
    return car, screen


def test_draw_without_ice(setup_car):
    car, screen = setup_car
    car.show_ice = False

    try:
        car.draw(screen)
    except Exception as e:
        pytest.fail(f"Метод draw() викликає помилку без льоду: {e}")


def test_draw_with_ice(setup_car):
    car, screen = setup_car
    car.show_ice = True
    car.ice_image = pygame.Surface((50, 50))
    car.ice_time = pygame.time.get_ticks() - 500

    try:
        car.draw(screen)
        assert car.show_ice, "Лід повинен бути показаний"
    except Exception as e:
        pytest.fail(f"Метод draw() викликає помилку при наявності льоду: {e}")


def test_draw_ice_timeout(setup_car):
    car, screen = setup_car
    car.show_ice = True
    car.ice_image = pygame.Surface((50, 50))
    car.ice_time = pygame.time.get_ticks() - 1500

    car.draw(screen)
    assert not car.show_ice, "show_ice повинен стати False після тайм-ауту"