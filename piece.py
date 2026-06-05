import pygame
from constants import SQUARE_SIZE, WHITE, BLACK, RED


class Piece:
    PADDING = 12
    OUTLINE = 3

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False

    def make_king(self):
        self.king = True

    def draw(self, win):
        radius = SQUARE_SIZE // 2 - self.PADDING
        x = self.col * SQUARE_SIZE + SQUARE_SIZE // 2
        y = self.row * SQUARE_SIZE + SQUARE_SIZE // 2

        pygame.draw.circle(win, BLACK, (x, y), radius + self.OUTLINE)
        pygame.draw.circle(win, self.color, (x, y), radius)

        if self.king:
            pygame.draw.circle(win, RED, (x, y), radius // 2, 4)