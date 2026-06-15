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
