import json
import math
import os
import pygame
from settings import (CHECKPOINT_COUNT, GATE_MAX_TURN_DEG, GATE_MAX_HALF_LENGTH, CHECKPOINT_FIRST_POINTS,
                      CHECKPOINT_SECOND_POINTS, LAP_WIN_POINTS, WALL_HIT_PENALTY,
                      OBSTACLE_HIT_PENALTY, WALL_HIT_COOLDOWN_MS, STREAK_MULTIPLIERS, FLAWLESS_BONUS,
                      RACE_POINTS_FILE)


def normalize(vector):
    length = math.hypot(*vector)
    if length == 0:
        return None
    return vector[0] / length, vector[1] / length


def cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def segments_intersect(p1, p2, q1, q2):
    """
    Перевіряє, чи перетинаються відрізки p1-p2 та q1-q2.

    :return: True, якщо відрізки перетинаються.
    """
    r = (p2[0] - p1[0], p2[1] - p1[1])
    s = (q2[0] - q1[0], q2[1] - q1[1])
    denominator = cross(r, s)
    if denominator == 0:
        return False
    offset = (q1[0] - p1[0], q1[1] - p1[1])
    t = cross(offset, s) / denominator
    u = cross(offset, r) / denominator
    return 0 <= t <= 1 and 0 <= u <= 1


class Gate:
    """
    Клас Gate представляє контрольну точку — невидиму лінію поперек дороги.
    """
    def __init__(self, start, end, direction, route_index):
        """
        :param start: Перший кінець лінії (x, y).
        :param end: Другий кінець лінії (x, y).
        :param direction: Одиничний вектор напрямку руху по трасі.
        :param route_index: Індекс точки маршруту бота, на якій побудовано ворота.
        """
        self.start = start
        self.end = end
        self.direction = direction
        self.route_index = route_index

    def is_crossed(self, previous_position, position):
        """
        Перевіряє, чи перетнула машина ворота в правильному напрямку.

        :param previous_position: Позиція машини в попередньому кадрі.
        :param position: Поточна позиція машини.
        :return: True, якщо ворота перетнуто вперед.
        """
        movement = (position[0] - previous_position[0], position[1] - previous_position[1])
        moving_forward = movement[0] * self.direction[0] + movement[1] * self.direction[1] > 0
        return moving_forward and segments_intersect(previous_position, position, self.start, self.end)


def route_direction(route_points, index):
    """
    Обчислює напрямок траси в точці маршруту та кут повороту в ній.

    :param route_points: Список точок маршруту бота.
    :param index: Індекс точки.
    :return: (одиничний вектор напрямку, кут повороту в градусах) або (None, None).
    """
    previous_point, point, next_point = route_points[index - 1], route_points[index], route_points[index + 1]
    incoming = normalize((point[0] - previous_point[0], point[1] - previous_point[1]))
    outgoing = normalize((next_point[0] - point[0], next_point[1] - point[1]))
    if incoming is None or outgoing is None:
        return None, None
    turn = math.degrees(math.acos(max(-1.0, min(1.0, incoming[0] * outgoing[0] + incoming[1] * outgoing[1]))))
    direction = normalize((incoming[0] + outgoing[0], incoming[1] + outgoing[1]))
    return direction, turn


def march_to_edge(contour_mask, point, step, max_length):
    """
    Рухається від точки в заданому напрямку до першого пікселя краю дороги.

    :return: Остання точка дороги перед краєм або None, якщо край не знайдено.
    """
    width, height = contour_mask.get_size()
    last_free = point
    for distance in range(1, max_length + 1):
        x = round(point[0] + step[0] * distance)
        y = round(point[1] + step[1] * distance)
        if not (0 <= x < width and 0 <= y < height):
            return last_free
        if contour_mask.get_at((x, y)):
            return last_free
        last_free = (x, y)
    return None


