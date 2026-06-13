import pygame
from konstante import (
    ROWS, COLS, SQUARE_SIZE, BROWN, BEIGE, GOLD, LIGHT_GOLD,
    WIDTH, HEIGHT, TABLA_VISINA, PANEL_VISINA, WHITE
)
import pravila


IGRAJ_OPET_RECT = pygame.Rect(WIDTH // 2 - 95, HEIGHT // 2 + 45, 190, 52)
POCETAK_DRUMA_RECT = pygame.Rect(WIDTH // 2 - 285, TABLA_VISINA // 2 - 35, 250, 145)
KRAJ_DRUMA_RECT = pygame.Rect(WIDTH // 2 + 35, TABLA_VISINA // 2 - 35, 250, 145)
BRAZDE = {(3, 0), (4, 7)}


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

                if (red, kolona) in BRAZDE:
                    nacrtaj_brazdu(prozor, red, kolona)


def nacrtaj_brazdu(prozor, red, kolona):
    x = kolona * SQUARE_SIZE
    y = red * SQUARE_SIZE
    okvir = pygame.Rect(x + 5, y + 5, SQUARE_SIZE - 10, SQUARE_SIZE - 10)

    pygame.draw.rect(prozor, (105, 67, 39), okvir, border_radius=8)
    pygame.draw.rect(prozor, GOLD, okvir, 3, border_radius=8)

    for pomeraj in (22, 40, 58, 76):
        pygame.draw.line(
            prozor,
            (67, 40, 25),
            (x + pomeraj - 12, y + 13),
            (x + pomeraj + 8, y + SQUARE_SIZE - 13),
            4,
        )

    font = pygame.font.SysFont("arial", 16, bold=True)
    tekst = font.render("БРАЗДА", True, (255, 226, 140))
    prozor.blit(tekst, tekst.get_rect(center=(x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2)))


def nacrtaj(igra, prozor):
    tabla = igra.tabla
    nacrtaj_polja(tabla, prozor)
    nacrtaj_validne_poteze(igra, prozor)

    for figura in tabla.tabla:
        if figura is not None:
            figura.nacrtaj(prozor)

    nacrtaj_zauzeta_validna_odredista(igra, prozor)
    nacrtaj_animaciju_jedenja(tabla, prozor)
    nacrtaj_animaciju_undo(tabla, prozor)
    nacrtaj_izabranu_figuru(tabla, prozor)
    nacrtaj_carev_drum(igra, prozor)
    nacrtaj_poruku_relikvije(igra, prozor)

    if igra.ceka_izbor_relikvije is not None:
        nacrtaj_izbor_relikvije(igra, prozor)


def naziv_relikvije(relikvija):
    return getattr(relikvija, "naziv", str(relikvija))


def opis_relikvije(relikvija):
    return getattr(relikvija, "opis", "")


def nacrtaj_carev_drum(igra, prozor):
    relikvije = igra.carev_drum.sadrzaj()
    panel = pygame.Rect(0, TABLA_VISINA, WIDTH, PANEL_VISINA)
    pygame.draw.rect(prozor, (48, 31, 24), panel)
    pygame.draw.line(prozor, GOLD, (0, TABLA_VISINA), (WIDTH, TABLA_VISINA), 4)

    font = pygame.font.SysFont("arial", 18, bold=True)
    naslov = font.render("ЦАРЕВ ДРУМ", True, (255, 226, 140))
    prozor.blit(naslov, (22, TABLA_VISINA + 18))

    if not relikvije:
        return

    x = 165
    sirina = 116
    for relikvija in relikvije:
        rect = pygame.Rect(x, TABLA_VISINA + 13, sirina, 48)
        pygame.draw.rect(prozor, (239, 225, 194), rect, border_radius=6)
        pygame.draw.rect(prozor, relikvija.boja, rect, 3, border_radius=6)
        tekst = pygame.font.SysFont("arial", 12, bold=True).render(
            naziv_relikvije(relikvija), True, (57, 38, 29)
        )
        prozor.blit(tekst, tekst.get_rect(center=rect.center))
        x += sirina + 6

def nacrtaj_izbor_relikvije(igra, prozor):
    zatamnjenje = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    zatamnjenje.fill((20, 12, 8, 185))
    prozor.blit(zatamnjenje, (0, 0))

    panel = pygame.Rect(WIDTH // 2 - 330, TABLA_VISINA // 2 - 150, 660, 315)
    pygame.draw.rect(prozor, (66, 43, 31), panel, border_radius=18)
    pygame.draw.rect(prozor, GOLD, panel, 4, border_radius=18)

    naslov_font = pygame.font.SysFont("arial", 29, bold=True)
    tekst_font = pygame.font.SysFont("arial", 18, bold=True)
    mali_font = pygame.font.SysFont("arial", 14)

    naslov = naslov_font.render("СТАО СИ НА БРАЗДУ", True, (255, 226, 140))
    prozor.blit(naslov, naslov.get_rect(center=(WIDTH // 2, panel.top + 38)))
    uputstvo = mali_font.render(
        "Изабери реликвију са почетка или краја Царевог друма", True, BEIGE
    )
    prozor.blit(uputstvo, uputstvo.get_rect(center=(WIDTH // 2, panel.top + 72)))

    nacrtaj_kartu(
        prozor, POCETAK_DRUMA_RECT, igra.carev_drum.prvi(),
        "ПОЧЕТАК ДРУМА", tekst_font, mali_font
    )
    nacrtaj_kartu(
        prozor, KRAJ_DRUMA_RECT, igra.carev_drum.poslednji(),
        "КРАЈ ДРУМА", tekst_font, mali_font
    )


def nacrtaj_kartu(prozor, rect, relikvija, strana, tekst_font, mali_font):
    pygame.draw.rect(prozor, (245, 233, 205), rect, border_radius=12)
    pygame.draw.rect(prozor, GOLD, rect, 4, border_radius=12)

    strana_tekst = mali_font.render(strana, True, (105, 70, 45))
    naziv = tekst_font.render(naziv_relikvije(relikvija), True, (50, 33, 27))
    opis = mali_font.render(opis_relikvije(relikvija), True, (139, 94, 60))
    klik = mali_font.render("КЛИКНИ ЗА ИЗБОР", True, (105, 70, 45))

    prozor.blit(strana_tekst, strana_tekst.get_rect(center=(rect.centerx, rect.top + 25)))
    prozor.blit(naziv, naziv.get_rect(center=(rect.centerx, rect.top + 62)))
    prozor.blit(opis, opis.get_rect(center=(rect.centerx, rect.top + 94)))
    prozor.blit(klik, klik.get_rect(center=(rect.centerx, rect.bottom - 18)))


def nacrtaj_poruku_relikvije(igra, prozor):
    if igra.poslednja_relikvija is None:
        return
    if pygame.time.get_ticks() > igra.poruka_relikvije_do:
        return

    figura, relikvija = igra.poslednja_relikvija
    rect = pygame.Rect(WIDTH // 2 - 210, HEIGHT - 72, 420, 50)
    pygame.draw.rect(prozor, (55, 38, 28), rect, border_radius=10)
    pygame.draw.rect(prozor, GOLD, rect, 3, border_radius=10)

    tekst = pygame.font.SysFont("arial", 19, bold=True).render(
        "Добијена реликвија: " + naziv_relikvije(relikvija), True, (255, 232, 170)
    )
    prozor.blit(tekst, tekst.get_rect(center=rect.center))

    x = figura.col * SQUARE_SIZE + SQUARE_SIZE // 2
    y = figura.row * SQUARE_SIZE + SQUARE_SIZE // 2
    puls = 48 + int(5 * abs((pygame.time.get_ticks() % 600) / 300 - 1))
    pygame.draw.circle(prozor, GOLD, (x, y), puls, 4)


def klik_na_izbor_relikvije(pos):
    if POCETAK_DRUMA_RECT.collidepoint(pos):
        return "pocetak"
    if KRAJ_DRUMA_RECT.collidepoint(pos):
        return "kraj"
    return None


def nacrtaj_validne_poteze(igra, prozor):
    tabla = igra.tabla
    vreme = pygame.time.get_ticks()
    puls = int(3 + 2 * abs((vreme % 900) / 450 - 1))

    if igra.obavezni_potezi_po_odredistu and tabla.izabrana_figura is None:
        validni = list(igra.obavezni_potezi_po_odredistu.keys())

        for figura in igra.figure_koje_moraju_da_jedu:
            x = figura.col * SQUARE_SIZE + SQUARE_SIZE // 2
            y = figura.row * SQUARE_SIZE + SQUARE_SIZE // 2
            pygame.draw.circle(prozor, (255, 238, 150), (x, y), SQUARE_SIZE // 2 - 4 + puls, 4)
    elif tabla.izabrana_figura is not None:
        validni, *_ = pravila.validni_potezi(tabla, tabla.izabrana_figura)
    else:
        return

    for indeks in validni:
        if tabla.tabla[indeks] is not None:
            continue

        red, kolona = tabla.indeks_u_red_kolonu(indeks)
        x = kolona * SQUARE_SIZE + SQUARE_SIZE // 2
        y = red * SQUARE_SIZE + SQUARE_SIZE // 2

        pygame.draw.circle(prozor, LIGHT_GOLD, (x, y), 20 + puls, 4)
        pygame.draw.circle(prozor, GOLD, (x, y), 8)


def nacrtaj_zauzeta_validna_odredista(igra, prozor):
    tabla = igra.tabla

    if igra.obavezni_potezi_po_odredistu and tabla.izabrana_figura is None:
        validni = list(igra.obavezni_potezi_po_odredistu.keys())
    elif tabla.izabrana_figura is not None:
        validni, *_ = pravila.validni_potezi(tabla, tabla.izabrana_figura)
    else:
        return

    vreme = pygame.time.get_ticks()
    puls = int(2 + 2 * abs((vreme % 900) / 450 - 1))

    for indeks in validni:
        if tabla.tabla[indeks] is None:
            continue

        red, kolona = tabla.indeks_u_red_kolonu(indeks)
        x = kolona * SQUARE_SIZE + SQUARE_SIZE // 2
        y = red * SQUARE_SIZE + SQUARE_SIZE // 2
        radius = SQUARE_SIZE // 2 - 5 + puls

        pygame.draw.circle(prozor, LIGHT_GOLD, (x, y), radius, 5)
        pygame.draw.circle(prozor, GOLD, (x, y), radius - 7, 3)


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
        tekst = "Нерешено"
    else:
        tekst = "Победио си" if pobednik == WHITE else "Изгубио си"
    naslov = naslov_font.render(tekst, True, BEIGE)
    naslov_rect = naslov.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 45))
    prozor.blit(naslov, naslov_rect)

    pygame.draw.rect(prozor, BEIGE, IGRAJ_OPET_RECT, border_radius=8)
    pygame.draw.rect(prozor, GOLD, IGRAJ_OPET_RECT, 3, border_radius=8)

    dugme = dugme_font.render("Играј опет", True, BROWN)
    dugme_rect = dugme.get_rect(center=IGRAJ_OPET_RECT.center)
    prozor.blit(dugme, dugme_rect)


def klik_na_igraj_opet(pos):
    return IGRAJ_OPET_RECT.collidepoint(pos)
