import os
import pygame


def scale_image(img, factor):
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size)


def center_of(size):
    return size[0] // 2, size[1] // 2


def load_set_from_file(file_path):
    if not os.path.exists(file_path):
        return set()
    with open(file_path, "r") as file:
        return set(file.read().splitlines())


def save_lines_to_file(file_path, lines):
    with open(file_path, "w") as file:
        file.write("\n".join(lines))