def build_gate(route_points, index, contour_mask):
    """
    Будує ворота в точці маршруту, перпендикулярно до напрямку траси.

    :return: Об'єкт Gate або None, якщо в цій точці ворота побудувати не можна.
    """
    direction, turn = route_direction(route_points, index)
    if direction is None or turn > GATE_MAX_TURN_DEG:
        return None
    point = route_points[index]
    width, height = contour_mask.get_size()
    if not (0 <= point[0] < width and 0 <= point[1] < height) or contour_mask.get_at(point):
        return None
    normal = (-direction[1], direction[0])
    start = march_to_edge(contour_mask, point, normal, GATE_MAX_HALF_LENGTH)
    end = march_to_edge(contour_mask, point, (-normal[0], -normal[1]), GATE_MAX_HALF_LENGTH)
    if start is None or end is None:
        return None
    return Gate(start, end, direction, index)


def build_gates(route_points, contour_mask, overrides=None, count=CHECKPOINT_COUNT):
    """
    Автоматично розставляє ворота вздовж маршруту бота.

    Ворота розподіляються рівномірно, а точки з різким поворотом пропускаються.

    :param route_points: Список точок маршруту бота.
    :param contour_mask: Маска країв дороги.
    :param overrides: Словник {номер воріт: ((x1, y1), (x2, y2))} для ручного налаштування.
    :param count: Бажана кількість воріт.
    :return: Список об'єктів Gate у порядку проходження.
    """
    overrides = overrides or {}
    last_index = len(route_points) - 2
    if last_index < 1:
        return []

    gates = []
    used_index = 0
    for number in range(count):
        target = round((number + 1) * len(route_points) / (count + 1))
        candidates = sorted(range(used_index + 1, last_index + 1), key=lambda i: abs(i - target))
        for index in candidates:
            gate = build_gate(route_points, index, contour_mask)
            if gate is not None:
                gates.append(gate)
                used_index = index
                break

    for number, (start, end) in overrides.items():
        if number < len(gates):
            gates[number] = Gate(start, end, gates[number].direction, gates[number].route_index)
    return gates


class RacerStats:
    """Статистика одного учасника гонки."""
    def __init__(self, name):
        self.name = name
        self.total = 0
        self.streak = 0
        self.laps_won = 0
        self.lap_summaries = []
        self.reset_lap()

    def reset_lap(self):
        self.lap_start_total = self.total
        self.next_gate = 0
        self.checkpoint_points = 0
        self.wall_hits = 0
        self.obstacle_hits = 0
        self.previous_position = None
        self.touching_obstacle = False
        self.last_wall_hit = None


