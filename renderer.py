import pygame
from konstante import ROWS, COLS, SQUARE_SIZE, BROWN, BEIGE, GOLD, LIGHT_GOLD, WIDTH, HEIGHT, WHITE
import pravila


IGRAJ_OPET_RECT = pygame.Rect(WIDTH // 2 - 95, HEIGHT // 2 + 45, 190, 52)


def nacrtaj_polja(tabla, prozor):
    prozor.fill(BEIGE)

    for red in range(ROWS):
        for kolona in range(COLS):
            if (red + kolona) % 2 == 1:
                pygame.draw.rect(
                    prozor,
                    BROWN,
                    (kolona * SQUARE_SIZE, red * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                )


def nacrtaj(tabla, prozor):
    nacrtaj_polja(tabla, prozor)
    nacrtaj_validne_poteze(tabla, prozor)

    for figura in tabla.tabla:
        if figura is not None:
            figura.nacrtaj(prozor)

    nacrtaj_izabranu_figuru(tabla, prozor)


def nacrtaj_validne_poteze(tabla, prozor):
    if tabla.izabrana_figura is None:
        return

    vreme = pygame.time.get_ticks()
    puls = int(3 + 2 * abs((vreme % 900) / 450 - 1))
    validni, *_ = pravila.validni_potezi(tabla, tabla.izabrana_figura)

    for indeks in validni:
        red, kolona = tabla.indeks_u_red_kolonu(indeks)
        x = kolona * SQUARE_SIZE + SQUARE_SIZE // 2
        y = red * SQUARE_SIZE + SQUARE_SIZE // 2

        pygame.draw.circle(prozor, LIGHT_GOLD, (x, y), 18 + puls, 3)
        pygame.draw.circle(prozor, GOLD, (x, y), 7)


def nacrtaj_izabranu_figuru(tabla, prozor):
    if tabla.izabrana_figura is None:
        return

    x = tabla.izabrana_figura.col * SQUARE_SIZE + SQUARE_SIZE // 2
    y = tabla.izabrana_figura.row * SQUARE_SIZE + SQUARE_SIZE // 2
    vreme = pygame.time.get_ticks()
    puls = int(4 * abs((vreme % 1000) / 500 - 1))
    radius = SQUARE_SIZE // 2 - 5 + puls

    pygame.draw.circle(prozor, LIGHT_GOLD, (x, y), radius, 3)
    pygame.draw.circle(prozor, GOLD, (x, y), radius - 6, 2)


def nacrtaj_kraj_igre(prozor, pobednik, nereseno=False):
    if pobednik is None and not nereseno:
        return

    prozor.fill(BROWN)

    naslov_font = pygame.font.SysFont("arial", 54, bold=True)
    dugme_font = pygame.font.SysFont("arial", 28, bold=True)

    if nereseno:
        tekst = "Nereseno"
    else:
        tekst = "Ti si pobedio" if pobednik == WHITE else "Izgubio si"
    naslov = naslov_font.render(tekst, True, BEIGE)
    naslov_rect = naslov.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 45))
    prozor.blit(naslov, naslov_rect)

    pygame.draw.rect(prozor, BEIGE, IGRAJ_OPET_RECT, border_radius=8)
    pygame.draw.rect(prozor, GOLD, IGRAJ_OPET_RECT, 3, border_radius=8)

    dugme = dugme_font.render("Igraj opet", True, BROWN)
    dugme_rect = dugme.get_rect(center=IGRAJ_OPET_RECT.center)
    prozor.blit(dugme, dugme_rect)


def klik_na_igraj_opet(pos):
    return IGRAJ_OPET_RECT.collidepoint(pos)
