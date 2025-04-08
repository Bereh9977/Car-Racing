import sys
import os
import pytest
import itertools
from unittest.mock import patch, call
import threading
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import music 


@pytest.fixture(autouse=True)
def reset_globals():
    music.soundtracks = []
    music.current_track_index = 0
    yield
    music.soundtracks = []
    music.current_track_index = 0

def test_upload_soundtracks_fills_list():
    result = music.upload_soundtracks()
    assert isinstance(result, list)
    assert len(result) == 14
    assert result[0] == "music/track1.mp3"
    assert result[-1] == "music/track14.mp3"

def test_upload_soundtracks_does_not_duplicate():
    music.soundtracks = ["existing_track.mp3"]
    result = music.upload_soundtracks()
    assert result == ["existing_track.mp3"]  

@patch("pygame.mixer.music")
def test_next_track_switches_track(mock_music):
    # Готуємо звук
    music.soundtracks = [f"track{i}.mp3" for i in range(1, 4)] 
    music.current_track_index = 0
    music.music_playing.set()

    music.next_track()

    assert music.current_track_index == 1
    mock_music.stop.assert_called_once()
    mock_music.load.assert_called_once_with("track2.mp3")
    mock_music.play.assert_called_once_with(1)

@patch("pygame.mixer.music")
def test_next_track_does_nothing_if_music_paused(mock_music):
    music.music_playing.clear()  
    music.soundtracks = ["track1.mp3", "track2.mp3"]
    music.current_track_index = 0

    music.next_track()

    assert music.current_track_index == 0
    mock_music.stop.assert_not_called()
    mock_music.load.assert_not_called()
    mock_music.play.assert_not_called()

@patch("pygame.time.delay")
@patch("pygame.mixer.music")
@patch("music.upload_soundtracks", return_value=["track1.mp3", "track2.mp3"])
def test_overlay_music_in_loop_infinity(mock_upload, mock_music, mock_delay):
    # Підготовка
    music.current_track_index = 0
    music.music_playing.set()

    # Імітація завершення програвання двох треків в циклі
    mock_music.get_busy.side_effect = itertools.cycle([True, False])

    def stop_music_after_short_time():
        music.music_playing.clear() 

    stop_thread = threading.Timer(0.2, stop_music_after_short_time)
    stop_thread.start()

    thread = threading.Thread(target=music.overlay_music_in_loop_infinity)
    thread.start()
    thread.join(timeout=2)

    expected_calls = [call("track1.mp3"), call("track2.mp3")]

    # Перевіряємо, що принаймні один цикл був виконаний з потрібними треками
    mock_music.load.assert_has_calls(expected_calls, any_order=False)