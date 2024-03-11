"""Просто файл с размерами метеоритов"""
import os
import pygame
import sys


pygame.init()


def load_image(name, colorkey=None):
    fullname = os.path.join('data\\images', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)

    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        # image.convert_alpha()
        pass

    return image


first_image = load_image('small_asteroid.png')
rect = first_image.get_rect()
print(f'first pic {rect[2:]}')
second_image = load_image('asteroid_s1.png')
rect_2 = second_image.get_rect()
print(f'second pic {rect_2[2:]}')
