from konstante import WHITE, BLACK
from potez import Potez
from pravila_kraljevic import validni_potezi_kraljevic


def validni_potezi(tabla, figura):
    validni = []
    moranje = False
    pojedeni = {}

    if figura is None:
        return [], {}

    pocetni_indeks = tabla.red_kolona_u_indeks(figura.row, figura.col)
    if pocetni_indeks is None:
        return []

    if figura.kraljevic:
        return validni_potezi_kraljevic(tabla,figura)

    if figura.color == WHITE:
        smerovi = [(-1, -1), (-1, 1)]
    elif figura.color == BLACK:
        smerovi = [(1, -1), (1, 1)]



    for red_smer, kolona_smer in smerovi:
        novi_red = figura.row + red_smer
        nova_kolona = figura.col + kolona_smer
        novi_indeks = tabla.red_kolona_u_indeks(novi_red, nova_kolona)

        if novi_indeks is None:
            continue

        if tabla.tabla[novi_indeks] is None and not moranje:
            validni.append(novi_indeks)

        elif tabla.tabla[novi_indeks] is not None and tabla.tabla[novi_indeks].color != figura.color:
            skok_indeks = jedi(tabla, red_smer, kolona_smer, novi_indeks)

            if skok_indeks is not None:
                if not moranje:
                    validni = []
                    moranje = True
            lancano(tabla,figura,smerovi,red_smer,kolona_smer,novi_indeks,pojedeni,validni,[])
            

    return validni,pojedeni
                
    
def jedi(tabla,smer_r,smer_k,indeks):
    red,kolona= tabla.indeks_u_red_kolonu(indeks)
    red+= smer_r
    kolona+=smer_k
    novi_indeks= tabla.red_kolona_u_indeks(red,kolona)
    if novi_indeks is None or tabla.tabla[novi_indeks] is not None:
        return None
    else:
        return novi_indeks
    

def lancano(tabla, figura, smerovi, red_smer, kolona_smer, indeks, pojedeni, validni, jedeni):
    pojeden = jedi(tabla, red_smer, kolona_smer, indeks)

    if pojeden is None:
        return

    novi_jedeni = jedeni + [indeks]

    red_p, kolona_p = tabla.indeks_u_red_kolonu(pojeden)
    nasao_nastavak = False

    for smer_r, smer_k in smerovi:
        novi_red = red_p + smer_r
        nova_kolona = kolona_p + smer_k
        novi_indeks = tabla.red_kolona_u_indeks(novi_red, nova_kolona)

        if novi_indeks is None:
            continue

        if tabla.tabla[novi_indeks] is None:
            continue

        if tabla.tabla[novi_indeks].color == figura.color:
            continue

        if novi_indeks in novi_jedeni:
            continue

        sledeci_skok = jedi(tabla, smer_r, smer_k, novi_indeks)

        if sledeci_skok is None:
            continue

        nasao_nastavak = True

        lancano(
            tabla,
            figura,
            smerovi,
            smer_r,
            smer_k,
            novi_indeks,
            pojedeni,
            validni,
            novi_jedeni
        )

    if not nasao_nastavak:
        validni.append(pojeden)
        pojedeni[pojeden] = novi_jedeni


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
