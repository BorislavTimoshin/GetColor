import pygame
from Py_files.settings import *


# Класс для хранения бутылок и обработки всего, что с ними связано
class Bottle:
    bottles = []

    def __init__(self, screen, position, liquids, liquid_positions):
        self.screen = screen
        self.position = position
        self.liquids = liquids
        self.liquid_positions = liquid_positions
        self.bottle = pygame.Rect(*position, *bottle_size)
        self.picked = False
        self.bottles.append(self)

    def move_top(self, purpose):
        """ Переливание верхней жидкости одной бутылки в другую """
        if len(self.liquids) > 0:
            first_liquid_current_bottle = self.liquids[0]
        else:
            first_liquid_current_bottle = False
        if len(purpose.liquids) > 0:
            first_liquid_purpose = purpose.liquids[0]
        else:
            first_liquid_purpose = False
        if (first_liquid_current_bottle == first_liquid_purpose or not first_liquid_purpose) and \
                first_liquid_current_bottle and self != purpose:
            # Делаем подсчет подряд идущих жидкостей одного цвета в текущей бутылке
            last_liquid = first_liquid_current_bottle
            number_of_liquids = 0
            for ind in range(len(self.liquids)):
                if self.liquids[ind] != last_liquid:
                    break
                last_liquid = self.liquids[ind]
                number_of_liquids += 1
            purpose.liquids = [first_liquid_current_bottle] * number_of_liquids + purpose.liquids  # Переливание жидкостей
            if len(purpose.liquid_positions) > 0:
                first_liquid_position_at_purpose = purpose.liquid_positions[0]
            else:
                first_liquid_position_at_purpose = purpose.position[0], purpose.position[1] + bottle_size[1]
            # Добавляем позиции недавно перелитых жидкостей
            for i in range(1, number_of_liquids + 1):
                purpose.liquid_positions.insert(
                    0,
                    (first_liquid_position_at_purpose[0], first_liquid_position_at_purpose[1] - i * 56)
                )
            # Удаляем первые counter жидкостей одного цвета из текущей бутылки
            del self.liquids[:number_of_liquids]
            del self.liquid_positions[:number_of_liquids]
        self.picked = False
        purpose.picked = False

    def draw(self):
        """ Рисование бутылок с жидкостями на основе новых позиций жидкостей liquid_positions """
        pygame.draw.rect(self.screen, bottle_color, self.bottle, 5)
        if self.picked:  # Если на бутылку нажали, то выделяем её белым цветом
            pygame.draw.rect(self.screen, (255, 255, 255), self.bottle, 5)
        for ind, liquid in enumerate(self.liquids):
            liquid_position = self.liquid_positions[ind]
            # Рисуем жидкость
            pygame.draw.rect(
                self.screen,
                colors_rgb[liquid],
                (liquid_position[0] + bottle_thickness,
                 liquid_position[1] - bottle_thickness,
                 liquid_size[0] - 2 * bottle_thickness,
                 liquid_size[1])
            )
            # Рисуем черный контур для жидкостей
            pygame.draw.rect(
                self.screen,
                (0, 0, 0),
                (liquid_position[0] + bottle_thickness,
                 liquid_position[1] - bottle_thickness,
                 liquid_size[0] - 2 * bottle_thickness,
                 liquid_size[1]), 1
            )

