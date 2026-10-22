SCREEN_SIZE = (1920, 1080)
WINDOW_TITLE = 'Car Racing'
FPS = 500

FONT_PATH = "fonts/AveriaSansLibre-Bold.ttf"
WHITE = (255, 255, 255)
RED = (255, 0, 0)

MENU_BACKGROUND = 'img/garage_blur.png'
FINISH_IMAGE = 'img/finish.png'
COIN_IMAGE = "img/coin.png"

BUTTON_SOUND = "soundeffects/button_sound.mp3"
PURCHASE_SOUND = "soundeffects/purchase.mp3"

CAR_IMAGES = {
    'car1': 'img/car1.png',
    'car2': 'img/car2.png',
    'car3': 'img/car3.png',
    'car4': 'img/car4.png',
    'car5': 'img/car5.png',
}
DEFAULT_CAR_IMAGE = CAR_IMAGES['car5']

SCORE_FILE = "score.txt"
PURCHASED_CARS_FILE = "purchased_cars.txt"
PURCHASED_MAPS_FILE = "purchased_maps.txt"
RACE_POINTS_FILE = "race_points.json"

CHECKPOINT_COUNT = 8
GATE_MAX_TURN_DEG = 60
GATE_MAX_HALF_LENGTH = 200

CHECKPOINT_FIRST_POINTS = 100
CHECKPOINT_SECOND_POINTS = 50
LAP_WIN_POINTS = 200
CLEAN_LAP_BONUS = 300
WALL_HIT_PENALTY = 20
OBSTACLE_HIT_PENALTY = 50
WALL_HIT_COOLDOWN_MS = 500
STREAK_MULTIPLIERS = (1, 1.5, 2)
FLAWLESS_BONUS = 200
