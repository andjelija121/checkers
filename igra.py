import pygame

from ai import Ai
from konstante import WHITE, BLACK
from pravila import svi_potezi
from strukture.Relikvija import MesinaRujnogVina, Relikvija, Sarac, TokaOdCelika, Topuz, TriTovaraBlaga
from strukture.cirkularni_dek import CirkularniDek
from strukture.figura import Figura
from strukture.replay import ReplayDogadjaj, StabloPartije
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

        pocetno_stanje = self.napravi_replay_stanje()
        self.stablo_partije = StabloPartije(pocetno_stanje)
        self.replay_dogadjaji = [
            ReplayDogadjaj(
                "pocetak",
                pocetno_stanje,
                self.stablo_partije.koren,
                "Pocetak partije"
            )
        ]
        self.replay_aktivan = False
        self.replay_indeks = 0
        self.replay_sledece_vreme = 0
        self.replay_razmak = 1000
        self.replay_opis = ""
        self.replay_krajnji_rezultat = None

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
        if self.replay_aktivan:
            return False
        if self.ceka_izbor_relikvije is not None:
            broj_poteza_za_vracanje = 1
        elif self.na_potezu == BLACK and self.ai_ceka_do is not None:
            broj_poteza_za_vracanje = 1
        elif self.na_potezu == WHITE:
            broj_poteza_za_vracanje = 2
        else:
            return False

        vracen_bar_jedan = False
        poslednji_undo_dogadjaj = None
        for _ in range(broj_poteza_za_vracanje):
            if self.tabla.undo_potez():
                vracen_bar_jedan = True
                if self.undo_stanja_igre:
                    undo_stanje = self.undo_stanja_igre.pop()
                    self.vrati_undo_stanje(undo_stanje)
                poslednji_undo_dogadjaj = self.zabelezi_replay_undo()

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
        self.pripremi_belog_igraca()

        if poslednji_undo_dogadjaj is not None:
            poslednji_undo_dogadjaj.stanje = self.napravi_replay_stanje()
        return True

    def napravi_replay_stanje(self):
        figure = []

        for figura in self.tabla.tabla:
            if figura is None:
                figure.append(None)
                continue

            figure.append({
                "row": figura.row,
                "col": figura.col,
                "color": figura.color,
                "kraljevic": figura.kraljevic,
                "marko": figura.marko,
                "oklop": figura.oklop,
                "kolebanje": figura.kolebanje,
                "relikvije": [relikvija.kljuc for relikvija in figura.relikvije]
            })

        return {
            "figure": figure,
            "na_potezu": self.na_potezu,
            "br": self.tabla.br,
            "carev_drum": [relikvija.kljuc for relikvija in self.carev_drum.dek],
            "sledeci_indeks": self.carev_drum.sledeci_indeks,
            "pobednik": self.pobednik,
            "nereseno": self.nereseno
        }

    def napravi_relikviju(self, kljuc):
        klase = {
            "toka": TokaOdCelika,
            "mesina": MesinaRujnogVina,
            "topuz": Topuz,
            "sarac": Sarac,
            "blago": TriTovaraBlaga
        }
        return klase[kljuc]()

    def ucitaj_replay_stanje(self, stanje):
        nova_tabla = [None] * 32

        for indeks, podaci in enumerate(stanje["figure"]):
            if podaci is None:
                continue

            figura = Figura(podaci["row"], podaci["col"], podaci["color"])
            figura.kraljevic = podaci["kraljevic"]
            figura.marko = podaci["marko"]
            figura.oklop = podaci["oklop"]
            figura.kolebanje = podaci["kolebanje"]
            figura.relikvije = [
                self.napravi_relikviju(kljuc)
                for kljuc in podaci["relikvije"]
            ]
            nova_tabla[indeks] = figura

        self.tabla.tabla = nova_tabla
        self.tabla.br = stanje["br"]
        self.tabla.izabrana_figura = None
        self.tabla.animacija_jedenja = []
        self.tabla.animacija_pomeranja = None
        self.tabla.animacija_undo = []

        self.carev_drum.dek = [
            self.napravi_relikviju(kljuc)
            for kljuc in stanje["carev_drum"]
        ]
        self.carev_drum.sledeci_indeks = stanje["sledeci_indeks"]

        self.na_potezu = stanje["na_potezu"]
        self.pobednik = stanje["pobednik"]
        self.nereseno = stanje["nereseno"]
        self.ai_ceka_do = None
        self.obavezna_figura = None
        self.figure_koje_moraju_da_jedu = []
        self.obavezni_potezi_po_odredistu = {}
        self.ceka_izbor_relikvije = None
        self.poslednja_relikvija = None
        self.poruka_relikvije_do = 0

    def zabelezi_replay_potez(self, boja):
        stanje = self.napravi_replay_stanje()
        naziv = "Beli" if boja == WHITE else "Crni"
        opis = f"{naziv} potez"
        cvor = self.stablo_partije.dodaj_potez(stanje, opis)
        self.replay_dogadjaji.append(
            ReplayDogadjaj("potez", stanje, cvor, opis)
        )

    def zabelezi_replay_undo(self):
        if not self.stablo_partije.undo():
            return None

        stanje = self.napravi_replay_stanje()
        dogadjaj = ReplayDogadjaj(
            "undo",
            stanje,
            self.stablo_partije.trenutni,
            "Undo poteza"
        )
        self.replay_dogadjaji.append(dogadjaj)
        return dogadjaj

    def pokreni_replay(self):
        if len(self.replay_dogadjaji) <= 1:
            return False

        self.replay_krajnji_rezultat = (self.pobednik, self.nereseno)
        self.replay_aktivan = True
        self.replay_indeks = 0
        self.replay_sledece_vreme = pygame.time.get_ticks()
        self.replay_opis = "Pocetak partije"
        self.ai_ceka_do = None
        return True

    def update_replay(self):
        sada = pygame.time.get_ticks()
        if sada < self.replay_sledece_vreme:
            return

        if self.replay_indeks >= len(self.replay_dogadjaji):
            self.replay_aktivan = False
            if self.replay_krajnji_rezultat is not None:
                self.pobednik, self.nereseno = self.replay_krajnji_rezultat
            return

        dogadjaj = self.replay_dogadjaji[self.replay_indeks]
        self.ucitaj_replay_stanje(dogadjaj.stanje)
        self.replay_opis = dogadjaj.opis
        self.replay_indeks += 1
        self.replay_sledece_vreme = sada + self.replay_razmak

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

            if figura.color == odigrala_boja:
                if figura.kolebanje > 0:
                    figura.kolebanje -= 1
            else:
                if figura.oklop > 0:
                    figura.oklop -= 1
