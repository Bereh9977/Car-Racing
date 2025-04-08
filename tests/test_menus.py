import pytest
from unittest.mock import Mock, patch, MagicMock
from menus import MapsMenu, Menu

@pytest.fixture
def menu():
    score_mock = Mock()
    score_mock.purchase_item.return_value = True

    # Створюємо екземпляр MapsMenu з мінімальними координатами
    m = MapsMenu(0, 0, score_mock)

    # Мокаємо Rect-и з collidepoint
    m.buy_image_rect = Mock()
    m.buy_image_rect2 = Mock()
    m.buy_image_rect3 = Mock()
    m.buy_image_rect4 = Mock()
    m.map3_rect = Mock()
    m.map2_rect = Mock()
    m.beach_rect = Mock()
    m.winter_rect = Mock()
    m.summer_rect = Mock()
    m.champions_field_rect = Mock()

    m.buy_image_rect.collidepoint.return_value = False
    m.buy_image_rect2.collidepoint.return_value = False
    m.buy_image_rect3.collidepoint.return_value = False
    m.buy_image_rect4.collidepoint.return_value = False
    m.map3_rect.collidepoint.return_value = False
    m.map2_rect.collidepoint.return_value = False
    m.beach_rect.collidepoint.return_value = False
    m.winter_rect.collidepoint.return_value = False
    m.summer_rect.collidepoint.return_value = False
    m.champions_field_rect.collidepoint.return_value = False

    m.score = score_mock
    m.save_purchased_maps = Mock()
    m.purchased_maps = set(["beach", "winter", "summer", "champions_field"])

    return m

@patch("menus.overlay_music_in_loop")
def test_click_on_beach_purchase(mock_music, menu):
    menu.buy_image_rect.collidepoint.return_value = True

    menu.check_click((100, 100))

    menu.score.purchase_item.assert_called_with("beach", "map")
    mock_music.assert_called_once()
    assert "beach" in menu.purchased_maps
    menu.save_purchased_maps.assert_called_once()

@patch("menus.overlay_music_in_loop")
def test_click_on_map2(mock_music, menu):
    menu.map2_rect.collidepoint.return_value = True

    result = menu.check_click((150, 150))
    assert result == "map2"

def test_click_on_locked_map(menu):
    menu.map3_rect.collidepoint.return_value = False
    menu.map2_rect.collidepoint.return_value = False

    menu.beach_rect.collidepoint.return_value = True
    menu.purchased_maps.discard("beach")

    result = menu.check_click((200, 200))
    assert result is None

def test_click_on_purchased_map(menu):
    menu.map3_rect.collidepoint.return_value = False
    menu.map2_rect.collidepoint.return_value = False

    menu.beach_rect.collidepoint.return_value = True
    menu.purchased_maps.add("beach")

    result = menu.check_click((300, 300))
    assert result == "beach"


@pytest.mark.parametrize("mode_choice", ["single", "doubles"])
def test_countdown_sleep_and_draw(mode_choice):
    menu = Menu(0, 0)

    countdown_images = [MagicMock() for _ in range(4)]  # 3, 2, 1, GO
    screen = MagicMock()
    roads = MagicMock()
    car = MagicMock()
    bot = MagicMock()
    car1 = MagicMock()
    car2 = MagicMock()
    aspect_ratio = (800, 600)

    with patch("menus.overlay_music_in_loop") as mock_music, \
         patch("menus.time.sleep") as mock_sleep, \
         patch("menus.pygame.display.update"):

        menu.countdown(
            countdown_images, screen, roads,
            car, car1, car2, bot,
            aspect_ratio, mode_choice
        )

        # Перевіряємо що музика запускалась
        mock_music.assert_called_once_with("soundeffects/321go.mp3")

        assert mock_sleep.call_count == 4
        mock_sleep.assert_called_with(1)

        # Перевірка що screen.fill викликано 4 рази
        assert screen.fill.call_count == 4
        roads.draw.assert_called()

        if mode_choice == 'single':
            car.draw.assert_called()
            bot.draw.assert_called()
            car1.draw.assert_not_called()
            car2.draw.assert_not_called()
        else:
            car1.draw.assert_called()
            car2.draw.assert_called()
            car.draw.assert_not_called()
            bot.draw.assert_not_called()
