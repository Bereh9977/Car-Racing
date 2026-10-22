import pytest
from game_clock import FixedTimestep


def run_frames(mocker, fps, seconds, step_rate=500, max_frame_time=0.1):
    timestep = FixedTimestep(step_rate, max_frame_time)
    timestep.clock = mocker.Mock(tick=mocker.Mock(return_value=1000 // fps))
    steps = 0
    for _ in range(fps * seconds):
        timestep.tick(fps)
        steps += sum(1 for _ in timestep.steps())
    return steps


@pytest.mark.parametrize("fps", [25, 50, 100, 125, 250, 500])
def test_same_number_of_steps_for_any_fps(mocker, fps):
    assert run_frames(mocker, fps, seconds=2) == 1000, "Кількість кроків симуляції не повинна залежати від FPS"


def test_long_frame_is_capped(mocker):
    timestep = FixedTimestep(500, 0.1)
    timestep.clock = mocker.Mock(tick=mocker.Mock(return_value=3000))
    timestep.tick(500)
    assert sum(1 for _ in timestep.steps()) == 50, "Довгий кадр має обмежуватися max_frame_time"


def test_reset_discards_accumulated_time(mocker):
    timestep = FixedTimestep(500, 0.1)
    timestep.clock = mocker.Mock(tick=mocker.Mock(return_value=50))
    timestep.tick(500)
    timestep.reset()
    assert sum(1 for _ in timestep.steps()) == 0, "Після reset накопичений час має обнулятися"


def test_leftover_time_carries_to_next_frame(mocker):
    timestep = FixedTimestep(500, 0.1)
    timestep.clock = mocker.Mock(tick=mocker.Mock(return_value=3))
    timestep.tick(500)
    assert sum(1 for _ in timestep.steps()) == 1
    timestep.tick(500)
    assert sum(1 for _ in timestep.steps()) == 2, "Залишок часу має переноситися на наступний кадр"
