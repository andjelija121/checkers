import random
import pygame
from math import inf

from strukture.figura import Figura
from konstante import BLACK, WHITE
from pravila import svi_potezi
from tabla import Tabla

class Ai:
    LIMIT_PRETRAGE_MS = 1800
    LIMIT_KRATKOG_JEDENJA_MS = 500
    OBICNA_FIGURA = 3.0
    KRALJEVIC = 5.5
    MARKO = 4.0
    OKLOP_PO_POTEZU = 1.25
    KOLEBANJE_PO_POTEZU = 0.9
    NAPREDOVANJE = 0.12
    IVICA = 0.28
    UGAO = 0.55
    CENTAR = 0.22
    BRAZDA = 0.65
    MOBILNOST = 0.06
    DOSTUPNO_JEDENJE = 0.35
    NAJBOLJE_JEDENJE = 0.75
    POBEDA = 10000

    VREDNOST_RELIKVIJE = {
        "topuz": 1.15,
        "sarac": 0.85,
        "toka": 0.25,
        "mesina": 0.25,
        "blago": 1.50,
    }

    MARKOVE_RELIKVIJE = {"mesina", "topuz", "sarac"}
    BRAZDE = {(3, 0), (4, 7)}
    UGLOVI = {(0, 7), (7, 0)}

    def __init__(self):
        self.transposition_table = {}
        self.zobrist = self.napravi_zobrist_tabelu()

    def ai_potez(self,tabla):
        self.transposition_table = {}

        pocetak = pygame.time.get_ticks()
        potezi = self.sortiraj_poteze(tabla, svi_potezi(tabla, BLACK))
        najbolji_potez = potezi[0] if potezi else None

        if najbolji_potez is None:
            return None

        if len(potezi) == 1:
            tabla.odigraj_potez(najbolji_potez)
            return najbolji_potez

        obavezno_jedenje = all(potez.pojedeni for potez in potezi)
        limit = (
            self.LIMIT_KRATKOG_JEDENJA_MS
            if obavezno_jedenje and len(potezi) <= 2
            else self.LIMIT_PRETRAGE_MS
        )

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
        
        tabla.odigraj_potez(najbolji_potez)

        return najbolji_potez

    def napravi_zobrist_tabelu(self):
        generator = random.Random(1)
        tabela = []

        for indeks in range(32):
            tabela.append({
                "BLACK": generator.getrandbits(64),
                "WHITE": generator.getrandbits(64),
                "KRALJEVIC": generator.getrandbits(64),
                "MARKO": generator.getrandbits(64),
                "RELIKVIJE": {
                    kljuc: generator.getrandbits(64)
                    for kljuc in self.VREDNOST_RELIKVIJE
                },
                "OKLOP": [generator.getrandbits(64) for _ in range(3)],
                "KOLEBANJE": [generator.getrandbits(64) for _ in range(3)],
            })

        return {
            "polja": tabela,
            "remi": [generator.getrandbits(64) for _ in range(41)],
        }

    def zobrist_hash(self, tabla):
        h = 0

        for indeks, figura in enumerate(tabla.tabla):
            if figura is None:
                continue

            polje = self.zobrist["polja"][indeks]
            h ^= polje["BLACK" if figura.color == BLACK else "WHITE"]
            if figura.kraljevic:
                h ^= polje["KRALJEVIC"]
            if figura.marko:
                h ^= polje["MARKO"]

            for kljuc in {relikvija.kljuc for relikvija in figura.relikvije}:
                h ^= polje["RELIKVIJE"][kljuc]

            h ^= polje["OKLOP"][min(figura.oklop, 2)]
            h ^= polje["KOLEBANJE"][min(figura.kolebanje, 2)]

        h ^= self.zobrist["remi"][min(tabla.br, 40)]

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

        return self.zobrist_hash(tabla), tabla.br, tuple(detalji_figura)

    def evaluacija(self, tabla):
        score = 0.0

        for i, figura in enumerate(tabla.tabla):
            if figura is None:
                continue

            red, kolona = tabla.indeks_u_red_kolonu(i)
            vrednost = self.vrednost_figure(figura)

            if not figura.kraljevic:
                if figura.color == BLACK:
                    vrednost += red * self.NAPREDOVANJE
                else:
                    vrednost += (7 - red) * self.NAPREDOVANJE

            if (red, kolona) in self.UGLOVI:
                vrednost += self.UGAO
            elif kolona == 0 or kolona == 7:
                vrednost += self.IVICA

            if 2 <= kolona <= 5:
                vrednost += self.CENTAR

            if (red, kolona) in self.BRAZDE:
                vrednost += self.BRAZDA

            if figura.color == BLACK:
                score += vrednost
            else:
                score -= vrednost

        black_potezi_lista = svi_potezi(tabla, BLACK)
        white_potezi_lista = svi_potezi(tabla, WHITE)

        if not black_potezi_lista and white_potezi_lista:
            return -self.POBEDA
        if not white_potezi_lista and black_potezi_lista:
            return self.POBEDA

        black_potezi = len(black_potezi_lista)
        white_potezi = len(white_potezi_lista)
        score += (black_potezi - white_potezi) * self.MOBILNOST

        black_jedenja = sum(len(p.pojedeni) for p in black_potezi_lista if p.pojedeni)
        white_jedenja = sum(len(p.pojedeni) for p in white_potezi_lista if p.pojedeni)
        score += (black_jedenja - white_jedenja) * self.DOSTUPNO_JEDENJE

        najveca_black_prilika = self.najveca_vrednost_jedenja(tabla, black_potezi_lista)
        najveca_white_prilika = self.najveca_vrednost_jedenja(tabla, white_potezi_lista)
        score += (najveca_black_prilika - najveca_white_prilika) * self.NAJBOLJE_JEDENJE

        return score

    def vrednost_figure(self, figura):
        if figura is None:
            return 0.0

        vrednost = self.KRALJEVIC if figura.kraljevic else self.OBICNA_FIGURA

        if figura.marko:
            vrednost += self.MARKO

        kljucevi = {relikvija.kljuc for relikvija in figura.relikvije}
        vrednost += sum(self.VREDNOST_RELIKVIJE.get(kljuc, 0.0) for kljuc in kljucevi)

        broj_markovih = len(kljucevi & self.MARKOVE_RELIKVIJE)
        vrednost += broj_markovih * broj_markovih * 0.12

        if not figura.marko and self.MARKOVE_RELIKVIJE <= kljucevi:
            if figura.kraljevic or "blago" in kljucevi:
                vrednost += self.MARKO
            else:
                vrednost += 0.8

        vrednost += figura.oklop * self.OKLOP_PO_POTEZU
        if not figura.marko:
            vrednost -= figura.kolebanje * self.KOLEBANJE_PO_POTEZU

        return vrednost

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
        nova.animacija_pomeranja = None
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
            rezultat = self.evaluacija(tabla)
            self.transposition_table[kljuc] = rezultat
            return rezultat
        else:
            if maxFigura:
                potezi = self.sortiraj_poteze(tabla, svi_potezi(tabla, BLACK))
                if not potezi:
                    rezultat = self.evaluacija(tabla)
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
                    rezultat = self.evaluacija(tabla)
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