class RaceTracker:
    """
    Клас RaceTracker нараховує очки гонки (окремо від монет).

    Очки змінюються одразу під час гонки:
    - за контрольні точки нараховуються очки (першому більше, ніж другому);
    - за удари об стіни та перешкоди очки віднімаються (але не нижче 0);
    - за вигране коло нараховуються очки з множником за серію перемог;
    - за ідеальну гонку нараховується бонус.
    """
    def __init__(self, gates, racers, names):
        """
        :param gates: Список воріт (Gate).
        :param racers: Список учасників (машини або бот).
        :param names: Імена учасників для відображення.
        """
        self.gates = gates
        self.racers = list(racers)
        self.stats = [RacerStats(name) for name in names]
        self.new_lap()

    def new_lap(self):
        self.gate_claimed = [False] * len(self.gates)
        for stats in self.stats:
            stats.reset_lap()

    def stats_for(self, racer):
        for tracked, stats in zip(self.racers, self.stats):
            if tracked is racer:
                return stats
        return None

    def update(self):
        """Перевіряє проходження воріт і удари об перешкоди. Викликається щокадру."""
        for racer, stats in zip(self.racers, self.stats):
            position = (racer.x, racer.y)
            if stats.previous_position is not None and stats.next_gate < len(self.gates):
                if self.gates[stats.next_gate].is_crossed(stats.previous_position, position):
                    self.claim_gate(stats)
            stats.previous_position = position

            touching_obstacle = getattr(racer, 'touching_obstacle', False)
            if touching_obstacle and not stats.touching_obstacle:
                stats.obstacle_hits += 1
                self.apply_penalty(stats, OBSTACLE_HIT_PENALTY)
            stats.touching_obstacle = touching_obstacle

    def claim_gate(self, stats):
        gate_number = stats.next_gate
        if self.gate_claimed[gate_number]:
            points = CHECKPOINT_SECOND_POINTS
        else:
            points = CHECKPOINT_FIRST_POINTS
            self.gate_claimed[gate_number] = True
        stats.checkpoint_points += points
        stats.total += points
        stats.next_gate += 1

    @staticmethod
    def apply_penalty(stats, amount):
        stats.total = max(0, stats.total - amount)

    def register_wall_contact(self, racer, touching):
        """
        Враховує удар об стіну (повторні дотики протягом короткого часу не рахуються).

        :param racer: Машина, що торкнулася стіни.
        :param touching: True, якщо машина зараз торкається стіни.
        """
        stats = self.stats_for(racer)
        if stats is None or not touching:
            return
        now = pygame.time.get_ticks()
        if stats.last_wall_hit is None or now - stats.last_wall_hit >= WALL_HIT_COOLDOWN_MS:
            stats.wall_hits += 1
            self.apply_penalty(stats, WALL_HIT_PENALTY)
        stats.last_wall_hit = now

    def finish_lap(self, winner):
        """
        Нараховує очки за вигране коло з множником за серію перемог.
        Викликається, коли переможець кола перетнув фініш.

        Множник застосовується до зароблених за коло очок (контрольні точки та перемога),
        штрафи не множаться.

        :param winner: Учасник, що першим перетнув фініш.
        """
        for racer, stats in zip(self.racers, self.stats):
            if racer is winner:
                stats.streak += 1
                stats.laps_won += 1
                multiplier = STREAK_MULTIPLIERS[min(stats.streak, len(STREAK_MULTIPLIERS)) - 1]
                earned = stats.checkpoint_points + LAP_WIN_POINTS
                stats.total += round(earned * multiplier) - stats.checkpoint_points
            else:
                stats.streak = 0
            stats.lap_summaries.append(stats.total - stats.lap_start_total)
        self.new_lap()

    def finish_race(self, required_circles):
        """
        Нараховує бонус за ідеальну гонку (виграні всі кола, якщо кіл більше одного).

        :param required_circles: Кількість кіл у гонці.
        """
        for stats in self.stats:
            if required_circles > 1 and stats.laps_won == required_circles:
                stats.total += FLAWLESS_BONUS
                stats.lap_summaries.append(f"flawless +{FLAWLESS_BONUS}")

    def live_points(self, index):
        """Поточні очки гонки учасника (для відображення під час гонки)."""
        return self.stats[index].total

    def summary_lines(self):
        return [f"{stats.name}: {stats.total} race points" for stats in self.stats]


class RacePointsStore:
    """
    Зберігає загальну кількість очок гонки та найкращий результат для кожної карти.
    """
    def __init__(self, file_path=RACE_POINTS_FILE):
        self.file_path = file_path
        self.total = 0
        self.best = {}
        self.load()

    def load(self):
        if not os.path.exists(self.file_path):
            return
        try:
            with open(self.file_path, "r") as file:
                data = json.load(file)
            self.total = int(data.get("total", 0))
            self.best = {name: int(points) for name, points in data.get("best", {}).items()}
        except (ValueError, AttributeError, TypeError):
            self.total = 0
            self.best = {}

    def save(self):
        with open(self.file_path, "w") as file:
            json.dump({"total": self.total, "best": self.best}, file, indent=2)

    def add_result(self, map_choice, points):
        """
        Додає результат гонки та оновлює рекорд карти.

        :return: True, якщо це новий рекорд для карти.
        """
        self.total += points
        is_best = points > self.best.get(map_choice, -1)
        if is_best:
            self.best[map_choice] = points
        self.save()
        return is_best
