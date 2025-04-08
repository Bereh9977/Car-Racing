import pytest
from main import GameSys
from pygame import Surface
import pygame

test_data_single = [
    (
        "winter", # map choice
        ("img/finish.png", 275, 230, 90, 0.308, "bottom"),  # Finish
        (1350, 250, 0, 0.75, 270, "img/finish.png", "wasd"),   # Cars
        (1350, 287, 0, 0.67, 270, [   # Bots
            (1654, 265), (1774, 309), (1822, 391), (1807, 657),
            (1721, 723), (1575, 681), (1539, 550), (1450, 468),
            (1317, 500), (1273, 607), (1197, 701), (1036, 739),
            (990, 815), (956, 929), (890, 990), (497, 1010),
            (184, 981), (138, 868), (139, 739), (162, 631),
            (225, 564), (384, 550), (637, 549), (727, 485),
            (739, 365), (644, 289), (268, 285)
        ]),
        ("img/coin.png", "winter")  # Score
    ),
    (
        "summer",
        ("img/finish.png", 183, 985, 142, 0.21, "bottom"),
        (1745, 945, 0, 0.5, 52, "img/finish.png", "wasd"),
        (1755, 925, 0, 0.48, 52, [
            (1491, 749), (1344, 634), (1243, 555), (1200, 474), (1236, 383),
            (1308, 282), (1376, 185), (1366, 109), (1293, 62), (1203, 92),
            (1106, 121), (1024, 90), (944, 110), (858, 163), (759, 132),
            (671, 144), (591, 228), (492, 381), (475, 475), (541, 545),
            (695, 643), (792, 598), (796, 505), (764, 401), (812, 328),
            (903, 332), (938, 378), (934, 446), (901, 525), (942, 606),
            (1064, 700), (1112, 768), (1102, 847), (1028, 898), (965, 875),
            (891, 816), (808, 757), (719, 740), (643, 809), (583, 881),
            (523, 918), (440, 909), (362, 887), (306, 917), (208, 1032)
        ]),
        ("img/coin.png", "summer")
    ),
    (
        "beach",
        ("img/finish.png", 1488, 993, 0, 0.308),
        (95, 990, 0, 0.75, 270, "img/finish.png", "wasd"),
        (95, 950, 0, 0.67, 270, [
            (336, 962), (489, 945), (547, 826), (490, 706), (329, 661),
            (268, 540), (347, 413), (619, 413), (709, 504), (714, 918),
            (767, 989), (901, 1005), (973, 921), (1005, 660), (1125, 596),
            (1248, 530), (1293, 407), (1428, 347), (1529, 414), (1566, 534),
            (1703, 602), (1808, 671), (1822, 767), (1780, 855), (1657, 894),
            (1575, 946), (1541, 1028)
        ]),
        ("img/coin.png", "beach")
    ),
    (
        "champions_field",
        ("img/finish.png", 292, 668, 0, 0.37, {"required_circles": 2}),
        (342, 730, 0, 0.99, 180, "img/finish.png", "wasd"),
        (372, 730, 0, 1, 180, [
            (376, 853), (458, 908), (557, 952), (706, 931),
            (861, 943), (1140, 925), (1368, 950), (1499, 884),
            (1556, 767), (1541, 560), (1565, 337), (1526, 216),
            (1413, 154), (1200, 158), (927, 136), (661, 154),
            (441, 162), (355, 282), (342, 428), (340, 700)
        ]),
        ("img/coin.png", "champions_field")
    ),
    (
        "map2",
        ("img/finish.png", 128, 400, 0, 0.5, {"required_circles": 2}),
        (200, 487, 0, 1.07, 180, "img/finish.png", "wasd"),
        (240, 487, 0, 0.95, 180, [
            (230, 770), (306, 907), (670, 943), (918, 882), (1214, 967),
            (1459, 852), (1557, 602), (1575, 330), (1460, 181), (1220, 81),
            (1097, 69), (986, 87), (911, 157), (921, 264), (1079, 326),
            (1207, 395), (1264, 512), (1230, 592), (1094, 651), (752, 636),
            (625, 538), (639, 338), (639, 175), (572, 110), (427, 119),
            (301, 168), (227, 242), (186, 419)
        ]),
        ("img/coin.png", "map2")
    ),
    (
        "map3",
        ("img/finish.png", 55, 278, 0, 0.53, {"required_circles": 2}),
        (160, 365, 0, 1.1, 180, "img/finish.png", "wasd"),
        (120, 365, 0, 0.95, 180, [
            (166, 629), (161, 861), (280, 970),
            (560, 845), (697, 674), (995, 685), (1225, 561),
            (1569, 519), (1742, 413), (1665, 242), (1362, 245),
            (943, 219), (686, 87), (401, 71), (184, 158), (98, 386)
        ]),
        ("img/coin.png", "map3")
    ),
]

