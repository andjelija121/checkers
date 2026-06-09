from konstante import ROWS, COLS, WHITE, BLACK
from figura import Figura
import pravila
import pygame
from strukture.stek import Stek
from strukture.UndoPotez import UndoZapis
from strukture.potez import Potez


class Tabla:
    def __init__(self):
        self.tabla = [None] * 32
        self.stek =  Stek()
        self.izabrana_figura = None
        self.animacija_jedenja = []
        self.animacija_undo = []
        self.animacije_ukljucene = True
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

            figura_indeks = self.red_kolona_u_indeks(self.izabrana_figura.row,self.izabrana_figura.col)
            potez = Potez(self.izabrana_figura,figura_indeks,indeks,pojedeni)
            pomereno = self.odigraj_potez(potez)
            
            if pomereno:
                self.izabrana_figura = None

            return pomereno

        return False

    def odigraj_potez(self, potez):
        pojedene_figure=[]
        for p in potez.pojedeni:
            pojedene_figure.append(self.tabla[p])

        self.stek.push(UndoZapis(potez,pojedene_figure,potez.figura.kraljevic,self.br))

        red, kolona = self.indeks_u_red_kolonu(potez.krajnji_indeks)
        return self.pomeri(potez.figura, red, kolona, potez.pojedeni)

    def undo_potez(self):
        undo = self.stek.pop()
        if undo is None:
            return False

        potez = undo.potez
        figura = self.tabla[potez.krajnji_indeks]
        if figura is None:
            return False

        red, kolona = self.indeks_u_red_kolonu(potez.pocetni_indeks)
        figura.row = red
        figura.col = kolona

        self.tabla[potez.pocetni_indeks]=figura
        self.tabla[potez.krajnji_indeks] = None

        for pf in undo.pojedene_figure:
            red=pf.row
            kol = pf.col
            novi_indeks = self.red_kolona_u_indeks(red,kol)
            self.tabla[novi_indeks]=pf
        
        if not undo.figura_bila_kraljevic:
            self.tabla[potez.pocetni_indeks].kraljevic = False

        if self.animacije_ukljucene:
            sada = pygame.time.get_ticks()
            self.animacija_undo = [
                ("potez", potez.krajnji_indeks, potez.pocetni_indeks, figura.color, figura.kraljevic, sada)
            ]

            for i, pf in enumerate(undo.pojedene_figure):
                indeks = self.red_kolona_u_indeks(pf.row,pf.col)
                self.animacija_undo.append(("figura", indeks, indeks, pf.color, pf.kraljevic, sada + 120 + i * 90))
        else:
            self.animacija_undo = []
        
        self.br = undo.br_pre
        self.izabrana_figura = None
        self.animacija_jedenja=[]

        return True


    def pomeri(self, figura, red, kolona, pojedeni=None):
        if pojedeni is None:
            pojedeni = []
        if self.animacije_ukljucene:
            sada = pygame.time.get_ticks()
            self.animacija_jedenja = []

            for i, p in enumerate(pojedeni):
                pojedena_figura = self.tabla[p]

                if pojedena_figura is not None:
                    self.animacija_jedenja.append((
                        p,
                        pojedena_figura.color,
                        pojedena_figura.kraljevic,
                        sada + i * 260
                    ))
        else:
            self.animacija_jedenja = []
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
