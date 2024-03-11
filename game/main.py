import time

import pygame
import os
import sys
import random
import pygame_gui
from math import sin, cos, radians
from pygame import mixer

from data_base import get_information, update_data_base
from levels_information import get_level_status, change_level_status


# Загрузка изображения
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
        image.convert_alpha()

    return image


# инициализация pygame
pygame.init()
# инициализация плеера
mixer.init()

# Устанавливаем лимит на каналы
pygame.mixer.set_num_channels(20)

# Звук выстрела
shot_sound = mixer.Sound('data\\sounds\\shot.mp3')
shot_sound.set_volume(0.5)
# Звук столкновения
collision_sound = mixer.Sound('data\\sounds\\collision.mp3')
# Главная тема
main_theme = mixer.Sound('data\\sounds\\main_theme.mp3')
main_theme.set_volume(0.05)

# шаг корабля за одно нажатие
step = 0.5

pygame.display.set_caption('Со скоростью света')
SIZE = WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode(SIZE)
FPS = 60
clock = pygame.time.Clock()
main_theme.play(loops=-1)
arcade = False

# Скорость астероидов для легкого уровня
min_meteorite_speed_for_easy_level = 90
max_meteorite_speed_for_easy_level = 110
# шанс на выпадения аптечки - 10% (для легкого уровня)
easy_level_heal_drop = (1, 10)

# Скорость астероидов для сложного уровня
min_meteorite_speed_for_hard_level = 110
max_meteorite_speed_for_hard_level = 150
# шанс на выпадения аптечки - 5% (для сложного уровня)
hard_level_heal_drop = (1, 20)


# Скорость сломанного корабля (для легкого уроня)
min_broken_ship_speed_for_easy_level = 60
max_broken_ship_speed_for_easy_level = 80

# Скорость сломанного корабля (для сложного уроня)
min_broken_ship_speed_for_hard_level = 70
max_broken_ship_speed_for_hard_level = 100

# Време для начисления очков
points_generation_time = 9000

# Время увеличения уровня игры для аркады
level_change_time = 0

# Список с числами, которые отображают размер метеорита (на разные уровни сложности - разные списки, т.к. на легком
# уровне сложности больших метеоритов должно быть меньше, чем на высоком
# Список для легкого уровня сложности
easy_meteorite_array = [1, 1, 1, 1, 2, 2, 3]
# Список для сложного уровня
hard_meteorite_array = [1, 1, 2, 2, 2, 2, 3, 3]

arcade_mode = False
easy_mode = False
hard_mode = False
name_flag = False

meteorite_array = easy_meteorite_array
min_meteorite_speed = min_meteorite_speed_for_easy_level
max_meteorite_speed = max_meteorite_speed_for_easy_level
meteorite_generation_time = 3000
broken_ship_generation_time = 10000
ufo_generation_time = 13000
first_point, second_point = easy_level_heal_drop
min_broken_ship_speed = min_broken_ship_speed_for_hard_level
max_broken_ship_speed = max_broken_ship_speed_for_hard_level


# Размеры астероидов
# Маленького астероида
small_asteroid_size = load_image('small_asteroid.png').get_rect()[2:]
# Среднего Астероида
medium_asteroid_size = load_image('medium_asteroid.png').get_rect()[2:]
# Большого астероида
large_asteroid_size = load_image('large_asteroid.png').get_rect()[2:]
# Размер сломанного корабля
broken_ship_size = load_image('Broken_ship.png').get_rect()[2:]
# Развмер НЛО
ufo_size = load_image('ufo.png').get_rect()[2:]

# группа выстрелов
shots_sprites = pygame.sprite.Group()
# группа метеоритов
meteorite_sprites = pygame.sprite.Group()
# группа корабля
ship_sprite = pygame.sprite.Group()
# группа аптечек
heal_sprites = pygame.sprite.Group()
# группа препятствия сломанный корабль
broken_ship_sprites = pygame.sprite.Group()
# группа выстрелов сломанного корабля
shot_of_broken_ship_sprites = pygame.sprite.Group()
# группа нло
ufo_sprites = pygame.sprite.Group()


# типы метеоритов
small = 'small'
medium = 'medium'
large = 'large'


# Класс аптечек
class Heal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Heal, self).__init__(heal_sprites)
        self.image = load_image('heal.png')
        self.heal_count = 20
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)
        # скорость аптечки
        self.v = 2

    def update(self, points):
        self.rect = self.rect.move(0, self.v)

        ship = pygame.sprite.spritecollideany(self, ship_sprite,
                                              collided=pygame.sprite.collide_mask)

        if not ship is None:
            heal_sprites.remove(self)
            ship.change_heal_points('+', self.heal_count, points)
            ship.taken_heal += 1

        # Условие, позволяющее убирать аптечки, вылетевшие за пределы карты
        if self.rect.y >= HEIGHT:
            heal_sprites.remove(self)


# Класс линии здоровья
class HpLine:
    def __init__(self, max_hp):
        self.max_hp = max_hp
        self.x, self.y = 10, 565
        self.width, self.height = 380, 15
        self.color = pygame.Color(60, 170, 60)

        self.draw_hp(max_hp)

    def draw_hp(self, hp):
        # рамка
        pygame.draw.rect(screen, pygame.Color(53, 0, 134),
                         (self.x - 2, self.y - 2, self.width + 3, self.height + 3), width=2)

        # цвет полоски в зависимости от хп
        if hp / self.max_hp <= 0.2:
            self.color = pygame.Color(255, 36, 0)
        elif hp / self.max_hp <= 0.4:
            self.color = pygame.Color(255, 219, 88)
        elif hp / self.max_hp <= 0.2:
            self.color = pygame.Color(255, 36, 0)

        # линия здоровья
        pygame.draw.rect(screen, self.color,
                         (self.x, self.y, self.width * hp / self.max_hp, self.height))

        # текст хп
        font = pygame.font.Font(None, 20)
        text = font.render(f'{hp}/{self.max_hp}', True, pygame.Color(255, 255, 255))
        text_x = self.x + self.width // 2 - text.get_width() // 2
        text_y = self.y + self.height // 2 - text.get_height() // 2
        screen.blit(text, (text_x, text_y))


