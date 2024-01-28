import pygame
import random
import sys
import os
import re
from bottle import Bottle
from animation import Particle, all_sprites_animation
from settings import *

pygame.init()
screen = pygame.display.set_mode(size)
background = pygame.image.load("Images/background.jpg")
icon_surface = pygame.image.load("Images/icon.png")
pygame.display.set_icon(icon_surface)
pygame.display.set_caption("Color Sort Bottles")
clock = pygame.time.Clock()
color_names = list(colors_rgb.keys())
first_pick = None
second_pick = None
all_sprites_bottle = pygame.sprite.Group()


# Класс, реализующий рисование прямоугольной кнопки
class Button:
    def __init__(self, width, height, color):
        self.width = width
        self.height = height
        self.color = color

    def draw_button(self, x, y, text, font_size=40, key=None, **kwargs):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if x < mouse[0] < x + self.width and y < mouse[1] < y + self.height:
            pygame.draw.rect(screen, self.color, (x, y, self.width, self.height))
            if click[0]:
                pygame.time.delay(300)
                if kwargs:
                    key(**kwargs)
                else:
                    key()
        else:
            pygame.draw.rect(screen, self.color, (x, y, self.width, self.height))
        print_text(text, (x + 5, y + 10), (0, 102, 0), font_size)


def load_image(name, color_key=None):
    fullname = os.path.join('Images', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print(f"Файл с изображением '{fullname}' не найден")
        raise SystemExit(message)
    if color_key is not None:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
            image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def create_bottles(level):
    """ Начало уровня:
     1) создание атрибута в виде списка, в котором хранится level + 3 бутылок и информауия о них (жидкости, их позиции)
     2) жидкости рандомно перемешиваются """
    amount_of_bottles = level + 3
    Bottle.bottles = []
    random_colors = random.sample(color_names, amount_of_bottles - 1)
    liquids = (random_colors * 20)[:amount_of_bottles*4]
    random.shuffle(liquids)
    for i in range(amount_of_bottles):
        bottle_position = x, y = (width_screen // (amount_of_bottles + 1)) * i + \
                                 (width_screen - amount_of_bottles * 80) // (amount_of_bottles + 1), 120
        # Позиции жидкостей в бутылке. Всегда по 4 жидкости в бутылке в начале игры
        liquid_positions = [
            (x, y + bottle_size[1] - 224),
            (x, y + bottle_size[1] - 168),
            (x, y + bottle_size[1] - 112),
            (x, y + bottle_size[1] - 56)
        ]
        Bottle(
            screen,
            bottle_position,
            liquids=liquids[i*4:i*4+4],
            liquid_positions=liquid_positions
        )


def lost() -> bool:
    """ Проверка на то, проиграл ли игрок (не может никуда расставить жидкости) """
    first_colors_bottles = [i.liquids[0] if len(i.liquids) > 0 else None for i in Bottle.bottles]
    if not win():  # Если мы не победили
        if None not in first_colors_bottles:  # Если нет пустых бутылок, то есть мы не можем перелить в пустую
            if len(first_colors_bottles) == len(set(first_colors_bottles)):  # Если все верхние цвета бутылок разные
                return True
    return False


def win() -> bool:
    """ Проверка на то, отсортированы ли все цвета в бутылках """
    # Проверка: есть ли бутылки, у которых цвет верхней жидкости совпадает. Если да, то нужно перелить
    first_colors_bottles = [i.liquids[0] if len(i.liquids) > 0 else None for i in Bottle.bottles]
    if len(first_colors_bottles) != len(set(first_colors_bottles)):
        return False
    # Проверка: есть ли бутылка-мультифрукт. Если да, то мы не победили
    for i in Bottle.bottles:
        if len(set(i.liquids)) > 1:
            return False
    return True


def draw_game(level):
    """ Функция, рисующая колбочки, кнопку назад: игровое поле """
    screen.blit(background, (0, 0))
    back = Button(100, 45, (217, 217, 196))
    back.draw_button(800, 660, "Назад", key=show_levels)
    again = Button(110, 45, (217, 217, 196))
    again.draw_button(670, 660, "Заново", key=start_level, level=level)
    # Рисуем бутылки
    for bottle in Bottle.bottles:
        bottle.draw()


def start_level(level):
    """ Начало выполнения уровня """
    global first_pick, second_pick
    first_pick, second_pick = None, None
    create_bottles(level)
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                for jar in Bottle.bottles:
                    if jar.bottle.collidepoint(e.pos):
                        if first_pick:  # Если бутылка уже была выбрана, и это уже второе нажатие
                            second_pick = jar
                            first_pick.move_top(second_pick)
                            # Если жидкости перелились в бутылке -> мы проигрываем и начинаем заново
                            if len(second_pick.liquids) > 8:
                                first_pick, second_pick = None, None
                                start_level(level)
                            first_pick, second_pick = None, None
                        else:  # Иначе сохраняем выбранную в первый раз бутылку
                            jar.picked = True
                            first_pick = jar
        draw_game(level)
        # Проверка на то, отмортированы жидкости или нет
        if win():
            pygame.display.flip()
            create_particles(pygame.mouse.get_pos(), level)
            start_level(level)
        elif lost():
            pygame.display.flip()
            start_level(level)
        pygame.display.flip()


def print_text(text, position, font_color, font_size):
    font_type = pygame.font.Font(None, font_size)
    text = font_type.render(text, True, font_color)
    screen.blit(text, position)


def create_particles(position, level):
    """ Функция, создающая анимацию звездопада """
    # количество создаваемых частиц
    particle_count = 150
    # возможные скорости
    numbers = range(-5, 6)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))
    for i in range(80):
        all_sprites_animation.update()
        draw_game(level)
        all_sprites_animation.draw(screen)
        pygame.display.flip()
        clock.tick(50)


