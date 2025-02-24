import pygame
import threading

pygame.init()

music_playing = threading.Event()
music_playing.set()
music_thread = None
current_track_index = 0
soundtracks = []
effect_music_channel = pygame.mixer.Channel(0)

def upload_soundtracks():
    global soundtracks
    if not soundtracks:
        soundtracks = [f"D:/CarRacing/soundtracks/track{i}.mp3" for i in range(1, 15)]
    return soundtracks

def overlay_music_in_loop_infinity():
    global current_track_index
    soundtracks = upload_soundtracks()
    while music_playing.is_set():
        pygame.mixer.music.load(soundtracks[current_track_index])
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(1)

        while pygame.mixer.music.get_busy() and music_playing.is_set():
            pygame.time.delay(100)

        if not music_playing.is_set():
            break

        current_track_index = (current_track_index + 1) % len(soundtracks)

def overlay_music_in_loop(background_audio_path):
    effect_music_channel.play(pygame.mixer.Sound(background_audio_path), loops=0, maxtime=0, fade_ms=0)

def stop_music():
    pygame.mixer.music.pause()  # Зупиняємо поточне відтворення
    music_playing.clear()     # Вимикаємо флаг

def start_music():
    global music_thread
    music_playing.set()
    if music_thread is None or not music_thread.is_alive():  # Якщо потік неактивний
        music_thread = threading.Thread(target=overlay_music_in_loop_infinity, daemon=True)
        music_thread.start()

def next_track():
    global current_track_index
    if music_playing.is_set():
        current_track_index = (current_track_index + 1) % len(upload_soundtracks())
        pygame.mixer.music.stop()
        pygame.mixer.music.load(soundtracks[current_track_index])
        pygame.mixer.music.play(1)

def mute_music():
    if music_playing.is_set():
        stop_music()
    else:
        start_music()

def stop_sound():
    effect_music_channel.stop()