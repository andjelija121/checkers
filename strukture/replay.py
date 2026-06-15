import pygame

from konstante import WHITE
from strukture.Relikvija import MesinaRujnogVina, Sarac, TokaOdCelika, Topuz, TriTovaraBlaga
from strukture.figura import Figura


class ReplayDogadjaj:
    def __init__(self, tip, stanje, cvor, opis=""):
        self.tip = tip
        self.stanje = stanje
        self.cvor = cvor
        self.opis = opis


class CvorPartije:
    def __init__(self, stanje, roditelj=None, opis=""):
        self.stanje = stanje
        self.roditelj = roditelj
        self.opis = opis
        self.deca = []


class StabloPartije:
    def __init__(self, pocetno_stanje):
        self.koren = CvorPartije(
            stanje=pocetno_stanje,
            opis="Pocetak partije"
        )
        self.trenutni = self.koren

    def dodaj_potez(self, stanje, opis):
        novi = CvorPartije(
            stanje=stanje,
            roditelj=self.trenutni,
            opis=opis
        )
        self.trenutni.deca.append(novi)
        self.trenutni = novi
        return novi

    def undo(self):
        if self.trenutni.roditelj is None:
            return False

        self.trenutni = self.trenutni.roditelj
        return True


class ReplayManager:
    def __init__(self, igra):
        self.igra = igra
        self.resetuj()

    def resetuj(self):
        igra = self.igra
        pocetno_stanje = self.napravi_stanje()
        igra.stablo_partije = StabloPartije(pocetno_stanje)
        igra.replay_dogadjaji = [
            ReplayDogadjaj(
                "pocetak", pocetno_stanje, igra.stablo_partije.koren,
                "Pocetak partije",
            )
        ]
        igra.replay_aktivan = False
        igra.replay_indeks = 0
        igra.replay_sledece_vreme = 0
        igra.replay_razmak = 1000
        igra.replay_opis = ""
        igra.replay_krajnji_rezultat = None

    def napravi_stanje(self):
        igra = self.igra
        figure = []
        for figura in igra.tabla.tabla:
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
                "relikvije": [relikvija.kljuc for relikvija in figura.relikvije],
            })

        return {
            "figure": figure,
            "na_potezu": igra.na_potezu,
            "br": igra.tabla.br,
            "carev_drum": [relikvija.kljuc for relikvija in igra.carev_drum.dek],
            "sledeci_indeks": igra.carev_drum.sledeci_indeks,
            "pobednik": igra.pobednik,
            "nereseno": igra.nereseno,
        }

    @staticmethod
    def napravi_relikviju(kljuc):
        klase = {
            "toka": TokaOdCelika,
            "mesina": MesinaRujnogVina,
            "topuz": Topuz,
            "sarac": Sarac,
            "blago": TriTovaraBlaga,
        }
        return klase[kljuc]()

    def ucitaj_stanje(self, stanje):
        igra = self.igra
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
                self.napravi_relikviju(kljuc) for kljuc in podaci["relikvije"]
            ]
            nova_tabla[indeks] = figura

        igra.tabla.tabla = nova_tabla
        igra.tabla.br = stanje["br"]
        igra.tabla.izabrana_figura = None
        igra.tabla.animacija_jedenja = []
        igra.tabla.animacija_pomeranja = None
        igra.tabla.animacija_undo = []
        igra.carev_drum.dek = [
            self.napravi_relikviju(kljuc) for kljuc in stanje["carev_drum"]
        ]
        igra.carev_drum.sledeci_indeks = stanje["sledeci_indeks"]
        igra.na_potezu = stanje["na_potezu"]
        igra.pobednik = stanje["pobednik"]
        igra.nereseno = stanje["nereseno"]
        igra.ai_ceka_do = None
        igra.obavezna_figura = None
        igra.figure_koje_moraju_da_jedu = []
        igra.obavezni_potezi_po_odredistu = {}
        igra.ceka_izbor_relikvije = None
        igra.poslednja_relikvija = None
        igra.poruka_relikvije_do = 0

    def zabelezi_potez(self, boja):
        igra = self.igra
        stanje = self.napravi_stanje()
        naziv = "Beli" if boja == WHITE else "Crni"
        opis = f"{naziv} potez"
        cvor = igra.stablo_partije.dodaj_potez(stanje, opis)
        igra.replay_dogadjaji.append(ReplayDogadjaj("potez", stanje, cvor, opis))

    def zabelezi_undo(self):
        igra = self.igra
        if not igra.stablo_partije.undo():
            return None
        stanje = self.napravi_stanje()
        dogadjaj = ReplayDogadjaj(
            "undo", stanje, igra.stablo_partije.trenutni, "Undo poteza"
        )
        igra.replay_dogadjaji.append(dogadjaj)
        return dogadjaj

    def pokreni(self):
        igra = self.igra
        if len(igra.replay_dogadjaji) <= 1:
            return False
        igra.replay_krajnji_rezultat = (igra.pobednik, igra.nereseno)
        igra.replay_aktivan = True
        igra.replay_indeks = 0
        igra.replay_sledece_vreme = pygame.time.get_ticks()
        igra.replay_opis = "Pocetak partije"
        igra.ai_ceka_do = None
        return True

    def update(self):
        igra = self.igra
        sada = pygame.time.get_ticks()
        if sada < igra.replay_sledece_vreme:
            return
        if igra.replay_indeks >= len(igra.replay_dogadjaji):
            igra.replay_aktivan = False
            if igra.replay_krajnji_rezultat is not None:
                igra.pobednik, igra.nereseno = igra.replay_krajnji_rezultat
            return
        dogadjaj = igra.replay_dogadjaji[igra.replay_indeks]
        self.ucitaj_stanje(dogadjaj.stanje)
        igra.replay_opis = dogadjaj.opis
        igra.replay_indeks += 1
        igra.replay_sledece_vreme = sada + igra.replay_razmak
