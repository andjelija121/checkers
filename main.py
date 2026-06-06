import pygame
from constants import WIDTH, HEIGHT, SQUARE_SIZE
from board import Tabla


pygame.init()

PROZOR = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Junacki megdan")


def uzmi_red_kolonu_od_misa(pos):
    x, y = pos
    red = y // SQUARE_SIZE
    kolona = x // SQUARE_SIZE
    return red, kolona


def main():
    radi = True
    sat = pygame.time.Clock()
    tabla = Tabla()

    while radi:
        sat.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                radi = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                red, kolona = uzmi_red_kolonu_od_misa(pos)
                tabla.izaberi(red, kolona)

        tabla.nacrtaj(PROZOR)
        pygame.display.update()

    pygame.quit()


main()