def show_levels():
    """ Функция для вывода меню уровней """
    screen.blit(background, (0, 0))
    print_text("ВЫБЕРИТЕ УРОВЕНЬ ИГРЫ!", (100, 150), main_head_color, 80)
    all_sprites_bottle.draw(screen)
    level_1 = Button(175, 45, (217, 217, 196))
    level_2 = Button(175, 45, (217, 217, 196))
    level_3 = Button(175, 45, (217, 217, 196))
    level_4 = Button(175, 45, (217, 217, 196))
    level_5 = Button(175, 45, (217, 217, 196))
    back = Button(100, 45, (217, 217, 196))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()
        level_1.draw_button(402, 270, "УРОВЕНЬ 1", key=start_level, level=1)
        level_2.draw_button(402, 340, "УРОВЕНЬ 2", key=start_level, level=2)
        level_3.draw_button(402, 410, "УРОВЕНЬ 3", key=start_level, level=3)
        level_4.draw_button(402, 480, "УРОВЕНЬ 4", key=start_level, level=4)
        level_5.draw_button(402, 550, "УРОВЕНЬ 5", key=start_level, level=5)
        back.draw_button(440, 620, "Назад", key=start_screen)
        pygame.display.flip()
        clock.tick(15)


def get_rule() -> str:
    with open("Other_files/rules.txt", "r", encoding="utf-8") as file:
        rule = file.read()
    return rule


def print_rule_text(rule: str):
    rule_font = pygame.font.SysFont(None, 40)
    # Разбиваем текст на строки с учетом переносов
    lines = []
    sentences = [sentence.split() for sentence in re.split("\n", rule)]
    print(sentences)
    for sentence in sentences:
        current_line = ''
        for word in sentence:
            test_line = current_line + word + ' '
            if rule_font.size(test_line)[0] < width_screen - 130:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + ' '
        lines.append(current_line)
    # Отображаем текст на экране с учетом переносов
    y = 280
    for line in lines:
        rule_surface = rule_font.render(line, True, rule_color)
        screen.blit(rule_surface, (100, y))
        y += rule_font.size(line)[1]
    pygame.display.update()


def print_rule():
    """ Функция, печатающая правила игры """
    screen.blit(background, (0, 0))
    back = Button(100, 45, (217, 217, 196))
    print_text("ПРАВИЛА ИГРЫ", (240, 150), main_head_color, 90)
    rule = get_rule()
    print_rule_text(rule)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()
        back.draw_button(430, 620, "Назад", key=start_screen)
        pygame.display.flip()
        clock.tick(15)


def show_menu():
    """ Функция для вывода кнопок главного меню """
    button_start = Button(205, 45, (217, 217, 196))
    button_rule = Button(150, 45, (217, 217, 196))
    button_quit = Button(120, 45, (217, 217, 196))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()
        button_start.draw_button(385, 410, "НАЧАТЬ ИГРУ", key=show_levels)
        button_rule.draw_button(412, 480, "ПРАВИЛА", key=print_rule)
        button_quit.draw_button(427, 550, "ВЫХОД", key=sys.exit)
        pygame.display.flip()
        clock.tick(15)


def start_screen():
    screen.blit(background, (0, 0))
    print_text("Get Color", (290, 150), main_head_color, 130)
    all_sprites_bottle.draw(screen)
    show_menu()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()


bottle_sprite1 = pygame.sprite.Sprite()
bottle_sprite2 = pygame.sprite.Sprite()
bottle_sprite1.image = load_image("bottle.png")
bottle_sprite2.image = load_image("bottle.png")
bottle_sprite1.rect = bottle_sprite1.image.get_rect()
bottle_sprite2.rect = bottle_sprite2.image.get_rect()
bottle_sprite1.rect.x = -50
bottle_sprite1.rect.y = 320
bottle_sprite2.rect.x = 530
bottle_sprite2.rect.y = 320
all_sprites_bottle.add(bottle_sprite1)
all_sprites_bottle.add(bottle_sprite2)

start_screen()