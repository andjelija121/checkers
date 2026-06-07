from konstante import WHITE, BLACK
from potez import Potez

def validni_potezi(tabla, figura):
    validni = []
    moranje = False
    pojedeni = []
    jedeni=[]
    if figura is None:
        return False

    red = figura.row
    kolona = figura.col

    if figura.color == WHITE:
        smerovi = [(-1, -1), (-1, 1)]
    if figura.color == BLACK:
        smerovi = [(1, -1), (1, 1)]
    if figura.kraljevic:
        smerovi = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    for red_smer, kolona_smer in smerovi:
        novi_red = red_smer + red
        nova_kolona = kolona_smer + kolona
        novi_indeks = tabla.red_kolona_u_indeks(novi_red, nova_kolona)

        if novi_indeks is None:
            continue

        if novi_indeks is not None and tabla.tabla[novi_indeks] is None and not moranje:
            validni.append(novi_indeks)
        elif tabla.tabla[novi_indeks] is not None:
            skok = jedi(tabla, novi_indeks, red_smer, kolona_smer, pojedeni,figura.color,jedeni)
            if skok is None:
                for j in jedeni:
                    pojedeni.remove(j)
                jedeni=[]

            if skok is not None:
                if not moranje:
                    validni = []
                moranje = True
                validni.append(skok)


    return validni, pojedeni


def jedi(tabla, indeks, smer_r, smer_k, pojedeni,boja,jedeni):
    if tabla.tabla[indeks] is None:
        return indeks
    else:
        if tabla.tabla[indeks] is not None and tabla.tabla[indeks].color == boja:
            return None
        jedeni.append(indeks)
        pojedeni.append(indeks)
        red, kolona = tabla.indeks_u_red_kolonu(indeks)
        red += smer_r
        kolona += smer_k
        indeks = tabla.red_kolona_u_indeks(red, kolona)

        if indeks is None:
            return None

        return jedi(tabla, indeks, smer_r, smer_k, pojedeni,boja,jedeni)

def svi_potezi(tabla,boja):
    svi_potezi=[]
    for polje in tabla.tabla:
        if polje is None:
            continue
        if polje.color == boja:
            validni,pojedeni = validni_potezi(tabla,polje)
            for v in validni:
                indeks = tabla.red_kolona_u_indeks(polje.row,polje.col)
                svi_potezi.append(Potez(polje,indeks,v,pojedeni))
    return svi_potezi