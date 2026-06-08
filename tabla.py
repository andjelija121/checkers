from konstante import ROWS, COLS, WHITE, BLACK
from figura import Figura
import pravila
import pygame


class Tabla:
    def __init__(self):
        self.tabla = [None] * 32
        self.izabrana_figura = None
        self.animacija_jedenja = []
        self.br=0
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

    def napravi_tablu(self):
        for red in range(ROWS):
            for kolona in range(COLS):
                if (red + kolona) % 2 == 1:
                    indeks = self.red_kolona_u_indeks(red, kolona)

                    if red < 3:
                        self.tabla[indeks] = Figura(red, kolona, BLACK)
                    elif red > 4:
                        self.tabla[indeks] = Figura(red, kolona, WHITE)

    def uzmi_figuru(self, red, kolona):
        indeks = self.red_kolona_u_indeks(red, kolona)

        if indeks is None:
            return None

        return self.tabla[indeks]

    def izaberi(self, red, kolona):

        indeks = self.red_kolona_u_indeks(red, kolona)
        figura = self.uzmi_figuru(red, kolona)

        if self.izabrana_figura is not None and  figura == self.izabrana_figura:
            self.izabrana_figura = None
            return False

        if figura is not None and figura.color == WHITE:
            self.izabrana_figura = figura
            return True

        if self.izabrana_figura is not None and indeks is not None:
            validni,pojedeni_po_skoku = pravila.validni_potezi(self, self.izabrana_figura)

            if indeks not in validni:
                return False
            pojedeni = pojedeni_po_skoku.get(indeks, [])
            pomereno = self.pomeri(self.izabrana_figura, red, kolona, pojedeni)
            
            if pomereno:
                self.izabrana_figura = None

            return pomereno

        return False

    def pomeri(self, figura, red, kolona, pojedeni=None):
        if pojedeni is None:
            pojedeni = []
        sada = pygame.time.get_ticks()
        self.animacija_jedenja = [(p, sada + i * 180) for i, p in enumerate(pojedeni)]
        self.br+=1
        indeks = self.red_kolona_u_indeks(figura.row,figura.col)
        self.tabla[indeks] = None
        novi_indeks =self.red_kolona_u_indeks(red,kolona)
        self.tabla[novi_indeks]=figura
        figura.row=red
        figura.col=kolona
        for p in pojedeni:
            self.br=0
            self.tabla[p] = None
        if red==0 or red==ROWS-1:
            figura.postani_kraljevic()
        return True