test_data_doubles = [
    (
        "winter", # map choice
        ("img/finish.png", 275, 230, 90, 0.308, "bottom"),  # Finish
        (1350, 250, 0, 0.75, 270, 'img/car1.png', "wasd"), # Cars
        (1350, 287, 0, 0.75, 270, 'img/car2.png', 'arrows') # Cars
    ),
    (
        "summer",
        ("img/finish.png", 183, 985, 142, 0.21, "bottom"),
        (1745, 945, 0, 0.5, 52, 'img/car1.png', "wasd"),
        (1755, 925, 0, 0.5, 52, 'img/car2.png', 'arrows')
    ),
    (
        "beach",
        ("img/finish.png", 1488, 993, 0, 0.308),
        (95, 990, 0, 0.75, 270, 'img/car1.png', "wasd"),
        (95, 950, 0, 0.75, 270, 'img/car2.png', 'arrows')
    ),
    (
        "champions_field",
        ("img/finish.png", 292, 668, 0, 0.37, {"required_circles": 2}),
        (342, 730, 0, 0.95, 180, 'img/car1.png', "wasd"),
        (372, 730, 0, 0.95, 180, 'img/car2.png', 'arrows')
    ),
    (
        "map2",
        ("img/finish.png", 128, 400, 0, 0.5, {"required_circles": 2}),
        (200, 487, 0, 1.07, 180, 'img/car1.png', "wasd"),
        (240, 487, 0, 1.07, 180, 'img/car2.png', 'arrows')
    ),
    (
        "map3",
        ("img/finish.png", 55, 278, 0, 0.53, {"required_circles": 2}),
        (160, 365, 0, 1.1, 180, 'img/car1.png', "wasd"),
        (120, 365, 0, 1.1, 180, 'img/car2.png', 'arrows')
    ),
]

@pytest.mark.parametrize(
    "map_choice, finish_expected, car_expected, bot_expected, score_expected", 
    test_data_single
)
def test_create_objects_single(mocker, map_choice, finish_expected, car_expected, bot_expected, score_expected):
    MockFinish = mocker.patch('main.Finish')
    MockCars = mocker.patch('main.Cars')
    MockBots = mocker.patch('main.Bots')
    MockScore = mocker.patch('main.Score')
         
    game_sys = GameSys()
    game_sys.image = "img/finish.png" # ???
    game_sys.create_objects_single(map_choice)
        
    if finish_expected and isinstance(finish_expected[-1], dict):
        pos_args = finish_expected[:-1]
        kw_args = finish_expected[-1]
        MockFinish.assert_called_with(*pos_args, **kw_args)
    else:
        MockFinish.assert_called_with(*finish_expected)
        
    MockCars.assert_called_with(*car_expected)
    MockBots.assert_called_with(*bot_expected)
    MockScore.assert_called_with(*score_expected)

@pytest.mark.parametrize(
    "map_choice, finish_expected, car1_expected, car2_expected", 
    test_data_doubles
)
def test_create_objects_doubles(mocker, map_choice, finish_expected, car1_expected, car2_expected):
    MockFinish = mocker.patch('main.Finish')
    MockCars = mocker.patch('main.Cars')
         
    game_sys = GameSys()
    MockCars.reset_mock() # без скидання отримаємо об'єкти із конструктора GameSys (нам потрібні з методу)
    game_sys.image = "img/finish.png" # ???
    game_sys.create_objects_doubles(map_choice)
        
    if finish_expected and isinstance(finish_expected[-1], dict):
        pos_args = finish_expected[:-1]
        kw_args = finish_expected[-1]
        MockFinish.assert_called_with(*pos_args, **kw_args)
    else:
        MockFinish.assert_called_with(*finish_expected)
        
    expected_calls = [
    mocker.call(*car1_expected),
    mocker.call(*car2_expected)]
    assert MockCars.call_args_list == expected_calls

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