import pygame
from konstante import ROWS, COLS, SQUARE_SIZE, BROWN, BEIGE, WHITE, BLACK, GREEN, GOLD, LIGHT_GOLD
from figura import Figura


class Tabla:
    def __init__(self):
        self.tabla = [None] * 32
        self.izabrana_figura = None
        self.napravi_tablu()

    def red_kolona_u_indeks(self, red, kolona):
        if red < 0 or red >= ROWS or kolona < 0 or kolona >= COLS:
            return None

        if (red + kolona) % 2 == 0:
            return None

        return red * 4 + kolona // 2

    def indeks_u_red_kolonu(self, indeks):
        red = indeks // 4
        pozicija_u_redu = indeks % 4

        if red % 2 == 0:
            kolona = pozicija_u_redu * 2 + 1
        else:
            kolona = pozicija_u_redu * 2

        return red, kolona

    def nacrtaj_polja(self, prozor):
        prozor.fill(BEIGE)

        for red in range(ROWS):
            for kolona in range(COLS):
                if (red + kolona) % 2 == 1:
                    pygame.draw.rect(
                        prozor,
                        BROWN,
                        (kolona * SQUARE_SIZE, red * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                    )

    def napravi_tablu(self):
        for red in range(ROWS):
            for kolona in range(COLS):
                if (red + kolona) % 2 == 1:
                    indeks = self.red_kolona_u_indeks(red, kolona)

                    if red < 3:
                        self.tabla[indeks] = Figura(red, kolona, BLACK)
                    elif red > 4:
                        self.tabla[indeks] = Figura(red, kolona, WHITE)

    def nacrtaj(self, prozor):
        self.nacrtaj_polja(prozor)
        self.nacrtaj_validne_poteze(prozor)

        for figura in self.tabla:
            if figura is not None:
                figura.nacrtaj(prozor)

        self.nacrtaj_izabranu_figuru(prozor)

    def nacrtaj_validne_poteze(self, prozor):
        if self.izabrana_figura is None:
            return

        vreme = pygame.time.get_ticks()
        puls = int(3 + 2 * abs((vreme % 900) / 450 - 1))

        for indeks in self.validni_potezi(self.izabrana_figura):
            red, kolona = self.indeks_u_red_kolonu(indeks)
            x = kolona * SQUARE_SIZE + SQUARE_SIZE // 2
            y = red * SQUARE_SIZE + SQUARE_SIZE // 2

            pygame.draw.circle(prozor, LIGHT_GOLD, (x, y), 18 + puls, 3)
            pygame.draw.circle(prozor, GOLD, (x, y), 7)

    def nacrtaj_izabranu_figuru(self, prozor):
        if self.izabrana_figura is None:
            return

        x = self.izabrana_figura.col * SQUARE_SIZE + SQUARE_SIZE // 2
        y = self.izabrana_figura.row * SQUARE_SIZE + SQUARE_SIZE // 2
        vreme = pygame.time.get_ticks()
        puls = int(4 * abs((vreme % 1000) / 500 - 1))
        radius = SQUARE_SIZE // 2 - 5 + puls

        pygame.draw.circle(prozor, LIGHT_GOLD, (x, y), radius, 3)
        pygame.draw.circle(prozor, GOLD, (x, y), radius - 6, 2)

    def uzmi_figuru(self, red, kolona):
        indeks = self.red_kolona_u_indeks(red, kolona)

        if indeks is None:
            return None

        return self.tabla[indeks]

    def izaberi(self, red, kolona):
        indeks = self.red_kolona_u_indeks(red, kolona)
        figura = self.uzmi_figuru(red, kolona)

        if figura == self.izabrana_figura:
            self.izabrana_figura = None
            return True

        if figura is not None:
            self.izabrana_figura = figura
            return True

        if self.izabrana_figura is not None and indeks is not None:

            if indeks not in self.validni_potezi(self.izabrana_figura):
                return False

            pomereno = self.pomeri(self.izabrana_figura, red, kolona)

            if pomereno:
                self.izabrana_figura = None

            return pomereno

        return False

    def validni_potezi(self,figura):
        validni=[]
        if figura is None:
            return False
        
        red =figura.row
        kolona=figura.col

        if figura.color == WHITE:
            smerovi = [(-1,-1),(-1,1)]
        if figura.color == BLACK:
            smerovi = [(1,-1),(1,1)]
        if figura.kraljevic:
            smerovi = [(-1,-1),(-1,1),(1,-1),(1,1)]
        
        for red_smer,kolona_smer in smerovi:
            novi_red= red_smer+red
            nova_kolona= kolona_smer+kolona
            novi_indeks = self.red_kolona_u_indeks(novi_red,nova_kolona)
            if novi_indeks is not None and self.tabla[novi_indeks] is None:
                validni.append(novi_indeks)
            else:
                continue
        return validni

    def pomeri(self,figura,red,kolona):
        indeks = self.red_kolona_u_indeks(figura.row,figura.col)
        self.tabla[indeks] = None
        novi_indeks =self.red_kolona_u_indeks(red,kolona)
        self.tabla[novi_indeks]=figura
        figura.row=red
        figura.col=kolona
        if red==0:
            figura.postani_kraljevic()
        return True
