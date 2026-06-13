class Relikvija:
    def __init__(self, naziv, opis, kljuc, boja, oznaka):
        self.naziv = naziv
        self.opis = opis
        self.kljuc = kljuc
        self.boja = boja
        self.oznaka = oznaka

    def aktiviraj(self, igra, figura):
        raise NotImplementedError


class TokaOdCelika(Relikvija):
    def __init__(self):
        super().__init__(
            naziv="Тока од челика",
            opis="Оклоп",
            kljuc="toka",
            boja=(105, 170, 205),
            oznaka="Ч"
        )

    def aktiviraj(self, igra, figura):
        if figura.marko:
            figura.oklop=2
        else:
            figura.oklop=1


class MesinaRujnogVina(Relikvija):
    def __init__(self):
        super().__init__(
            naziv="Мешина рујног вина",
            opis="Поглед испод обрва",
            kljuc="mesina",
            boja=(155, 55, 80),
            oznaka="М"
        )

    def aktiviraj(self, igra, figura):
        najblizi = self.nadji_najblizeg(igra,figura)
        if najblizi is not None:
            if not najblizi.marko:
                najblizi.kolebanje=2
    def nadji_najblizeg(self,igra,figura):
        protivnici =[polje for polje in igra.tabla.tabla if polje is not None and polje.color!=figura.color]
        najblizi = None
        najmanja_udaljenost = float("inf")

        for protivnik in protivnici:
            udaljenost = max(
                abs(protivnik.row - figura.row),
                abs(protivnik.col - figura.col)
            )

            if udaljenost < najmanja_udaljenost:
                najmanja_udaljenost = udaljenost
                najblizi = protivnik
        return najblizi



class Topuz(Relikvija):
    def __init__(self):
        super().__init__(
            naziv="Топуз",
            opis="Разорни ударац",
            kljuc="topuz",
            boja=(205, 75, 42),
            oznaka="Т"
        )

    def aktiviraj(self, igra, figura):
        pass


class Sarac(Relikvija):
    def __init__(self):
        super().__init__(
            naziv="Шарац",
            opis="Шарчев скок",
            kljuc="sarac",
            boja=(65, 150, 88),
            oznaka="Ш"
        )

    def aktiviraj(self, igra, figura):
        pass


class TriTovaraBlaga(Relikvija):
    def __init__(self):
        super().__init__(
            naziv="Три товара блага",
            opis="Крунисање",
            kljuc="blago",
            boja=(225, 175, 35),
            oznaka="Б"
        )

    def aktiviraj(self, igra, figura):
        bila_kraljevic = figura.kraljevic
        figura.postani_kraljevic()
        if igra is not None and not bila_kraljevic:
            igra.tabla.br = 0
