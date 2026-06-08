import pygame

from pravila import svi_potezi, validni_potezi
from tabla import Tabla
from konstante import WHITE, BLACK
from ai import Ai


class Igra:
    def __init__(self):
        self.tabla = Tabla()
        self.na_potezu = WHITE
        self.ai = Ai()
        self.ai_ceka_do = None
        self.obavezna_figura=None
        self.pobednik = None
        self.nereseno = False

    def resetuj(self):
        self.tabla = Tabla()
        self.na_potezu = WHITE
        self.ai_ceka_do = None
        self.obavezna_figura = None
        self.pobednik = None
        self.nereseno = False

    def jedan_potez(self, red, kolona):
        if self.pobednik is not None or self.nereseno:
            return

        indeks = self.tabla.red_kolona_u_indeks(red,kolona)
        if self.na_potezu != WHITE:
            return

        if self.obavezna_figura is  None:
            odigrano = self.tabla.izaberi(red, kolona)
        elif indeks is not None and self.tabla.tabla[indeks] is None:
            odigrano = self.tabla.izaberi(red,kolona)
            self.obavezna_figura = None
        else:
            return False

        if odigrano and self.tabla.izabrana_figura is None:
            self.proveri_nereseno()
            if self.nereseno:
                return

            self.na_potezu = BLACK
            self.ai_ceka_do = pygame.time.get_ticks() +500

    def update(self):
        if self.pobednik is not None or self.nereseno:
            return

        if self.na_potezu != BLACK:
            return

        if pygame.time.get_ticks() < self.ai_ceka_do:
            return

        potezi = svi_potezi(self.tabla, BLACK)

        if not potezi:
            self.pobednik = WHITE
            self.na_potezu = None
            self.ai_ceka_do = None
            return

        self.ai.ai_potez(self.tabla)
        self.zavrsi_ai_potez()

    def zavrsi_ai_potez(self):
        self.proveri_nereseno()
        if self.nereseno:
            self.na_potezu = None
            self.ai_ceka_do = None
            return

        self.na_potezu = WHITE
        self.ai_ceka_do = None

        for potez in svi_potezi(self.tabla, WHITE):
            if potez.pojedeni:
                self.tabla.izabrana_figura = potez.figura
                self.obavezna_figura = potez.figura


    def proveri_nereseno(self):
        if self.tabla.br >= 40:
            self.nereseno = True
            self.na_potezu = None
            self.ai_ceka_do = None
