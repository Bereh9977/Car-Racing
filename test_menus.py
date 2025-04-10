import pytest
from menus import CarsMenu, Menu, MapsMenu
import pygame

@pytest.fixture
def mock_screen(mocker):
    screen = mocker.Mock()
    screen.blit = mocker.Mock()
    return screen

@pytest.fixture
def mock_score(mocker):
    return mocker.Mock()

def test_draw_all_cars_purchased(mock_screen, mock_score):
    cars_menu = CarsMenu(x=230, y=724, score=mock_score)
    cars_menu.purchased_cars = ['car1', 'car2', 'car3']
    cars_menu.draw(mock_screen)
    
    mock_screen.blit.assert_any_call(cars_menu.image_car1, cars_menu.car1_rect.topleft)
    mock_screen.blit.assert_any_call(cars_menu.image_car2, cars_menu.car2_rect.topleft)
    mock_screen.blit.assert_any_call(cars_menu.image_car3, cars_menu.car3_rect.topleft)
    mock_screen.blit.assert_any_call(cars_menu.image_car4, cars_menu.car4_rect.topleft)
    mock_screen.blit.assert_any_call(cars_menu.image_car5, cars_menu.car5_rect.topleft)
    
def test_draw_no_cars_purchased(mock_screen, mock_score):
    cars_menu = CarsMenu(x=52, y=851, score=mock_score)
    cars_menu.purchased_cars = []
    cars_menu.draw(mock_screen)

    mock_screen.blit.assert_any_call(cars_menu.image_car1_lock, cars_menu.car1_rect.topleft)
    mock_screen.blit.assert_any_call(cars_menu.image_car2_lock, cars_menu.car2_rect.topleft)
    mock_screen.blit.assert_any_call(cars_menu.image_car3_lock, cars_menu.car3_rect.topleft)
    mock_screen.blit.assert_any_call(cars_menu.image_car4, cars_menu.car4_rect.topleft)
    mock_screen.blit.assert_any_call(cars_menu.image_car5, cars_menu.car5_rect.topleft)

    mock_screen.blit.assert_any_call(cars_menu.buy_image, cars_menu.buy_image_rect.topleft)
    mock_screen.blit.assert_any_call(cars_menu.buy_image, cars_menu.buy_image2_rect.topleft)
    mock_screen.blit.assert_any_call(cars_menu.buy_image, cars_menu.buy_image3_rect.topleft)

# BEREH9977 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@pytest.fixture
def menu_instance(mocker):
    mock_img = mocker.Mock()
    mock_rect = mocker.Mock()
    mock_rect.topleft = (100, 240)  # Імітуємо topleft для off_music_rect
    mock_rect.x = 100
    mock_rect.y = 240
    mock_rect.width = 287
    mock_rect.height = 103
    mock_img.get_rect.return_value = mock_rect
    mocker.patch("pygame.image.load", return_value=mock_img)
    mocker.patch("pygame.transform.scale", side_effect=lambda img, size: img)
    mocker.patch.object(Menu, "load_image", return_value=mock_img)
    menu = Menu(x=100, y=100)
    # Явно встановлюємо значення для тестування
    menu.slider_x = 100
    menu.slider_width = 288
    menu.knob_x = 244  # Початкове значення не впливає, але для консистентності
    return menu

@pytest.fixture
def mock_screen(mocker):
    """Фікстура для замокування екрану."""
    screen = mocker.Mock()
    screen.blit = mocker.Mock()
    screen.fill = mocker.Mock()
    return screen

