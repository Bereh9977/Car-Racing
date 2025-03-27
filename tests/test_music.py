import pytest
import pygame
import sys
import os
from unittest.mock import patch, MagicMock
import threading
from music import next_track, current_track_index

@pytest.fixture
def mock_soundtracks():
    """Фікстура для мокування завантаження треків."""
    # Мокаємо завантаження треків
    mock_soundtracks = [f"music/track{i}.mp3" for i in range(1, 5)]  # 4 треки
    with patch('music.upload_soundtracks', return_value=mock_soundtracks):
        yield mock_soundtracks

@pytest.fixture
def mock_pygame():
    """Фікстура для мокування pygame.mixer."""
    with patch('pygame.mixer.music.stop') as mock_stop, \
         patch('pygame.mixer.music.load') as mock_load, \
         patch('pygame.mixer.music.play') as mock_play:
        yield mock_stop, mock_load, mock_play

def test_next_track(mock_soundtracks, mock_pygame):
    """Тестування методу next_track для перевірки перемикання між треками."""
    
    # Початкове значення індексу
    assert current_track_index == 0

    # Мокаємо функцію pygame для тестування
    mock_stop, mock_load, mock_play = mock_pygame

    # Викликаємо метод next_track
    next_track()

    # Перевіряємо, що індекс змінився на наступний трек (1)
    assert current_track_index == 1

    # Перевіряємо, що зупинили поточний трек
    mock_stop.assert_called_once()

    # Перевіряємо, що новий трек завантажено
    mock_load.assert_called_once_with(mock_soundtracks[1])

    # Перевіряємо, що новий трек відтворюється
    mock_play.assert_called_once_with(1)
