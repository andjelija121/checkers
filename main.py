import pygame
from konstante import WIDTH, HEIGHT, SQUARE_SIZE
from igra import Igra
import renderer


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
    igra = Igra()

    while radi:
        sat.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                radi = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if (igra.pobednik is not None or igra.nereseno) and renderer.klik_na_igraj_opet(pos):
                    igra.resetuj()
                    continue

                red, kolona = uzmi_red_kolonu_od_misa(pos)
                igra.jedan_potez(red,kolona)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u:
                    igra.undo_potez()

        igra.update()
        renderer.nacrtaj(igra.tabla, PROZOR)
        renderer.nacrtaj_kraj_igre(PROZOR, igra.pobednik, igra.nereseno)
        pygame.display.update()

    pygame.quit()


main()
