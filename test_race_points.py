import pytest
import pygame
import race_points
from race_points import Gate, RaceTracker, RacePointsStore, build_gate, build_gates, segments_intersect
from game_objects import Finish


class FakeRacer:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.touching_obstacle = False


def corridor_mask(top=100, bottom=200, size=(400, 300)):
    """Маска з горизонтальною дорогою між стінами top та bottom."""
    mask = pygame.mask.Mask(size)
    for x in range(size[0]):
        mask.set_at((x, top))
        mask.set_at((x, bottom))
    return mask


def horizontal_gate(x=100):
    return Gate((x, 0), (x, 100), (1, 0), 0)


@pytest.mark.parametrize("p1, p2, q1, q2, expected", [
    ((0, 0), (10, 10), (0, 10), (10, 0), True),    # хрест
    ((0, 0), (10, 0), (0, 5), (10, 5), False),     # паралельні
    ((0, 0), (4, 4), (6, 0), (6, 10), False),      # не дотягує
    ((0, 0), (6, 0), (6, -5), (6, 5), True),       # торкається кінцем
])
def test_segments_intersect(p1, p2, q1, q2, expected):
    assert segments_intersect(p1, p2, q1, q2) is expected


def test_gate_counts_only_forward_crossing():
    gate = horizontal_gate()
    assert gate.is_crossed((99, 50), (101, 50)), "Перетин вперед має зараховуватися"
    assert not gate.is_crossed((101, 50), (99, 50)), "Перетин назад не має зараховуватися"
    assert not gate.is_crossed((90, 50), (95, 50)), "Рух без перетину не зараховується"


def test_build_gate_spans_road_between_walls():
    route = [(50, 150), (200, 150), (350, 150)]
    gate = build_gate(route, 1, corridor_mask())
    assert gate is not None
    ys = sorted([gate.start[1], gate.end[1]])
    assert ys == [101, 199], "Ворота мають тягнутися від стіни до стіни"
    assert gate.start[0] == gate.end[0] == 200, "Ворота мають бути перпендикулярні до дороги"
    assert gate.direction == pytest.approx((1, 0))


def test_build_gate_skips_sharp_turn():
    route = [(100, 150), (200, 150), (110, 160)]
    assert build_gate(route, 1, corridor_mask()) is None, "На різкому повороті ворота не будуються"


def test_build_gate_skips_point_without_walls():
    route = [(50, 400), (200, 400), (350, 400)]
    empty_mask = pygame.mask.Mask((400, 800))
    assert race_points.GATE_MAX_HALF_LENGTH < 400
    assert build_gate(route, 1, empty_mask) is None, "Без країв дороги в межах ліміту ворота не будуються"


def test_build_gates_are_ordered_and_override_applies():
    route = [(x, 150) for x in range(20, 400, 20)]
    gates = build_gates(route, corridor_mask(), overrides={0: ((5, 5), (6, 6))}, count=4)
    assert len(gates) == 4
    indexes = [gate.route_index for gate in gates]
    assert indexes == sorted(indexes) and len(set(indexes)) == 4, "Ворота мають іти по порядку маршруту"
    assert (gates[0].start, gates[0].end) == ((5, 5), (6, 6)), "Ручне налаштування має замінювати кінці воріт"


def make_tracker(gate_count=2):
    gates = [Gate((100 * (i + 1), 0), (100 * (i + 1), 100), (1, 0), i) for i in range(gate_count)]
    racers = [FakeRacer(50, 50), FakeRacer(50, 60)]
    return RaceTracker(gates, racers, ["A", "B"]), racers


def drive(tracker, racer, x):
    racer.x = x
    tracker.update()


def test_first_racer_gets_more_checkpoint_points():
    tracker, (a, b) = make_tracker()
    tracker.update()
    drive(tracker, a, 150)
    drive(tracker, b, 150)
    assert tracker.stats[0].checkpoint_points == race_points.CHECKPOINT_FIRST_POINTS
    assert tracker.stats[1].checkpoint_points == race_points.CHECKPOINT_SECOND_POINTS


def test_gates_must_be_passed_in_order():
    tracker, (a, _) = make_tracker()
    tracker.update()
    a.x = 250
    a.y = 50
    tracker.stats[0].previous_position = (190, 50)
    tracker.update()
    assert tracker.stats[0].next_gate == 0, "Ворота 2 не зараховуються до воріт 1"


def test_first_update_after_reset_does_not_count_teleport():
    tracker, (a, _) = make_tracker()
    a.x = 150
    tracker.update()
    assert tracker.stats[0].next_gate == 0, "Перший кадр лише запам'ятовує позицію"


def test_obstacle_hit_counted_once_per_contact():
    tracker, (a, _) = make_tracker()
    for touching in (True, True, True, False, True):
        a.touching_obstacle = touching
        tracker.update()
    assert tracker.stats[0].obstacle_hits == 2


