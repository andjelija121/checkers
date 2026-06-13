import random
import pygame
from math import inf

from strukture.figura import Figura
from konstante import BLACK, WHITE
from pravila import svi_potezi
from tabla import Tabla

class Ai:
    def __init__(self):
        self.transposition_table = {}
        self.zobrist = self.napravi_zobrist_tabelu()

    def ai_potez(self,tabla):
        self.transposition_table = {}

        pocetak = pygame.time.get_ticks()
        limit = 3000
        potezi = self.sortiraj_poteze(tabla, svi_potezi(tabla, BLACK))
        najbolji_potez = potezi[0] if potezi else None

        dubina = 1

        while pygame.time.get_ticks() - pocetak < limit:
            najbolja_ocena_za_dubinu = -inf
            najbolji_potez_za_dubinu = None

            try:
                for potez in potezi:
                    nova_tabla,lanac = self.odigraj_na_kopiji_table(tabla,potez)
                    ocena = self.minimax(nova_tabla,dubina,-inf,+inf,False,pocetak,limit)
                    
                    if ocena>najbolja_ocena_za_dubinu:
                        najbolja_ocena_za_dubinu = ocena
                        najbolji_potez_za_dubinu = potez
            except TimeoutError:
                break

            if najbolji_potez_za_dubinu is not None:
                najbolji_potez = najbolji_potez_za_dubinu
                potezi.remove(najbolji_potez)
                potezi.insert(0, najbolji_potez)

            dubina += 1
        
        if najbolji_potez is None:
            return

        tabla.odigraj_potez(najbolji_potez)

        return najbolji_potez

    def napravi_zobrist_tabelu(self):
        random.seed(1)
        tabela = []

        for indeks in range(32):
            tabela.append({
                "BLACK": random.getrandbits(64),
                "BLACK_KRALJEVIC": random.getrandbits(64),
                "WHITE": random.getrandbits(64),
                "WHITE_KRALJEVIC": random.getrandbits(64),
            })

        return tabela

    def zobrist_hash(self, tabla):
        h = 0

        for indeks, figura in enumerate(tabla.tabla):
            if figura is None:
                continue

            if figura.color == BLACK:
                tip = "BLACK_KRALJEVIC" if figura.kraljevic else "BLACK"
            else:
                tip = "WHITE_KRALJEVIC" if figura.kraljevic else "WHITE"

            h ^= self.zobrist[indeks][tip]

        return h

    def kljuc_stanja(self, tabla):
        detalji_figura = []

        for indeks, figura in enumerate(tabla.tabla):
            if figura is None:
                continue

            detalji_figura.append((
                indeks,
                figura.color,
                figura.kraljevic,
                figura.marko,
                tuple(sorted(relikvija.kljuc for relikvija in figura.relikvije)),
                figura.oklop,
                figura.kolebanje
            ))

        return self.zobrist_hash(tabla), tuple(detalji_figura)

    def evaluacijatest(self, tabla):
        return 0

    def evaluacija(self, tabla):
        score = 0

        for i, figura in enumerate(tabla.tabla):
            if figura is None:
                continue

            red, kolona = tabla.indeks_u_red_kolonu(i)
            vrednost = 3 if not figura.kraljevic else 5

            if not figura.kraljevic:
                if figura.color == BLACK:
                    vrednost += red * 0.1
                else:
                    vrednost += (7 - red) * 0.1


            if kolona == 0 or kolona == 7:
                vrednost += 0.5


            if 2 <= kolona <= 5:
                vrednost += 0.3

            if figura.color == BLACK:
                score += vrednost
            else:
                score -= vrednost

        black_potezi_lista = svi_potezi(tabla, BLACK)
        white_potezi_lista = svi_potezi(tabla, WHITE)
        black_potezi = len(black_potezi_lista)
        white_potezi = len(white_potezi_lista)
        score += (black_potezi - white_potezi) * 0.05


        black_jedenja = sum(len(p.pojedeni) for p in black_potezi_lista if p.pojedeni)
        white_jedenja = sum(len(p.pojedeni) for p in white_potezi_lista if p.pojedeni)
        score += (black_jedenja - white_jedenja) * 1.4

        najveca_black_prilika = self.najveca_vrednost_jedenja(tabla, black_potezi_lista)
        najveca_white_prilika = self.najveca_vrednost_jedenja(tabla, white_potezi_lista)
        score += najveca_black_prilika * 0.8
        score -= najveca_white_prilika * 2.2

        return score

    def vrednost_figure(self, figura):
        if figura is None:
            return 0

        return 5 if figura.kraljevic else 3

    def sortiraj_poteze(self, tabla, potezi):
        return sorted(
            potezi,
            key=lambda potez: self.ocena_redosleda_poteza(tabla, potez),
            reverse=True
        )

    def ocena_redosleda_poteza(self, tabla, potez):
        ocena = 0

        for indeks in potez.pojedeni:
            ocena += self.vrednost_figure(tabla.tabla[indeks]) * 100

        krajnji_red, krajnja_kolona = tabla.indeks_u_red_kolonu(potez.krajnji_indeks)

        if not potez.figura.kraljevic:
            promocija = (
                potez.figura.color == BLACK and krajnji_red == 7
                or potez.figura.color == WHITE and krajnji_red == 0
            )
            if promocija:
                ocena += 80

        udaljenost_od_centra = abs(3.5 - krajnji_red) + abs(3.5 - krajnja_kolona)
        ocena += 7 - udaljenost_od_centra

        return ocena

    def najveca_vrednost_jedenja(self, tabla, potezi):
        najbolja = 0

        for potez in potezi:
            vrednost = 0

            for indeks in potez.pojedeni:
                vrednost += self.vrednost_figure(tabla.tabla[indeks])

            najbolja = max(najbolja, vrednost)

        return najbolja

    def odigraj_na_kopiji_table(self,tabla,potez):
        nova_tabla = self.kopija_table(tabla)
        novi_red,nova_kolona = tabla.indeks_u_red_kolonu(potez.krajnji_indeks)
        nova_figura = nova_tabla.tabla[potez.pocetni_indeks]

        nova_tabla.pomeri(nova_figura,novi_red,nova_kolona,potez.pojedeni)
        nova_figura = nova_tabla.tabla[potez.krajnji_indeks]

        lanac=False

        for sledeci in svi_potezi(nova_tabla,nova_figura.color):
            if sledeci.figura==nova_figura and sledeci.pojedeni:
                lanac=True
        return nova_tabla,lanac
    
    def kopija_table(self,tabla):
        nova = Tabla.__new__(Tabla)
        nova.tabla = [None] * 32
        nova.izabrana_figura = None
        nova.animacija_jedenja = []
        nova.animacije_ukljucene = False
        nova.br = tabla.br
        for i,f in enumerate(tabla.tabla):
            if f is not None:
                nova_figura = Figura(f.row,f.col,f.color)
                nova_figura.kraljevic = f.kraljevic
                nova_figura.marko = f.marko
                nova_figura.relikvije = list(f.relikvije)
                nova_figura.oklop = f.oklop
                nova_figura.kolebanje = f.kolebanje
                nova.tabla[i] = nova_figura
        return nova


    def minimax(self,tabla,dubina,alfa,beta,maxFigura,pocetak,limit):
        if pygame.time.get_ticks() - pocetak >= limit:
            raise TimeoutError

        kljuc = (self.kljuc_stanja(tabla),dubina,maxFigura)

        if kljuc in self.transposition_table:
            return self.transposition_table[kljuc]

        if dubina ==0:
            rezultat = self.evaluacijatest(tabla)
            self.transposition_table[kljuc] = rezultat
            return rezultat
        else:
            if maxFigura:
                potezi = self.sortiraj_poteze(tabla, svi_potezi(tabla, BLACK))
                if not potezi:
                    rezultat = self.evaluacijatest(tabla)
                    self.transposition_table[kljuc] = rezultat
                    return rezultat
                maximum = -inf
                preseceno = False
                
                for potez in potezi:
                    nova_tabla,lanac = self.odigraj_na_kopiji_table(tabla,potez)
                    ocena = self.minimax(nova_tabla,dubina-1,alfa,beta,False,pocetak,limit)
                    maximum = max(ocena,maximum)
                    alfa = max(alfa, ocena)
                    if alfa >= beta:
                        preseceno = True
                        break
                if not preseceno:
                    self.transposition_table[kljuc] = maximum
                return maximum
            else:
                potezi = self.sortiraj_poteze(tabla, svi_potezi(tabla, WHITE))
                if not potezi:
                    rezultat = self.evaluacijatest(tabla)
                    self.transposition_table[kljuc] = rezultat
                    return rezultat
                minimum = inf
                preseceno = False

                for potez in potezi:
                    nova_tabla,lanac = self.odigraj_na_kopiji_table(tabla,potez)
                    ocena = self.minimax(nova_tabla,dubina-1,alfa,beta,True,pocetak,limit)
                    beta =min(beta,ocena)
                    minimum = min(ocena,minimum)
                    if beta<=alfa:
                        preseceno = True
                        break
                if not preseceno:
                    self.transposition_table[kljuc] = minimum
                return minimum
