from konstante import WHITE, BLACK
from potez import Potez


def validni_potezi(tabla, figura):
    validni = []
    moranje = False
    pojedeni = {}

    if figura is None:
        return [], {}

    red = figura.row
    kolona = figura.col

    if figura.color == WHITE:
        smerovi = [(-1, -1), (-1, 1)]
    elif figura.color == BLACK:
        smerovi = [(1, -1), (1, 1)]

    if figura.kraljevic:
        smerovi = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    pocetni_indeks = tabla.red_kolona_u_indeks(red, kolona)

    for red_smer, kolona_smer in smerovi:
        novi_red = red + red_smer
        nova_kolona = kolona + kolona_smer
        novi_indeks = tabla.red_kolona_u_indeks(novi_red, nova_kolona)

        if novi_indeks is None:
            continue

        if tabla.tabla[novi_indeks] is None and not moranje:
            validni.append(novi_indeks)

        elif tabla.tabla[novi_indeks] is not None and tabla.tabla[novi_indeks].color != figura.color:
            krajevi = lancano(tabla, pocetni_indeks, figura.color, figura.kraljevic, [])

            if krajevi:
                if not moranje:
                    validni = []

                moranje = True

                for krajnji_indeks, jedeni in krajevi:
                    if krajnji_indeks not in validni:
                        validni.append(krajnji_indeks)
                    pojedeni[krajnji_indeks] = jedeni

    return validni, pojedeni


def jedi(tabla, moj_indeks, smer_r, smer_k, boja, vec_jedeni):
    red, kolona = tabla.indeks_u_red_kolonu(moj_indeks)

    protivnik_red = red + smer_r
    protivnik_kolona = kolona + smer_k
    protivnik_indeks = tabla.red_kolona_u_indeks(protivnik_red, protivnik_kolona)

    if protivnik_indeks is None:
        return None

    protivnik = tabla.tabla[protivnik_indeks]

    if protivnik is None:
        return None

    if protivnik.color == boja:
        return None

    if protivnik_indeks in vec_jedeni:
        return None

    skok_red = protivnik_red + smer_r
    skok_kolona = protivnik_kolona + smer_k
    skok_indeks = tabla.red_kolona_u_indeks(skok_red, skok_kolona)

    if skok_indeks is None:
        return None

    if tabla.tabla[skok_indeks] is not None:
        return None

    return skok_indeks, protivnik_indeks


def lancano(tabla, moj_indeks, boja, kraljevic, vec_jedeni):
    krajevi = []

    if boja == WHITE:
        smerovi = [(-1, -1), (-1, 1)]
    elif boja == BLACK:
        smerovi = [(1, -1), (1, 1)]

    if kraljevic:
        smerovi = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    for smer_r, smer_k in smerovi:
        rezultat = jedi(tabla, moj_indeks, smer_r, smer_k, boja, vec_jedeni)

        if rezultat is None:
            continue

        skok_indeks, protivnik_indeks = rezultat
        novi_jedeni = vec_jedeni + [protivnik_indeks]

        nastavci = lancano(tabla, skok_indeks, boja, kraljevic, novi_jedeni)

        if nastavci:
            krajevi.extend(nastavci)
        else:
            krajevi.append((skok_indeks, novi_jedeni))

    return krajevi


def svi_potezi(tabla, boja):
    svi = []

    for polje in tabla.tabla:
        if polje is None:
            continue

        if polje.color == boja:
            validni, pojedeni = validni_potezi(tabla, polje)

            for v in validni:
                indeks = tabla.red_kolona_u_indeks(polje.row, polje.col)
                svi.append(Potez(polje, indeks, v, pojedeni.get(v, [])))

    jedenja = []

    for potez in svi:
        if potez.pojedeni:
            jedenja.append(potez)

    if jedenja:
        return jedenja

    return svi
