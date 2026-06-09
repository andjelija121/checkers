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

    nacrtaj_animaciju_jedenja(tabla, prozor)
    nacrtaj_animaciju_undo(tabla, prozor)
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


def nacrtaj_animaciju_jedenja(tabla, prozor):
    vreme = pygame.time.get_ticks()
    aktivne = []

    for indeks, boja, kraljevic, pocetak in tabla.animacija_jedenja:
        proslo = vreme - pocetak

        if proslo < 0:
            aktivne.append((indeks, boja, kraljevic, pocetak))
            continue

        if proslo > 520:
            continue

        aktivne.append((indeks, boja, kraljevic, pocetak))
        red, kolona = tabla.indeks_u_red_kolonu(indeks)
        x = kolona * SQUARE_SIZE + SQUARE_SIZE // 2
        y = red * SQUARE_SIZE + SQUARE_SIZE // 2
        radius = SQUARE_SIZE // 2 - 10 + proslo // 30
        alpha = max(0, 230 - proslo // 2)

        efekat = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        centar = (SQUARE_SIZE // 2, SQUARE_SIZE // 2)
        pygame.draw.circle(efekat, (0, 0, 0, alpha // 3), (centar[0], centar[1] + 5), radius)
        pygame.draw.circle(efekat, (*boja, alpha), centar, radius)
        pygame.draw.circle(efekat, (*GOLD, alpha), centar, radius, 4)

        if kraljevic:
            pygame.draw.circle(efekat, (*LIGHT_GOLD, alpha), centar, radius // 2, 3)

        prozor.blit(efekat, (x - SQUARE_SIZE // 2, y - SQUARE_SIZE // 2))

    tabla.animacija_jedenja = aktivne


def nacrtaj_animaciju_undo(tabla, prozor):
    if not hasattr(tabla, "animacija_undo"):
        return

    vreme = pygame.time.get_ticks()
    aktivne = []

    for tip, od_indeksa, do_indeksa, boja, kraljevic, pocetak in tabla.animacija_undo:
        proslo = vreme - pocetak

        if proslo < 0:
            aktivne.append((tip, od_indeksa, do_indeksa, boja, kraljevic, pocetak))
            continue

        if proslo > 420:
            continue

        aktivne.append((tip, od_indeksa, do_indeksa, boja, kraljevic, pocetak))

        if tip == "potez":
            napredak = min(1, proslo / 420)
            red_od, kolona_od = tabla.indeks_u_red_kolonu(od_indeksa)
            red_do, kolona_do = tabla.indeks_u_red_kolonu(do_indeksa)

            x_od = kolona_od * SQUARE_SIZE + SQUARE_SIZE // 2
            y_od = red_od * SQUARE_SIZE + SQUARE_SIZE // 2
            x_do = kolona_do * SQUARE_SIZE + SQUARE_SIZE // 2
            y_do = red_do * SQUARE_SIZE + SQUARE_SIZE // 2

            x = x_od + (x_do - x_od) * napredak
            y = y_od + (y_do - y_od) * napredak
            radius = SQUARE_SIZE // 2 - 12
            alpha = max(0, 180 - int(proslo / 3))
        else:
            red, kolona = tabla.indeks_u_red_kolonu(do_indeksa)
            x = kolona * SQUARE_SIZE + SQUARE_SIZE // 2
            y = red * SQUARE_SIZE + SQUARE_SIZE // 2
            radius = SQUARE_SIZE // 2 - 18 + proslo // 24
            alpha = min(210, 70 + proslo // 2)

        efekat = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        centar = (SQUARE_SIZE // 2, SQUARE_SIZE // 2)
        pygame.draw.circle(efekat, (0, 0, 0, alpha // 4), (centar[0], centar[1] + 5), radius)
        pygame.draw.circle(efekat, (*boja, alpha), centar, radius)
        pygame.draw.circle(efekat, (*LIGHT_GOLD, alpha), centar, radius, 4)

        if kraljevic:
            pygame.draw.circle(efekat, (*GOLD, alpha), centar, radius // 2, 3)

        prozor.blit(efekat, (x - SQUARE_SIZE // 2, y - SQUARE_SIZE // 2))

    tabla.animacija_undo = aktivne


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
