class CirkularniDek:
    def __init__(self, elementi, kapacitet=5):
        if kapacitet <= 0:
            raise ValueError("Kapacitet mora biti veci od nule.")
        if not elementi:
            raise ValueError("Kruzni niz elemenata ne sme biti prazan.")

        self.elementi = list(elementi)
        self.kapacitet = kapacitet
        self.sledeci_indeks = 0
        self.dek = []

    def dodaj_sledeci(self):
        element = self.elementi[self.sledeci_indeks]
        self.sledeci_indeks = (self.sledeci_indeks + 1) % len(self.elementi)

        self.dek.insert(0, element)
        izbacen = None

        if len(self.dek) > self.kapacitet:
            izbacen = self.dek.pop()

        return element, izbacen

    def uzmi_prvi(self):
        if self.prazan():
            return None
        return self.dek.pop(0)

    def uzmi_poslednji(self):
        if self.prazan():
            return None
        return self.dek.pop()

    def prvi(self):
        if self.prazan():
            return None
        return self.dek[0]

    def poslednji(self):
        if self.prazan():
            return None
        return self.dek[-1]

    def prazan(self):
        return len(self.dek) == 0

    def pun(self):
        return len(self.dek) == self.kapacitet

    def velicina(self):
        return len(self.dek)

    def sadrzaj(self):
        return list(self.dek)

    def kopija(self):
        novi = CirkularniDek(self.elementi, self.kapacitet)
        novi.sledeci_indeks = self.sledeci_indeks
        novi.dek = list(self.dek)
        return novi