@pytest.mark.parametrize(
    "mouse_x, expected_knob_x, expected_volume",
    [
        (100, 100, 0.0),  # Крайній лівий край повзунка
        (388, 388, 1.0),  # Крайній правий край повзунка
        (244, 244, 0.5),  # Середина повзунка
        (50, 100, 0.0),   # Позиція лівіше за повзунок (обмежується min)
        (400, 388, 1.0),  # Позиція правіше за повзунок (обмежується max)
    ],
)
def test_slider_position(menu_instance, monkeypatch, mock_screen, mocker, mouse_x, expected_knob_x, expected_volume):
    """
    Тестує позицію повзунка гучності та відповідне значення гучності при різних позиціях миші.
    
    :param mouse_x: Координата X миші.
    :param expected_knob_x: Очікувана позиція повзунка.
    :param expected_volume: Очікуване значення гучності (0.0 - 1.0).
    """
    # Замокування методів Pygame
    mock_rect = mocker.Mock()
    mock_rect.topleft = (835, 200)
    mock_rect.x = 835
    mock_rect.y = 200
    mock_text = mocker.Mock()
    mock_text.get_rect.return_value = mock_rect
    mock_font = mocker.Mock()
    mock_font.render.return_value = mock_text
    mocker.patch("pygame.font.Font", return_value=mock_font)
    mocker.patch("pygame.draw.rect")
    mocker.patch("pygame.draw.circle")
    mocker.patch("pygame.display.update")
    mocker.patch("pygame.mixer.music.set_volume")

    # Ініціалізуємо повзунок у стані перетягування
    menu_instance.dragging = True

    # Симулюємо подію руху миші та завершення циклу
    mock_motion_event = mocker.Mock(type=pygame.MOUSEMOTION, pos=(mouse_x, menu_instance.slider_y))
    mock_exit_event = mocker.Mock(type=pygame.MOUSEBUTTONDOWN, button=1, pos=menu_instance.back_rect.center)
    monkeypatch.setattr("pygame.event.get", lambda: [mock_motion_event, mock_exit_event])

    # Викликаємо метод show_options
    menu_instance.show_options(mock_screen, background=mocker.Mock())

    # Перевіряємо, чи правильно оновлено knob_x
    assert menu_instance.knob_x == expected_knob_x, f"Очікувалось knob_x={expected_knob_x}, отримано {menu_instance.knob_x}"

    # Перевіряємо, чи правильно оновлено volume
    assert abs(menu_instance.volume - expected_volume) < 0.01, f"Очікувалось volume={expected_volume}, отримано {menu_instance.volume}"
    
@pytest.fixture
def maps_menu(mock_score):
    menu = MapsMenu(x=100, y=100, score=mock_score)
    return menu

def test_draw_all_maps_purchased(mock_screen, maps_menu):
    maps_menu.purchased_maps = ['beach', 'winter', 'summer', 'champions_field']
    maps_menu.draw(mock_screen)
    
    # Перевіряємо, що кожна карта відображається
    mock_screen.blit.assert_any_call(maps_menu.image_map3, maps_menu.map3_rect.topleft)
    mock_screen.blit.assert_any_call(maps_menu.image_map2, maps_menu.map2_rect.topleft)
    mock_screen.blit.assert_any_call(maps_menu.image_beach, maps_menu.beach_rect.topleft)
    mock_screen.blit.assert_any_call(maps_menu.image_winter, maps_menu.winter_rect.topleft)
    mock_screen.blit.assert_any_call(maps_menu.image_summer, maps_menu.summer_rect.topleft)
    mock_screen.blit.assert_any_call(maps_menu.image_champions_field, maps_menu.champions_field_rect.topleft)

    # Перевірка, що зображення для покупки не відображаються
    assert maps_menu.buy_image not in mock_screen.blit.call_args_list

def test_draw_no_maps_purchased(mock_screen, maps_menu):
    maps_menu.purchased_maps = []
    maps_menu.draw(mock_screen)
    
    # Перевірка, що кожна карта відображається в заблокованому вигляді
    mock_screen.blit.assert_any_call(maps_menu.image_map3, maps_menu.map3_rect.topleft)
    mock_screen.blit.assert_any_call(maps_menu.image_map2, maps_menu.map2_rect.topleft)
    mock_screen.blit.assert_any_call(maps_menu.image_beach_lock, maps_menu.beach_rect.topleft)
    mock_screen.blit.assert_any_call(maps_menu.image_winter_lock, maps_menu.winter_rect.topleft)
    mock_screen.blit.assert_any_call(maps_menu.image_summer_lock, maps_menu.summer_rect.topleft)
    mock_screen.blit.assert_any_call(maps_menu.image_champions_field_lock, maps_menu.champions_field_rect.topleft)

    # Перевірка, що кнопки покупки відображаються
    mock_screen.blit.assert_any_call(maps_menu.buy_image, maps_menu.buy_image_rect.topleft)
    mock_screen.blit.assert_any_call(maps_menu.buy_image, maps_menu.buy_image_rect2.topleft)
    mock_screen.blit.assert_any_call(maps_menu.buy_image, maps_menu.buy_image_rect3.topleft)
    mock_screen.blit.assert_any_call(maps_menu.buy_image, maps_menu.buy_image_rect4.topleft)

