import pygame

from ai import Ai
from konstante import WHITE, BLACK
from pravila import svi_potezi
from strukture.Relikvija import MesinaRujnogVina, Relikvija, Sarac, TokaOdCelika, Topuz, TriTovaraBlaga
from strukture.cirkularni_dek import CirkularniDek
from tabla import Tabla


BRAZDE = {(3, 0), (4, 7)}


class Igra:
    def __init__(self):
        self.ai = Ai()
        self.resetuj()

    def resetuj(self):
        self.tabla = Tabla()
        self.na_potezu = WHITE
        self.ai_ceka_do = None
        self.obavezna_figura = None
        self.figure_koje_moraju_da_jedu = []
        self.obavezni_potezi_po_odredistu = {}
        self.pobednik = None
        self.nereseno = False
        self.ceka_izbor_relikvije = None
        self.poslednja_relikvija = None
        self.poruka_relikvije_do = 0
        self.undo_stanja_igre = []

        relikvije = [
            TokaOdCelika(),
            MesinaRujnogVina(),
            Topuz(),
            Sarac(),
            TriTovaraBlaga()
]
        self.carev_drum = CirkularniDek(relikvije)
        self.zapocni_potez()

    def zapocni_potez(self):
        self.carev_drum.dodaj_sledeci()

    def pripremi_belog_igraca(self):
        figure = []
        potezi_po_odredistu = {}

        for potez in svi_potezi(self.tabla, WHITE):
            if potez.pojedeni:
                if potez.figura not in figure:
                    figure.append(potez.figura)
                potezi_po_odredistu[potez.krajnji_indeks] = potez

        self.figure_koje_moraju_da_jedu = figure
        self.obavezni_potezi_po_odredistu = potezi_po_odredistu
        self.obavezna_figura = None
        self.tabla.izabrana_figura = None

        if len(figure) == 1:
            self.obavezna_figura = figure[0]
            self.tabla.izabrana_figura = figure[0]

    def jedan_potez(self, red, kolona):
        if self.pobednik is not None or self.nereseno:
            return
        if self.ceka_izbor_relikvije is not None:
            return
        if self.na_potezu != WHITE:
            return

        indeks = self.tabla.red_kolona_u_indeks(red, kolona)
        kliknuta_figura = self.tabla.uzmi_figuru(red, kolona)

        if (
            self.obavezni_potezi_po_odredistu
            and indeks in self.obavezni_potezi_po_odredistu
            and kliknuta_figura is None
        ):
            potez = self.obavezni_potezi_po_odredistu[indeks]
            self.tabla.izabrana_figura = potez.figura
            self.obavezna_figura = potez.figura


        if (
            self.figure_koje_moraju_da_jedu
            and self.tabla.izabrana_figura is None
            and kliknuta_figura not in self.figure_koje_moraju_da_jedu
        ):
            return False

        if (
            self.figure_koje_moraju_da_jedu
            and kliknuta_figura is not None
            and kliknuta_figura not in self.figure_koje_moraju_da_jedu
        ):
            return False

        undo_stanje = self.napravi_undo_stanje()
        broj_poteza_pre = self.tabla.stek.size()

        if self.obavezna_figura is None:
            odigrano = self.tabla.izaberi(red, kolona)
        elif indeks is not None and self.tabla.tabla[indeks] is None:
            odigrano = self.tabla.izaberi(red, kolona)
            self.obavezna_figura = None
        else:
            return False

        if self.tabla.stek.size() > broj_poteza_pre:
            self.undo_stanja_igre.append(undo_stanje)

        if odigrano and self.tabla.izabrana_figura is None:
            pomerena_figura = self.tabla.tabla[indeks]
            self.figure_koje_moraju_da_jedu = []
            self.obavezni_potezi_po_odredistu = {}

            if self.proveri_brazdu(pomerena_figura):
                return

            self.zavrsi_trenutni_potez()

    def update(self):
        if self.pobednik is not None or self.nereseno:
            return
        if self.ceka_izbor_relikvije is not None:
            return
        if self.na_potezu != BLACK:
            return
        if pygame.time.get_ticks() < self.ai_ceka_do:
            return

        undo_stanje = self.napravi_undo_stanje()
        broj_poteza_pre = self.tabla.stek.size()
        ai_potez = self.ai.ai_potez(self.tabla)

        if ai_potez is None:
            return

        if self.tabla.stek.size() > broj_poteza_pre:
            self.undo_stanja_igre.append(undo_stanje)

        self.zavrsi_ai_potez(ai_potez.figura)

    def zavrsi_ai_potez(self, pomerena_figura):
        if self.proveri_brazdu(pomerena_figura):
            self.izaberi_relikviju("pocetak")
            return

        self.zavrsi_trenutni_potez()

    def proveri_brazdu(self, figura):
        if figura is None or (figura.row, figura.col) not in BRAZDE:
            return False
        if self.carev_drum.prazan():
            return False

        self.ceka_izbor_relikvije = figura
        return True

    def izaberi_relikviju(self, izbor):
        if self.ceka_izbor_relikvije is None:
            return False

        if izbor == "pocetak":
            relikvija = self.carev_drum.uzmi_prvi()
        elif izbor == "kraj":
            relikvija = self.carev_drum.uzmi_poslednji()
        else:
            return False

        if relikvija is None:
            return False

        figura = self.ceka_izbor_relikvije
        figura.relikvije.append(relikvija)
        relikvija.aktiviraj(self,figura)
        self.proveri_da_li_je_marko(figura)
        self.ceka_izbor_relikvije = None
        self.poslednja_relikvija = (figura, relikvija)
        self.poruka_relikvije_do = pygame.time.get_ticks() + 2200
        self.zavrsi_trenutni_potez()
        return True

    def proveri_da_li_je_marko(self, figura):
        potrebne_relikvije = {"mesina", "topuz", "sarac", "blago"}
        relikvije_figure = {relikvija.kljuc for relikvija in figura.relikvije}

        if (
            figura.ima_relikviju("mesina")
            and figura.ima_relikviju("topuz")
            and figura.ima_relikviju("sarac")
            and figura.ima_relikviju("blago")
        ):
            figura.marko = True

    def zavrsi_trenutni_potez(self):
        if self.na_potezu == WHITE:
            protivnik = BLACK
        else:
            protivnik = WHITE

        if self.proveri_pobednika(protivnik):
            return

        self.proveri_nereseno()
        if self.nereseno:
            return

        if self.na_potezu == WHITE:
            self.smanji_trajanje_efekata(WHITE)
            self.na_potezu = BLACK
            self.zapocni_potez()
            self.ai_ceka_do = self.vreme_za_ai_potez()
        else:
            self.smanji_trajanje_efekata(BLACK)
            self.na_potezu = WHITE
            self.zapocni_potez()
            self.ai_ceka_do = None
            self.pripremi_belog_igraca()

    def proveri_pobednika(self, boja_na_potezu):
        if svi_potezi(self.tabla, boja_na_potezu):
            return False

        self.pobednik = BLACK if boja_na_potezu == WHITE else WHITE
        self.na_potezu = None
        self.ai_ceka_do = None
        return True

    def vreme_za_ai_potez(self):
        sada = pygame.time.get_ticks()
        vreme = sada + 1000

        if self.tabla.animacija_jedenja:
            poslednji_pocetak = max(animacija[3] for animacija in self.tabla.animacija_jedenja)
            vreme = max(vreme, poslednji_pocetak + 520 + 150)

        return vreme

    def proveri_nereseno(self):
        if self.tabla.br >= 40:
            self.nereseno = True
            self.na_potezu = None
            self.ai_ceka_do = None

    def undo_potez(self):
        if self.na_potezu == BLACK and self.ai_ceka_do is not None:
            broj_poteza_za_vracanje = 1
        elif self.na_potezu == WHITE:
            broj_poteza_za_vracanje = 2
        else:
            return False

        vracen_bar_jedan = False
        for _ in range(broj_poteza_za_vracanje):
            if self.tabla.undo_potez():
                vracen_bar_jedan = True
                if self.undo_stanja_igre:
                    undo_stanje = self.undo_stanja_igre.pop()
                    self.vrati_undo_stanje(undo_stanje)

        if not vracen_bar_jedan:
            return False

        self.na_potezu = WHITE
        self.ai_ceka_do = None
        self.obavezna_figura = None
        self.figure_koje_moraju_da_jedu = []
        self.obavezni_potezi_po_odredistu = {}
        self.pobednik = None
        self.nereseno = False
        self.ceka_izbor_relikvije = None
        return True

    def napravi_undo_stanje(self):
        stanja_figura = []

        for figura in self.tabla.tabla:
            if figura is None:
                continue

            stanja_figura.append((
                figura,
                list(figura.relikvije),
                figura.oklop,
                figura.kolebanje,
                figura.marko
            ))

        return {
            "stanja_figura": stanja_figura,
            "dek": list(self.carev_drum.dek),
            "sledeci_indeks": self.carev_drum.sledeci_indeks,
            "poslednja_relikvija": self.poslednja_relikvija,
            "poruka_relikvije_do": self.poruka_relikvije_do
        }

    def vrati_undo_stanje(self, undo_stanje):
        for figura, relikvije, oklop, kolebanje, marko in undo_stanje["stanja_figura"]:
            figura.relikvije = list(relikvije)
            figura.oklop = oklop
            figura.kolebanje = kolebanje
            figura.marko = marko

        self.carev_drum.dek = list(undo_stanje["dek"])
        self.carev_drum.sledeci_indeks = undo_stanje["sledeci_indeks"]
        self.poslednja_relikvija = undo_stanje["poslednja_relikvija"]
        self.poruka_relikvije_do = undo_stanje["poruka_relikvije_do"]

    def smanji_trajanje_efekata(self, odigrala_boja):
        for figura in self.tabla.tabla:
            if figura is None:
                continue

            if figura.color == odigrala_boja and figura.ima_relikviju("sarac"):
                figura.sarac_skok = True

            if figura.color == odigrala_boja:
                if figura.kolebanje > 0:
                    figura.kolebanje -= 1
            else:
                if figura.oklop > 0:
                    figura.oklop -= 1