# класс выстрелов
class Shot(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(shots_sprites)
        self.image = load_image('shot_0.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)
        # скорость выстрела
        self.v = -10

    def update(self):
        self.rect = self.rect.move(0, self.v)
        # Удаление выстрела, если он вылетел за пределы карты
        # Условие, позволяющее убирать выстрелы, вылетевшие за пределы карты
        if self.rect.y <= 0:
            shots_sprites.remove(self)


# Класс корабля
class SpaceShip(pygame.sprite.Sprite):
    def __init__(self, speed, hp, damage):
        super().__init__(ship_sprite)
        self.speed = speed
        self.hp = hp
        self.hp_line = HpLine(self.hp)
        self.max_hp = hp
        self.damage = damage

        self.image = load_image('ship.png')
        self.rect = self.image.get_rect()
        self.rect.x = 275
        self.rect.y = 400
        self.mask = pygame.mask.from_surface(self.image)

        self.meteorite_killed = 0
        self.broken_ship_killed = 0
        self.taken_heal = 0

    """ Метод для изменения координат корабля """

    def move(self, movement_x, movement_y):
        self.rect = self.rect.move(self.speed * movement_x, self.speed * movement_y)

    """ Метод, возвращяющий координаты корабля """

    def get_cords(self):
        return self.rect.x, self.rect.y

    """ Метод, возвращающий размер корабля """

    def get_size(self):
        return self.image.get_rect()[2:]

    """ Метод, устанавливающий координаты """

    def set_cords(self, x, y):
        self.rect.x = x
        self.rect.y = y

    """ Метод, позволяющий стрелять """

    def shoot(self):
        bullet_x = self.rect.x
        bullet_y = self.rect.y
        shots_sprites.add(Shot(bullet_x, bullet_y))
        shot_sound.play()

    """ Метод, изменяющий hp """

    def change_heal_points(self, action, value, points):
        if action == '+':
            if self.hp == self.max_hp:
                pass
            else:
                self.hp += value
                if self.hp > self.max_hp:
                    self.hp = self.max_hp
        elif action == '-':
            self.hp -= value
            points.minus_points(50)

    """ Метод, непозволяющий кораблю вылететь за пределы карты """
    def update(self, *args):
        # обновление полоски хп
        self.hp_line.draw_hp(self.hp)

        if self.get_cords()[0] <= 0:
            self.set_cords(1, self.get_cords()[1])
        if self.get_cords()[1] <= 0:
            self.set_cords(self.get_cords()[0], 1)
        if self.get_cords()[0] >= WIDTH - self.get_size()[0]:
            self.set_cords(WIDTH - self.get_size()[0], self.get_cords()[1])
        if self.get_cords()[1] >= HEIGHT - self.get_size()[1]:
            self.set_cords(self.get_cords()[0], HEIGHT - 1 - self.get_size()[1])

    """ Метод, возвращающий урон, который наносит корабль """

    def get_damage(self):
        return self.damage


# Класс припятствий
class Meteorite(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, hp, damage, image, experience_for_kill, type):
        super().__init__(meteorite_sprites)
        self.image = load_image(image)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)

        self.type = type
        self.speed = speed
        self.max_hp = self.hp = hp
        self.damage = damage
        self.full_damage = True
        self.experience_for_kill = experience_for_kill

        # координата для движения (промежуточные)
        self.y_moving_coord = y

    def update(self, space_ship, points):
        # движение корабля
        self.y_moving_coord += self.speed / FPS
        self.rect = self.rect.move(0, int(self.y_moving_coord - self.rect.y))

        # попадание выстрела корабля
        shot = pygame.sprite.spritecollideany(self, shots_sprites,
                                              collided=pygame.sprite.collide_mask)
        if not shot is None:
            shots_sprites.remove(shot)
            self.minus_hp(space_ship.get_damage(), points, space_ship)

        # столкновение с метеоритом корябля
        ship = pygame.sprite.spritecollideany(self, ship_sprite,
                                              collided=pygame.sprite.collide_mask)
        if not ship is None:
            collision_sound.play()
            meteorite_sprites.remove(self)
            ship.change_heal_points('-', self.damage, points)

        if self.hp <= self.max_hp / 2:
            # Если метеорит разьился на мелкие кусочки, то его урон снижается вдвое
            if self.full_damage:
                self.damage //= 2
                self.full_damage = False

            if self.type == large:
                self.image = load_image('large_asteroid_half_hp.png')
            else:
                self.image = load_image('asteroid_half_hp.png')
            self.mask = pygame.mask.from_surface(self.image)

        # Условие, позволяющее убирать астероиды, вылетевшие за пределы карты
        if self.rect.y >= HEIGHT:
            meteorite_sprites.remove(self)

    """Метод, для уменьшеня количества hp при попадании"""

    def minus_hp(self, value, points, space_ship):
        self.hp -= value

        if self.hp <= 0:
            # выпадение хилки
            # first_point = second_point = 2  # 100% шанс
            if random.randint(first_point, second_point) == 2:
                # размер картинки хилки 40*40
                Heal((self.image.get_rect()[2] - 40) // 2 + self.rect.x, self.rect.y)

            # когда метеорит разрушается то он удалается
            meteorite_sprites.remove(self)
            points.add_points(300)
            space_ship.meteorite_killed += 1

    """Метод для получения информации о метеорите"""

    def get_information(self):
        return self.rect.x, self.rect.y, self.speed, self.hp

    """Метод, наносящий урон"""

    def get_damage(self):
        return self.damage

    def get_experience(self):
        return self.experience_for_kill


# Класс выстрелов сломанного корабля
class ShotOfBrokenShip(pygame.sprite.Sprite):
    def __init__(self, x, y, type_shot, ship_speed, ship_move_direction):
        super().__init__(shot_of_broken_ship_sprites)
        self.image = load_image(f'enemy_shot_round_{str(type_shot)}.png')
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = 110
        # скорость корабля
        self.ship_speed = ship_speed
        # дамаг при попадании высрела
        self.damage = 10
        # тип выстрела (откуда идет)
        self.type_shot = type_shot

        # направление
        self.move_direction = ship_move_direction
        # координата для движения
        self.y_moving_coord = y
        self.x_moving_coord = x

    def update(self, points):
        # движение
        if self.type_shot == 0:
            self.y_moving_coord -= self.speed / FPS

        elif self.type_shot == 1:
            self.y_moving_coord -= sin(radians(18)) * self.speed / FPS
            self.x_moving_coord += cos(radians(18)) * self.speed / FPS

        elif self.type_shot == 2:
            self.y_moving_coord -= sin(radians(-54)) * self.speed / FPS
            self.x_moving_coord += cos(radians(-54)) * self.speed / FPS

        elif self.type_shot == 3:
            self.y_moving_coord -= sin(radians(234)) * self.speed / FPS
            self.x_moving_coord += cos(radians(234)) * self.speed / FPS

        elif self.type_shot == 4:
            self.y_moving_coord -= sin(radians(162)) * self.speed / FPS
            self.x_moving_coord += cos(radians(162)) * self.speed / FPS

        # учитывается скорость движения корабля
        if self.move_direction == 'y':
            if self.type_shot != 0:
                self.y_moving_coord += self.ship_speed / FPS

        elif self.move_direction == 'x':
            self.x_moving_coord += self.ship_speed / FPS

        self.rect = self.rect.move(int(self.x_moving_coord - self.rect.x), int(self.y_moving_coord - self.rect.y))

        # побадание в гг корябль
        ship = pygame.sprite.spritecollideany(self, ship_sprite,
                                              collided=pygame.sprite.collide_mask)
        if not ship is None:
            shot_of_broken_ship_sprites.remove(self)
            ship.change_heal_points('-', self.damage, points)

        # Условие, позволяющее убирать выстрелы, вылетевшие за пределы карты
        if (self.rect.x < 0 or self.rect.x >= WIDTH) or (self.rect.y < 0 or self.rect.y >= HEIGHT):
            shot_of_broken_ship_sprites.remove(self)


# Класс сломанного корабля
# move_direction позволяет кораблю двигаться погоризонтали, если move_direction = y
class BrokenShip(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, move_direction):
        super().__init__(broken_ship_sprites)
        self.image = load_image('Broken_ship.png')
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.speed = speed
        self.hp = 55
        self. move_direction = move_direction
        # дамаг при столкновениии с конструкцией
        self.damage = 40
        # координата y для движения
        self.y_moving_coord = y
        # координата x для движения
        self.x_moving_coord = x

        # отсчет выстрелов
        self.clock_self = pygame.time.Clock()
        self.shot_time = 1000  # каждые shot_time миллисекунд удет выстрел
        self.time_past = self.clock_self.tick()  # время прошло с предыдущего выстрела

        # определяет откуда стреляет
        # отсчитывается по часовой стрелки с верхней пушки - 0
        # всего их 5 => 0-4
        self.type_shot = random.randrange(1, 5)

    # Движение сломанного корабля
    def update(self, space_ship, points):
        # движение корабля
        # Позволяет двигаться кораблю погоризонтали
        if self.move_direction == 'y':
            self.y_moving_coord += self.speed / FPS
            self.rect = self.rect.move(0, int(self.y_moving_coord - self.rect.y))
        elif self.move_direction == 'x':
            self.x_moving_coord += self.speed / FPS
            self.rect = self.rect.move(int(self.x_moving_coord - self.rect.x), 0)

        # Регистрация выстрелов гг корабля по сломанному кораблю
        shot = pygame.sprite.spritecollideany(self, shots_sprites,
                                              collided=pygame.sprite.collide_mask)
        if not shot is None:
            shots_sprites.remove(shot)
            self.minus_hp(space_ship.get_damage(), points, space_ship)

        # отсчет выстрелов
        tick = self.clock_self.tick()
        self.time_past += tick
        if self.time_past // self.shot_time > 0:
            self.time_past = self.time_past % tick
            self.shoot(self.type_shot)
            self.type_shot = (self.type_shot + 1) % 5

        if self.rect.y > HEIGHT:
            broken_ship_sprites.remove(self)

        # побадание в гг корябль
        ship = pygame.sprite.spritecollideany(self, ship_sprite,
                                              collided=pygame.sprite.collide_mask)
        if not ship is None:
            collision_sound.play()
            broken_ship_sprites.remove(self)
            ship.change_heal_points('-', self.damage, points)

        # Условие, позволяющее убирать корабли, вылетевшие за пределы карты
        if self.rect.y >= HEIGHT or (self.rect.x <= 0 - broken_ship_size[0] or self.rect.x >= WIDTH):
            broken_ship_sprites.remove(self)

    # стрельба
    def shoot(self, type_shot):
        a = self.image.get_rect()[2]  # сторона картинки корабля

        if type_shot == 0:
            image_shot = load_image('enemy_shot_round_0.png')
            x_shot = self.rect.x + self.image.get_rect()[2] // 2 - image_shot.get_rect()[2] // 2
            y_shot = self.rect.y - image_shot.get_rect()[3]

        elif type_shot == 1:
            image_shot = load_image('enemy_shot_round_1.png')
            x_shot = self.rect.x + round(a * 88 / 90)
            y_shot = self.rect.y + round(a * 32 / 90) - round(image_shot.get_rect()[3] * 20 / 26)

        elif type_shot == 2:
            x_shot = self.rect.x + round(a * 72 / 90)
            y_shot = self.rect.y + round(a * 8 / 9)

        elif type_shot == 3:
            image_shot = load_image('enemy_shot_round_3.png')
            x_shot = self.rect.x + round(a * 2 / 9) - image_shot.get_rect()[2]
            y_shot = self.rect.y + round(a * 8 / 9)

        elif type_shot == 4:
            image_shot = load_image('enemy_shot_round_4.png')
            x_shot = self.rect.x + round(a * 4 / 90) - image_shot.get_rect()[2]
            y_shot = self.rect.y + round(a * 32 / 90) - round(image_shot.get_rect()[3] * 20 / 26)

        shot_of_broken_ship_sprites.add(ShotOfBrokenShip(x_shot, y_shot, self.type_shot, self.speed, self.move_direction))

    # Уменьшение hp
    def minus_hp(self, count, points, space_ship):
        self.hp -= count
        if self.hp <= 0:
            # выпадение хилки
            # first_point = second_point = 2  # 100% шанс
            if random.randint(first_point, second_point) == 2:
                # размер картинки хилки 40*40
                Heal((self.image.get_rect()[2] - 40) // 2 + self.rect.x, self.rect.y)

            # когда сломанный корабль разрушается,то он удалается
            broken_ship_sprites.remove(self)
            points.add_points(400)
            space_ship.broken_ship_killed += 1

    def get_hp(self):
        return self.hp


# класс нло
class Ufo(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(ufo_sprites)
        self.image = load_image('ufo.png')
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.damage = 30
        self.hp = 20
        self.mask = pygame.mask.from_surface(self.image)
        self.speed_y = 85

        # сколько пикселей пройдет в данном направлении
        self.change_direction = self.generate_change_direction()
        # из какой координаты начинается движение в данном направлении
        self.last_x = x
        # скорость в данном направлении
        self.speed_x = self.generate_speed_x()
        # направо или навлево двигаеся в данной позиции списка self.change_direction_list
        self.left_right_dir = 1

        # координата для движения
        self.y_moving_coord = y
        self.x_moving_coord = x

    def generate_speed_x(self):
        return random.randrange(5, 160)

    def generate_change_direction(self):
        return random.randrange(30, 350)

    def update(self, space_ship, points):
        self.y_moving_coord += self.speed_y / FPS

        # смена позиции-направления по оси x
        if abs(self.last_x - self.rect.x) >= self.change_direction:
            self.change_direction = self.generate_change_direction()
            self.speed_x = self.generate_speed_x()
            self.last_x = self.rect.x
            self.left_right_dir *= -1

        # чтобы не выходил за экран вправо и влево
        if self.rect.x + self.image.get_rect()[2] >= WIDTH:
            self.left_right_dir = -1
            self.change_direction = self.generate_change_direction()
            self.last_x = self.rect.x
        elif self.rect.x <= 0:
            self.left_right_dir = 1
            self.change_direction = self.generate_change_direction()
            self.last_x = self.rect.x

        self.x_moving_coord += self.left_right_dir * self.speed_x / FPS

        self.rect = self.rect.move(int(self.x_moving_coord - self.rect.x), int(self.y_moving_coord - self.rect.y))

        # удаление после вылета за карту
        if self.rect.y > HEIGHT:
            ufo_sprites.remove(self)

        # побадание в гг корябль
        ship = pygame.sprite.spritecollideany(self, ship_sprite,
                                              collided=pygame.sprite.collide_mask)
        if not ship is None:
            collision_sound.play()
            ufo_sprites.remove(self)
            points.minus_points(950)
            ship.change_heal_points('-', self.damage, points)

        # попадание выстрела гг корабля с нло
        shot = pygame.sprite.spritecollideany(self, shots_sprites,
                                              collided=pygame.sprite.collide_mask)
        if not shot is None:
            shots_sprites.remove(shot)
            self.minus_hp(space_ship.get_damage(), points)

    # Уменьшение hp
    def minus_hp(self, count, points):
        self.hp -= count
        if self.hp <= 0:
            # выпадение хилки
            # first_point = second_point = 2  # 100% шанс
            if random.randint(first_point, second_point) == 2:
                # размер картинки хилки 40*40
                Heal((self.image.get_rect()[2] - 40) // 2 + self.rect.x, self.rect.y)

            # когда нло разрушается,то он удалается
            ufo_sprites.remove(self)
            points.minus_points(1000)


# Класс очков
class Points:
    def __init__(self):
        self.count = 0
        self.x, self.y = 10, 545

    def add_points(self, count):
        self.count += count

    def get_points(self):
        return self.count

    def minus_points(self, count):
        if self.count - count >= 0:
            self.count -= count

    def draw_points(self):
        font = pygame.font.Font(None, 25)
        points_text = font.render('Points: ', True, (255, 255, 255))
        screen.blit(points_text, (self.x, self.y))
        count_text = font.render(str(self.count), True, (255, 255, 255))
        screen.blit(count_text, (self.x + points_text.get_width(), self.y))


# Создание метеорита
def create_meteorite():
    meteorite_y = 0
    meteorite_speed = random.randint(min_meteorite_speed, max_meteorite_speed)
    meteorite_size = random.choice(meteorite_array)
    # Самый маленький метеорит
    if meteorite_size == 1:
        meteorite_x = random.randint(1, WIDTH - small_asteroid_size[0])
        meteorite_hp = 10
        meteorite_damage = 10
        meteorite_image = 'small_asteroid.png'
        meteorite_type = small
        # опыт за разрушение астероида
        experience_for_kill = 100
    # Средний метеорит
    elif meteorite_size == 2:
        meteorite_x = random.randint(1, WIDTH - medium_asteroid_size[0])
        meteorite_hp = 20
        meteorite_damage = 20
        meteorite_image = 'medium_asteroid.png'
        meteorite_type = medium
        # опыт за разрушение астероида
        experience_for_kill = 200
    elif meteorite_size == 3:
        meteorite_x = random.randint(1, WIDTH - large_asteroid_size[0])
        meteorite_hp = 50
        meteorite_damage = 30
        meteorite_image = 'large_asteroid.png'
        meteorite_type = large
        # опыт за разрушение астероида
        experience_for_kill = 300

    new_meteorite = Meteorite(meteorite_x, meteorite_y, meteorite_speed,
                              meteorite_hp, meteorite_damage, meteorite_image,
                              experience_for_kill, meteorite_type)


# Создание НЛО
def create_ufo():
    ufo_x = random.randint(1, WIDTH - ufo_size[0])
    ufo_y = 0
    ufo = Ufo(ufo_x, ufo_y)


# Создание сломанного корабля
def create_broken_ship():
    generation_array = [1, 2]
    broken_ship_speed = random.randint(min_broken_ship_speed, max_broken_ship_speed)
    if random.choice(generation_array) == 1:
        broken_ship_y = 0
        broken_ship_x = random.randint(1, WIDTH - broken_ship_size[0])
        move_direction = 'y'
    else:
        broken_ship_y = random.randint(1, WIDTH - broken_ship_size[0])
        broken_ship_x = random.choice([1, WIDTH - broken_ship_size[0]])
        move_direction = 'x'
        # Позволяет кораблю лететь влево
        if broken_ship_x == WIDTH - broken_ship_size[0]:
            broken_ship_speed *= -1

    broken_ship = BrokenShip(broken_ship_x, broken_ship_y, broken_ship_speed, move_direction)


# менеджер для интерфейса
manager = pygame_gui.UIManager(SIZE)


def game():
    global min_meteorite_speed
    global max_meteorite_speed
    global meteorite_generation_time
    global broken_ship_generation_time
    global ufo_generation_time
    global level_change_time
    global first_point, second_point
    global min_broken_ship_speed
    global max_broken_ship_speed
    global easy_mode
    global hard_mode

    # Создание экземпляра класса SpaceShip
    # Аргументы: Скоргость, hp, урон
    space_ship = SpaceShip(10, 100, 5)
    ship_sprite.add(space_ship)
    movement_x = movement_y = 0

    # Создание события при которм появляются метеориты
    METEORITEGENERATION = pygame.USEREVENT + 1
    pygame.time.set_timer(METEORITEGENERATION, meteorite_generation_time)
    # Создание события, которое начисляет очки
    GIVEPOINTS = pygame.USEREVENT + 2
    pygame.time.set_timer(GIVEPOINTS, points_generation_time)
    # Создание события генерации сломанного корабля
    BROKENSHIPGENERATION = pygame.USEREVENT + 3
    pygame.time.set_timer(BROKENSHIPGENERATION, broken_ship_generation_time)
    # Создания события, которое создает НЛО
    UFOGENERATION = pygame.USEREVENT + 4
    pygame.time.set_timer(UFOGENERATION, ufo_generation_time)

    LEVELCHANGE = pygame.USEREVENT + 5
    pygame.time.set_timer(LEVELCHANGE, level_change_time)

    points = Points()

    paused = False

    running = True
    while running:
        # Задний фон
        if not paused:
            background = Background("space_1.png", [0, 0])
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return terminate
                # пауза
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        paused = True
                # Создание метеорита с случайными положением, радиусом, скоростью и кол-вом hp
                if event.type == METEORITEGENERATION:
                    create_meteorite()
                if event.type == LEVELCHANGE:
                    print(meteorite_generation_time)
                    print(max_meteorite_speed)
                    if min_meteorite_speed <= 150:
                        min_meteorite_speed += 20
                    if meteorite_generation_time > 1000:
                        meteorite_generation_time -= 1000
                    if max_meteorite_speed <= 210:
                        max_meteorite_speed += 20
                    if broken_ship_generation_time > 4000:
                        broken_ship_generation_time -= 2000
                    if ufo_generation_time > 10000:
                        ufo_generation_time -= 1000
                    if level_change_time <= 50000:
                        level_change_time += 5000
                    if level_change_time >= 45000:
                        broken_ship_generation_time -= 1000
                        level_change_time = 0
                    if level_change_time > 29000:
                        level_change_time = 0
                    if min_broken_ship_speed <= 100:
                        min_broken_ship_speed += 10
                    if max_broken_ship_speed <= 140:
                        max_broken_ship_speed += 10
                    # Создание события при которм появляются метеориты
                    METEORITEGENERATION = pygame.USEREVENT + 1
                    pygame.time.set_timer(METEORITEGENERATION, meteorite_generation_time)
                    # Создание события, которое начисляет очки
                    GIVEPOINTS = pygame.USEREVENT + 2
                    pygame.time.set_timer(GIVEPOINTS, points_generation_time)
                    # Создание события генерации сломанного корабля
                    BROKENSHIPGENERATION = pygame.USEREVENT + 3
                    pygame.time.set_timer(BROKENSHIPGENERATION, broken_ship_generation_time)
                    # Создания события, которое создает НЛО
                    UFOGENERATION = pygame.USEREVENT + 4
                    pygame.time.set_timer(UFOGENERATION, ufo_generation_time)
                    LEVELCHANGE = pygame.USEREVENT + 5
                    pygame.time.set_timer(LEVELCHANGE, level_change_time)
                # Создание сломанного корабля
                if event.type == BROKENSHIPGENERATION:
                    create_broken_ship()
                # Начисленеи очков
                if event.type == GIVEPOINTS:
                    points.add_points(100)
                if event.type == UFOGENERATION:
                    create_ufo()
                # Вызов функции, производящей выстрел
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    space_ship.shoot()
                # движение
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        movement_y = -step
                    if event.key == pygame.K_s:
                        movement_y = step
                    if event.key == pygame.K_d:
                        movement_x = step
                    if event.key == pygame.K_a:
                        movement_x = -step
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_w:
                        movement_y = 0
                    if event.key == pygame.K_s:
                        movement_y = 0
                    if event.key == pygame.K_d:
                        movement_x = 0
                    if event.key == pygame.K_a:
                        movement_x = 0

            space_ship.move(movement_x, movement_y)

            # когда гг корабль умирает игра заканчивается
            if space_ship.hp <= 0:
                ship_sprite.remove(space_ship)
                running = False
                return final_screen(points.count)

            if easy_mode:
                if points.count >= 7000:
                    running = False
                    change_level_status('first_level_passed')
                    return final_screen(points.count, result='WIN')
            if hard_mode:
                if space_ship.broken_ship_killed >= 1 and space_ship.taken_heal <= 5\
                        and space_ship.meteorite_killed >= 6: #########################################################################
                    running = False
                    change_level_status('second_level_passed')
                    return final_screen(points.count, result='WIN')

            # Отображения заднего фона
            screen.fill([255, 255, 255])
            screen.blit(background.image, background.rect)

            meteorite_sprites.draw(screen)
            meteorite_sprites.update(space_ship, points)

            shots_sprites.draw(screen)
            shots_sprites.update()

            ship_sprite.draw(screen)
            ship_sprite.update(points)

            heal_sprites.draw(screen)
            heal_sprites.update(points)

            broken_ship_sprites.draw(screen)
            broken_ship_sprites.update(space_ship, points)

            shot_of_broken_ship_sprites.draw(screen)
            shot_of_broken_ship_sprites.update(points)

            ufo_sprites.draw(screen)
            ufo_sprites.update(space_ship, points)

            points.draw_points()

            pygame.display.flip()
            clock.tick(FPS)
        else: ##################################################################################################################
            flag = False
            manager.clear_and_reset()

            end_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(((WIDTH - 150) // 2, 400), (150, 30)),
                text='Завершить игру',
                manager=manager,
            )
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return terminate
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            paused = False
                            flag = True
                            movement_x, movement_y = 0, 0
                            break
                    if event.type == pygame.USEREVENT:
                        if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                            if event.ui_element == end_button:
                                running = False
                                return start_screen()
                    manager.process_events(event)

                if flag:
                    break

                if easy_mode:
                    font = pygame.font.Font(None, 24)
                    text1 = font.render('Задача: набрать 7000 очков', True, (255, 255, 255))
                    screen.blit(text1, (10, 10))
                    text1 = font.render(f'Набрано: {points.count}/7000', True, (255, 255, 255))
                    screen.blit(text1, (10, 37))
                elif hard_mode:
                    font = pygame.font.Font(None, 23)
                    text1 = font.render('Задача: убить  1 сломанный корабль', True, (255, 255, 255))
                    text11 = font.render('               6 метеоритов, ', True, (255, 255, 255))
                    text111 = font.render('        подобрать не более 5 хилок', True, (255, 255, 255))
                    screen.blit(text1, (10, 10))
                    screen.blit(text11, (10, 36))
                    screen.blit(text111, (10, 62))
                    text2 = font.render(f'Сломанных кораблей: {space_ship.broken_ship_killed}/1', True, (255, 255, 255))
                    screen.blit(text2, (10, 88))
                    text2 = font.render(f'Метеоритов: : {space_ship.meteorite_killed}/6', True, (255, 255, 255))
                    screen.blit(text2, (10, 114))
                    text3 = font.render(f'Хилок: : {space_ship.taken_heal}', True, (255, 255, 255))
                    screen.blit(text3, (10, 140))

                screen.blit(load_image('start_pause.png', -1), ((WIDTH - 128) // 2, (HEIGHT - 128) // 2))

                time_delta = clock.tick(FPS) / 1000.0
                manager.update(time_delta)
                manager.draw_ui(screen)
                pygame.display.flip()


# Класс заднего фона
class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location


def table():
    data = get_information()
    manager.clear_and_reset()
    background = Background('space_1.png', [0, 0])
    menu_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(((WIDTH - 150) // 2, 400), (150, 30)),
        text='Меню',
        manager=manager,
    )
    while True:
        for final_screen_event in pygame.event.get():
            if final_screen_event.type == pygame.QUIT:
                return terminate
            if final_screen_event.type == pygame.USEREVENT:
                if final_screen_event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if final_screen_event.ui_element == menu_button:
                        return start_screen
            manager.process_events(final_screen_event)

        # Отображения заднего фона
        screen.fill([0, 0, 0])
        # screen.blit(background.image, background.rect)

        try:
            for i in range(50, 300, 50):
                pygame.draw.line(screen, pygame.Color(255, 255, 255), (10, i), (WIDTH - 10, i))

                font1 = pygame.font.Font(None, 40)
                text = font1.render(f'{i // 50}', True, pygame.Color(255, 255, 255))
                text_x = 40 - text.get_width() // 2 - 5
                text_y = i + 14
                screen.blit(text, (text_x, text_y))

                font2 = pygame.font.Font(None, 20)
                text2 = font2.render(data[i // 50 - 1][0], True, pygame.Color(255, 255, 255))
                text_y = i + 15
                text_x2 = 65
                screen.blit(text2, (text_x2, text_y))

                font3 = pygame.font.Font(None, 25)
                text3 = font3.render(f'{data[i // 50 - 1][1]}', True, pygame.Color(255, 255, 255))
                text_y = i + 15
                text_x3 = 295
                screen.blit(text3, (text_x3, text_y))
        except:
            pass

        pygame.draw.line(screen, pygame.Color(255, 255, 255), (10, 300), (WIDTH - 10, 300))
        pygame.draw.line(screen, pygame.Color(255, 255, 255), (10, 50), (10, 300))
        pygame.draw.line(screen, pygame.Color(255, 255, 255), (60, 50), (60, 300))
        pygame.draw.line(screen, pygame.Color(255, 255, 255), (290, 50), (290, 300))
        pygame.draw.line(screen, pygame.Color(255, 255, 255), (WIDTH - 10, 50), (WIDTH - 10, 300))

        time_delta = clock.tick(FPS) / 1000.0
        manager.update(time_delta)
        manager.draw_ui(screen)

        pygame.display.flip()


def terminate():
    pygame.quit()
    sys.exit()


def choice_of_game_mode():
    global meteorite_array
    global min_meteorite_speed
    global max_meteorite_speed
    global meteorite_generation_time
    global broken_ship_generation_time
    global ufo_generation_time
    global first_point, second_point
    global min_broken_ship_speed
    global max_broken_ship_speed
    global arcade_mode
    global easy_level_heal_drop
    global hard_level_heal_drop
    global level_change_time
    global easy_mode
    global hard_mode

    manager.clear_and_reset()
    background = Background('start_fon_2.png', [0, 0])
    arcade_mode_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(((WIDTH - 150) // 2, 250), (150, 50)),
        text='АРКАДА',
        manager=manager,
    )
    levels_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(((WIDTH - 150) // 2, 305), (150, 30)),
        text='УРОВНИ',
        manager=manager,
    )
    open_main_screen_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(((WIDTH - 150) // 2, 400), (150, 30)),
        text='НА ГЛАВНЫЙ',
        manager=manager,
    )

    while True:
        for choice_of_game_mode_event in pygame.event.get():
            if choice_of_game_mode_event.type == pygame.QUIT:
                return terminate
            if choice_of_game_mode_event.type == pygame.USEREVENT:
                if choice_of_game_mode_event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if choice_of_game_mode_event.ui_element == arcade_mode_button:
                        # Режим аркады
                        arcade_mode = True
                        easy_mode = False
                        hard_mode = False
                        meteorite_array = hard_meteorite_array
                        min_meteorite_speed = min_meteorite_speed_for_easy_level - 20
                        max_meteorite_speed = max_meteorite_speed_for_easy_level - 20
                        meteorite_generation_time = 5000
                        broken_ship_generation_time = 17000
                        ufo_generation_time = 20000
                        level_change_time = 1000
                        first_point, second_point = hard_level_heal_drop
                        min_broken_ship_speed = min_broken_ship_speed_for_hard_level - 20
                        max_broken_ship_speed = max_broken_ship_speed_for_hard_level - 20
                        return game
                    if choice_of_game_mode_event.ui_element == levels_button:
                        return levels
                    if choice_of_game_mode_event.ui_element == open_main_screen_button:
                        return start_screen
            manager.process_events(choice_of_game_mode_event)

        # Отображения заднего фона
        screen.fill([255, 255, 255])
        screen.blit(background.image, background.rect)

        time_delta = clock.tick(FPS) / 1000.0
        manager.update(time_delta)
        manager.draw_ui(screen)

        pygame.display.flip()


def levels():
    global meteorite_array
    global min_meteorite_speed
    global max_meteorite_speed
    global meteorite_generation_time
    global broken_ship_generation_time
    global ufo_generation_time
    global first_point, second_point
    global min_broken_ship_speed
    global max_broken_ship_speed
    global arcade_mode
    global easy_level_heal_drop
    global hard_level_heal_drop
    global level_change_time
    global hard_mode
    global easy_mode

    manager.clear_and_reset()
    background = Background('start_fon_2.png', [0, 0])

    dict1 = get_level_status()

    if dict1['first_level_passed'] == 'True':
        first_level_text = '1 - ПРОЙДЕНО'
    else:
        first_level_text = '1'

    if dict1['second_level_passed'] == 'True':
        second_level_text = '2 - ПРОЙДЕНО'
    else:
        second_level_text = '2'

    level_1 = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(((WIDTH - 150) // 2, 250), (150, 30)),
        text=first_level_text,
        manager=manager,
    )
    level_2 = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(((WIDTH - 150) // 2, 285), (150, 30)),
        text=second_level_text,
        manager=manager,
    )
    open_main_screen_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(((WIDTH - 150) // 2, 400), (150, 30)),
        text='НА ГЛАВНЫЙ',
        manager=manager,
    )

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return terminate
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == level_1:
                        # Легкий уровень
                        easy_mode = True
                        arcade_mode = False
                        hard_mode = False
                        meteorite_array = easy_meteorite_array
                        min_meteorite_speed = min_meteorite_speed_for_easy_level
                        max_meteorite_speed = max_meteorite_speed_for_easy_level
                        meteorite_generation_time = 3000
                        broken_ship_generation_time = 10000
                        # В легком режиме нет НЛО
                        ufo_generation_time = 0
                        first_point, second_point = easy_level_heal_drop
                        min_broken_ship_speed = min_broken_ship_speed_for_hard_level
                        max_broken_ship_speed = max_broken_ship_speed_for_hard_level
                        return game
                    if event.ui_element == level_2:
                        # Сложный уровень
                        hard_mode = True
                        arcade_mode = False
                        easy_mode = False
                        meteorite_array = hard_meteorite_array
                        min_meteorite_speed = min_meteorite_speed_for_hard_level
                        max_meteorite_speed = max_meteorite_speed_for_hard_level
                        meteorite_generation_time = 2000
                        broken_ship_generation_time = 5000
                        ufo_generation_time = 12000
                        first_point, second_point = hard_level_heal_drop
                        min_broken_ship_speed = min_broken_ship_speed_for_easy_level
                        max_broken_ship_speed = max_broken_ship_speed_for_easy_level
                        return game
                    if event.ui_element == open_main_screen_button:
                        return start_screen

            manager.process_events(event)

        # Отображения заднего фона
        screen.fill([255, 255, 255])
        screen.blit(background.image, background.rect)

        time_delta = clock.tick(FPS) / 1000.0
        manager.update(time_delta)
        manager.draw_ui(screen)

        pygame.display.flip()


# начальный экран
def start_screen():
    global shots_sprites
    global meteorite_sprites
    global ship_sprite
    global heal_sprites
    global broken_ship_sprites
    global shot_of_broken_ship_sprites
    global ufo_sprites

    # группа выстрелов
    shots_sprites.empty()
    # группа метеоритов
    meteorite_sprites.empty()
    # группа корабля
    ship_sprite.empty()
    # группа аптечек
    heal_sprites.empty()
    # группа препятствия сломанный корабль
    broken_ship_sprites.empty()
    # группа выстрелов сломанного корабля
    shot_of_broken_ship_sprites.empty()
    # группа нло
    ufo_sprites.empty()

    manager.clear_and_reset()
    background = Background('start_fon_2.png', [0, 0])
    # кнопка запускающая игру
    play_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(((WIDTH - 150) // 2, 250), (150, 50)),
        text='ИГРАТЬ',
        manager=manager,
    )
    rating_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(((WIDTH - 150) // 2, 305), (150, 30)),
        text='РЕЙТИНГ',
        manager=manager,
    )

    while True:
        for start_screen_event in pygame.event.get():
            if start_screen_event.type == pygame.QUIT:
                return terminate
            if start_screen_event.type == pygame.USEREVENT:
                if start_screen_event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if start_screen_event.ui_element == play_button:
                        return choice_of_game_mode
                    if start_screen_event.ui_element == rating_button:
                        return table

            manager.process_events(start_screen_event)

        # Отображения заднего фона
        screen.fill([255, 255, 255])
        screen.blit(background.image, background.rect)

        time_delta = clock.tick(FPS) / 1000.0
        manager.update(time_delta)
        manager.draw_ui(screen)

        pygame.display.flip()


def final_screen(points, result=False):
    global name_flag
    manager.clear_and_reset()
    background = Background('space_1.png', [0, 0])

    # координаты воображемой рамки в которой записан текст
    alignment_x = 60
    alignment_x_end = 340
    alignment_y = 180

    # ввод текста
    if arcade_mode:
        entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(alignment_x_end - 120, alignment_y + 45, 120, 30),
            manager=manager,
        )

    # кнопка - начать заново
    menu_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(((WIDTH - 150) // 2, 340), (150, 30)),
        text='Меню',
        manager=manager,
    )

    while True:
        for final_screen_event in pygame.event.get():
            if final_screen_event.type == pygame.QUIT:
                return terminate
            if final_screen_event.type == pygame.USEREVENT:
                if final_screen_event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if final_screen_event.ui_element == menu_button:
                        if arcade_mode:
                            person_name = entry.get_text()
                            if person_name == '':
                                name_flag = True
                                return final_screen(points)
                            else:
                                name_flag = False
                                update_data_base([person_name, points])
                                return start_screen
                        else:
                            return start_screen
            manager.process_events(final_screen_event)

        # Отображения заднего фона
        screen.fill([0, 0, 0])
        screen.blit(background.image, background.rect)

        # текст
        font1 = pygame.font.Font(None, 60)
        text = font1.render('Game over', True, pygame.Color(229, 43, 80))
        text_x = WIDTH // 2 - text.get_width() // 2
        text_y = 100
        screen.blit(text, (text_x, text_y))

        if name_flag:
            font_name = pygame.font.Font(None, 60)
            text_name = font_name.render('Введите имя', True, pygame.Color(229, 43, 80))
            text_name_x = WIDTH // 2 - text_name.get_width() // 2
            text_name_y = 500
            screen.blit(text_name, (text_name_x, text_name_y))

        font2 = pygame.font.Font(None, 24)
        score_t = font2.render(f'Счёт: {points}', True, pygame.Color(255, 255, 255))
        screen.blit(score_t, (alignment_x, alignment_y))
        if arcade_mode:
            pygame.draw.line(screen, pygame.Color(255, 255, 255),
                             (alignment_x, alignment_y + 25), (alignment_x_end, alignment_y + 25))

            name_t = font2.render('Имя: ', True, pygame.Color(255, 255, 255))
            screen.blit(name_t, (alignment_x, alignment_y + 50))
        if easy_mode is True or hard_mode is True:
            if result == 'WIN':
                font_w = pygame.font.Font(None, 60)
                text_w = font_w.render('ПОБЕДА', True, pygame.Color(229, 43, 80))
                text_w_x = WIDTH // 2 - text_w.get_width() // 2
                text_w_y = 400
                screen.blit(text_w, (text_w_x, text_w_y))
            else:
                font_l = pygame.font.Font(None, 60)
                text_l = font_l.render('ПОРАЖЕНИЕ', True, pygame.Color(229, 43, 80))
                text_l_x = WIDTH // 2 - text_l.get_width() // 2
                text_l_y = 400
                screen.blit(text_l, (text_l_x, text_l_y))

        time_delta = clock.tick(FPS) / 1000.0
        manager.update(time_delta)
        manager.draw_ui(screen)

        pygame.display.flip()


def main():
    # вызов функций
    # чтобы не было вложенности функций
    # каждую активную функцию сначало закрываем
    # и потом отсюда вызываем следующую
    call = start_screen
    while True:
        call = call()


main()
