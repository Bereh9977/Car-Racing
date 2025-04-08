import sys
import os
import pytest
import itertools
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


@pytest.fixture
def mock_music(monkeypatch):
    class MockMusic:
        def stop(self):
            pass
        def load(self, track):
            self.loaded_track = track
        def play(self, loops=0):
            self.played = True
        def get_busy(self):
            return False
        def set_volume(self, volume):
            pass  # Мок для set_volume

    mock = MockMusic()
    monkeypatch.setattr("pygame.mixer.music", mock)
    return mock

def test_next_track_switches_track(mock_music):
    # Готуємо звук
    music.soundtracks = [f"track{i}.mp3" for i in range(1, 4)] 
    music.current_track_index = 0
    music.music_playing.set()

    music.next_track()

    assert music.current_track_index == 1
    assert hasattr(mock_music, 'loaded_track') and mock_music.loaded_track == "track2.mp3"
    assert mock_music.played


def test_next_track_does_nothing_if_music_paused(mock_music):
    music.music_playing.clear()  
    music.soundtracks = ["track1.mp3", "track2.mp3"]
    music.current_track_index = 0

    music.next_track()

    assert music.current_track_index == 0
    assert not hasattr(mock_music, 'loaded_track')
    assert not hasattr(mock_music, 'played')


@pytest.fixture
def mock_upload_soundtracks(monkeypatch):
    monkeypatch.setattr(music, "upload_soundtracks", lambda: ["track1.mp3", "track2.mp3"])


@pytest.fixture
def mock_delay(monkeypatch):
    def fake_delay(x):
        pass
    monkeypatch.setattr("pygame.time.delay", fake_delay)

def test_overlay_music_in_loop_infinity(mock_upload_soundtracks, mock_music, mock_delay, monkeypatch):
    # Підготовка
    music.current_track_index = 0
    music.music_playing.set()

    # Імітація завершення програвання двох треків у циклі
    busy_cycle = itertools.cycle([True, False])
    def mock_get_busy():
        return next(busy_cycle)
    monkeypatch.setattr(mock_music, "get_busy", mock_get_busy)

    # Лог для відслідковування завантажених треків
    loaded_tracks = []

    def mock_load(track):
        loaded_tracks.append(track)

    # Підключаємо мок функції завантаження треків
    monkeypatch.setattr(mock_music, "load", mock_load)

    def stop_music_after_short_time():
        music.music_playing.clear()

    stop_thread = threading.Timer(0.5, stop_music_after_short_time)  # Затримка для циклічного відтворення
    stop_thread.start()

    thread = threading.Thread(target=music.overlay_music_in_loop_infinity)
    thread.start()
    thread.join(timeout=5)  # Чекаємо більше часу для циклу

    # Перевіряємо, що треки завантажувалися
    assert "track1.mp3" in loaded_tracks
    assert "track2.mp3" in loaded_tracks
    assert loaded_tracks[0] == "track1.mp3"  # Першим завантажується track1.mp3
    assert loaded_tracks[1] == "track2.mp3"  # Потім track2.mp3