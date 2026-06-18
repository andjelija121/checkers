from konstante import BLACK, WHITE


class UndoManager:
    def __init__(self, igra):
        self.igra = igra
        self.stanja = []

    def napravi_stanje(self):
        igra = self.igra
        stanja_figura = []

        for figura in igra.tabla.tabla:
            if figura is None:
                continue

            stanja_figura.append((
                figura,
                list(figura.relikvije),
                figura.oklop,
                figura.kolebanje,
                figura.marko,
            ))

        return {
            "stanja_figura": stanja_figura,
            "dek": list(igra.carev_drum.dek),
            "sledeci_indeks": igra.carev_drum.sledeci_indeks,
            "poslednja_relikvija": igra.poslednja_relikvija,
            "poruka_relikvije_do": igra.poruka_relikvije_do,
        }
    def vrati_stanje(self, stanje):
        igra = self.igra
        for figura, relikvije, oklop, kolebanje, marko in stanje["stanja_figura"]:
            figura.relikvije = list(relikvije)
            figura.oklop = oklop
            figura.kolebanje = kolebanje
            figura.marko = marko

        igra.carev_drum.dek = list(stanje["dek"])
        igra.carev_drum.sledeci_indeks = stanje["sledeci_indeks"]
        igra.poslednja_relikvija = stanje["poslednja_relikvija"]
        igra.poruka_relikvije_do = stanje["poruka_relikvije_do"]

    def undo_potez(self):
        igra = self.igra
        if igra.replay_aktivan:
            return False
        if igra.ceka_izbor_relikvije is not None:
            broj_poteza_za_vracanje = 1
        elif igra.na_potezu == BLACK and igra.ai_ceka_do is not None:
            broj_poteza_za_vracanje = 1
        elif igra.na_potezu == WHITE:
            broj_poteza_za_vracanje = 2
        else:
            return False
        vracen_bar_jedan = False
        poslednji_undo_dogadjaj = None
        for _ in range(broj_poteza_za_vracanje):
            if igra.tabla.undo_potez():
                vracen_bar_jedan = True
                if self.stanja:
                    self.vrati_stanje(self.stanja.pop())
                poslednji_undo_dogadjaj = igra.zabelezi_replay_undo()

        if not vracen_bar_jedan:
            return False
        igra.na_potezu = WHITE
        igra.ai_ceka_do = None
        igra.obavezna_figura = None
        igra.figure_koje_moraju_da_jedu = []
        igra.obavezni_potezi_po_odredistu = {}
        igra.pobednik = None
        igra.nereseno = False
        igra.ceka_izbor_relikvije = None
        igra.pripremi_belog_igraca()

        if poslednji_undo_dogadjaj is not None:
            poslednji_undo_dogadjaj.stanje = igra.napravi_replay_stanje()
        return True
