import pygame

from ai import Ai
from konstante import WHITE, BLACK
from pravila import svi_potezi
from strukture.Relikvija import MesinaRujnogVina, Sarac, TokaOdCelika, Topuz, TriTovaraBlaga
from strukture.cirkularni_dek import CirkularniDek
from strukture.replay import ReplayManager
from strukture.undo import UndoManager
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

        relikvije = [
            TokaOdCelika(),
            MesinaRujnogVina(),
            Topuz(),
            Sarac(),
            TriTovaraBlaga()
]
        self.carev_drum = CirkularniDek(relikvije)
        self.zapocni_potez()

        self.undo_manager = UndoManager(self)
        self.undo_stanja_igre = self.undo_manager.stanja
        self.replay_manager = ReplayManager(self)

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
        if self.replay_aktivan:
            return
        if self.tabla.animacija_pomeranja is not None:
            return
        if self.pobednik is not None or self.nereseno:
            return
        if self.ceka_izbor_relikvije is not None:
            return
        if self.na_potezu != WHITE:
            return

        indeks = self.tabla.red_kolona_u_indeks(red, kolona)
        kliknuta_figura = self.tabla.uzmi_figuru(red, kolona)
        klik_na_obavezno_odrediste = (
            indeks is not None
            and indeks in self.obavezni_potezi_po_odredistu
        )

        if klik_na_obavezno_odrediste:
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
            and not klik_na_obavezno_odrediste
        ):
            return False

        undo_stanje = self.napravi_undo_stanje()
        broj_poteza_pre = self.tabla.stek.size()

        if self.obavezna_figura is None:
            odigrano = self.tabla.izaberi(red, kolona)
        elif indeks is not None and (
            self.tabla.tabla[indeks] is None or klik_na_obavezno_odrediste
        ):
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
        if self.replay_aktivan:
            self.update_replay()
            return
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
            relikvija = self.carev_drum.prvi()
        elif izbor == "kraj":
            relikvija = self.carev_drum.poslednji()
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
        relikvije_figure = {relikvija.kljuc for relikvija in figura.relikvije}

        osnovne_relikvije = {"mesina", "topuz", "sarac"}
        postaje_marko = not figura.marko and osnovne_relikvije <= relikvije_figure and (
            figura.kraljevic or "blago" in relikvije_figure
        )
        if postaje_marko:
            figura.marko = True
            self.tabla.br = 0

    def zavrsi_trenutni_potez(self):
        odigrala_boja = self.na_potezu

        if self.na_potezu == WHITE:
            protivnik = BLACK
        else:
            protivnik = WHITE

        if self.proveri_pobednika(protivnik):
            self.zabelezi_replay_potez(odigrala_boja)
            return

        self.proveri_nereseno()
        if self.nereseno:
            self.zabelezi_replay_potez(odigrala_boja)
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

        self.preskoci_potez_ako_je_igrac_blokiran(odigrala_boja)

        self.zabelezi_replay_potez(odigrala_boja)

    def proveri_pobednika(self, boja_na_potezu):
        if any(
            figura is not None and figura.color == boja_na_potezu
            for figura in self.tabla.tabla
        ):
            return False

        self.pobednik = BLACK if boja_na_potezu == WHITE else WHITE
        self.na_potezu = None
        self.ai_ceka_do = None
        return True

    def preskoci_potez_ako_je_igrac_blokiran(self, prethodna_boja):
        if svi_potezi(self.tabla, self.na_potezu):
            return False

        if not svi_potezi(self.tabla, prethodna_boja):
            self.nereseno = True
            self.na_potezu = None
            self.ai_ceka_do = None
            return True

        self.na_potezu = prethodna_boja
        if prethodna_boja == WHITE:
            self.ai_ceka_do = None
            self.pripremi_belog_igraca()
        else:
            self.ai_ceka_do = self.vreme_za_ai_potez()
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
        return self.undo_manager.undo_potez()

    def napravi_replay_stanje(self):
        return self.replay_manager.napravi_stanje()

    def napravi_relikviju(self, kljuc):
        return self.replay_manager.napravi_relikviju(kljuc)

    def ucitaj_replay_stanje(self, stanje):
        self.replay_manager.ucitaj_stanje(stanje)

    def zabelezi_replay_potez(self, boja):
        self.replay_manager.zabelezi_potez(boja)

    def zabelezi_replay_undo(self):
        return self.replay_manager.zabelezi_undo()

    def pokreni_replay(self):
        return self.replay_manager.pokreni()

    def update_replay(self):
        self.replay_manager.update()

    def napravi_undo_stanje(self):
        return self.undo_manager.napravi_stanje()

    def vrati_undo_stanje(self, undo_stanje):
        self.undo_manager.vrati_stanje(undo_stanje)

    def smanji_trajanje_efekata(self, odigrala_boja):
        for figura in self.tabla.tabla:
            if figura is None:
                continue

            if figura.color == odigrala_boja:
                if figura.kolebanje > 0:
                    figura.kolebanje -= 1
            else:
                if figura.oklop > 0:
                    figura.oklop -= 1
