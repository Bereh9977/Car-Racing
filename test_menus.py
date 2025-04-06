import pytest
from menus import CarsMenu

@pytest.fixture
def mock_screen(mocker):
    return mocker.Mock()

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