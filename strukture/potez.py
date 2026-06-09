class Potez:
    def __init__(self, figura, pocetni_indeks, krajnji_indeks, pojedeni=None):
        self.figura = figura
        self.pocetni_indeks = pocetni_indeks
        self.krajnji_indeks = krajnji_indeks
        self.pojedeni = pojedeni or {}