def test_wall_hits_use_cooldown(mocker):
    tracker, (a, _) = make_tracker()
    ticks = mocker.patch("pygame.time.get_ticks")
    for now, touching in [(0, True), (100, True), (200, False), (300, True), (1000, True)]:
        ticks.return_value = now
        tracker.register_wall_contact(a, touching)
    assert tracker.stats[0].wall_hits == 2, "Удари в межах cooldown рахуються як один"


def test_unknown_racer_wall_contact_ignored():
    tracker, _ = make_tracker()
    tracker.register_wall_contact(FakeRacer(), True)
    assert all(stats.wall_hits == 0 for stats in tracker.stats)


def test_finish_lap_points_and_progress_scaling():
    tracker, (a, b) = make_tracker(gate_count=2)
    tracker.update()
    drive(tracker, a, 250)
    drive(tracker, a, 150)
    a.x = 150
    tracker.stats[0].previous_position = (90, 50)
    tracker.update()
    tracker.stats[0].previous_position = (190, 50)
    a.x = 210
    tracker.update()
    drive(tracker, b, 150)
    tracker.stats[0].wall_hits = 1
    tracker.finish_lap(a)

    first = race_points.CHECKPOINT_FIRST_POINTS
    second = race_points.CHECKPOINT_SECOND_POINTS
    clean = race_points.CLEAN_LAP_BONUS
    expected_a = 2 * first + (clean - race_points.WALL_HIT_PENALTY) + race_points.LAP_WIN_POINTS
    expected_b = second + round(clean * 0.5)
    assert tracker.stats[0].total == expected_a
    assert tracker.stats[1].total == expected_b, "Бонус за чисте коло переможеного залежить від прогресу"
    assert tracker.stats[0].total > tracker.stats[1].total


def test_clean_bonus_never_negative():
    tracker, (a, b) = make_tracker()
    tracker.stats[0].wall_hits = 1000
    tracker.finish_lap(a)
    assert tracker.stats[0].total == race_points.LAP_WIN_POINTS


def test_streak_multiplier_and_reset():
    tracker, (a, b) = make_tracker(gate_count=0)
    lap = race_points.CLEAN_LAP_BONUS + race_points.LAP_WIN_POINTS
    tracker.finish_lap(a)
    tracker.finish_lap(a)
    assert tracker.stats[0].lap_summaries == [lap, round(lap * race_points.STREAK_MULTIPLIERS[1])]
    tracker.finish_lap(b)
    assert tracker.stats[0].streak == 0
    tracker.finish_lap(a)
    assert tracker.stats[0].lap_summaries[-1] == lap, "Після програного кола серія починається спочатку"


def test_flawless_bonus_only_for_multi_lap_sweep():
    tracker, (a, b) = make_tracker(gate_count=0)
    tracker.finish_lap(a)
    tracker.finish_lap(a)
    before = tracker.stats[0].total
    tracker.finish_race(2)
    assert tracker.stats[0].total == before + race_points.FLAWLESS_BONUS
    assert tracker.stats[1].total == 0

    single_lap, (c, _) = make_tracker(gate_count=0)
    single_lap.finish_lap(c)
    before = single_lap.stats[0].total
    single_lap.finish_race(1)
    assert single_lap.stats[0].total == before, "Для однієї кола бонус не нараховується"


def test_store_saves_total_and_best(tmp_path):
    path = tmp_path / "race_points.json"
    store = RacePointsStore(str(path))
    assert store.add_result("winter", 900) is True
    assert store.add_result("winter", 500) is False
    reloaded = RacePointsStore(str(path))
    assert reloaded.total == 1400
    assert reloaded.best == {"winter": 900}


def test_store_handles_corrupt_file(tmp_path):
    path = tmp_path / "race_points.json"
    path.write_text("not json")
    store = RacePointsStore(str(path))
    assert store.total == 0 and store.best == {}


def test_finish_crossed_reports_lap_and_race(mocker):
    pygame.init()
    finish = Finish("img/finish.png", 0, 0, 0, 0.5, required_circles=1)
    finish.mask = mocker.Mock()
    car1, car2 = mocker.Mock(), mocker.Mock()
    car1.cross_finish.return_value = True
    tracker = mocker.Mock()
    tracker.summary_lines.return_value = ["You: 10 race points"]
    mocker.patch.object(finish, "display_circle_number")
    mocker.patch("game_objects.time.sleep")
    mocker.patch("game_objects.overlay_music_in_loop")

    assert finish.crossed(None, (1920, 1080), car1, car2, race_tracker=tracker) is False
    tracker.finish_lap.assert_called_once_with(car1)

    show_result = mocker.patch.object(finish, "show_result")
    assert finish.crossed(None, (1920, 1080), car1, car2, race_tracker=tracker) is True
    tracker.finish_race.assert_called_once_with(1)
    assert show_result.call_args[0][-1] == ["You: 10 race points"]