#KLYM !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

@pytest.fixture
def fake_score():
    class FakeScore:
        def __init__(self):
            self.calls = []

        def purchase_item(self, item, item_type):
            self.calls.append((item, item_type))
            return True

    return FakeScore()

@pytest.fixture
def menu(fake_score):
    class FakeRect:
        def __init__(self, should_collide=False):
            self.should_collide = should_collide

        def collidepoint(self, pos):
            return self.should_collide

    m = MapsMenu(0, 0, fake_score)

    # Додаємо фейкові Rect-и
    m.buy_image_rect = FakeRect()
    m.buy_image_rect2 = FakeRect()
    m.buy_image_rect3 = FakeRect()
    m.buy_image_rect4 = FakeRect()
    m.map3_rect = FakeRect()
    m.map2_rect = FakeRect()
    m.beach_rect = FakeRect()
    m.winter_rect = FakeRect()
    m.summer_rect = FakeRect()
    m.champions_field_rect = FakeRect()

    m.save_purchased_maps_called = False

    def fake_save():
        m.save_purchased_maps_called = True

    m.save_purchased_maps = fake_save
    m.purchased_maps = {"beach", "winter", "summer", "champions_field"}

    return m

def test_click_on_beach_purchase(menu, monkeypatch):
    menu.buy_image_rect.should_collide = True

    music_called = {"called": False}

    def fake_music(path):
        music_called["called"] = True

    monkeypatch.setattr("menus.overlay_music_in_loop", fake_music)

    menu.check_click((100, 100))

    assert ("beach", "map") in menu.score.calls
    assert music_called["called"]
    assert "beach" in menu.purchased_maps
    assert menu.save_purchased_maps_called


def test_click_on_map2(menu):
    menu.map2_rect.should_collide = True
    result = menu.check_click((150, 150))
    assert result == "map2"


def test_click_on_locked_map(menu):
    menu.beach_rect.should_collide = True
    menu.purchased_maps.discard("beach")

    result = menu.check_click((200, 200))
    assert result is None


def test_click_on_purchased_map(menu):
    menu.beach_rect.should_collide = True
    menu.purchased_maps.add("beach")

    result = menu.check_click((300, 300))
    assert result == "beach"


@pytest.mark.parametrize("mode_choice", ["single", "doubles"])
def test_countdown_sleep_and_draw(monkeypatch, mode_choice):
    menu = Menu(0, 0)

    class FakeImage:
        def get_rect(self, **kwargs):
            return None

    countdown_images = [FakeImage() for _ in range(4)]

    fills = []
    road_calls = []
    car_calls = []
    sleeps = []
    music_called = {"called": False}

    class FakeScreen:
        def fill(self, color):
            fills.append(color)

        def blit(self, img, rect):
            pass

    class FakeRoads:
        def draw(self, screen):  # ← FIX
            road_calls.append(True)

    class FakeObj:
        def __init__(self, name):
            self.name = name

        def draw(self, screen):  # ← FIX тут
            car_calls.append(self.name)

    screen = FakeScreen()
    roads = FakeRoads()
    car = FakeObj("car")
    bot = FakeObj("bot")
    car1 = FakeObj("car1")
    car2 = FakeObj("car2")

    monkeypatch.setattr("menus.overlay_music_in_loop", lambda path: music_called.update({"called": True}))
    monkeypatch.setattr("menus.time.sleep", lambda x: sleeps.append(x))
    monkeypatch.setattr("menus.pygame.display.update", lambda: None)

    menu.countdown(
        countdown_images, screen, roads,
        car, car1, car2, bot,
        (800, 600), mode_choice
    )

    assert music_called["called"]
    assert len(sleeps) == 4
    assert all(s == 1 for s in sleeps)
    assert len(fills) == 4
    assert road_calls

    if mode_choice == "single":
        assert "car" in car_calls
        assert "bot" in car_calls
        assert "car1" not in car_calls
        assert "car2" not in car_calls
    else:
        assert "car1" in car_calls
        assert "car2" in car_calls
        assert "car" not in car_calls
        assert "bot" not in car_calls