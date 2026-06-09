def validni_potezi_kraljevic(tabla, figura):
    validni = []
    pojedeni = {}
    moranje = False

    smerovi = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    pocetni_indeks = tabla.red_kolona_u_indeks(figura.row, figura.col)

    for smer_r, smer_k in smerovi:
        smer_validni = []
        jedeni = []

        red = figura.row + smer_r
        kolona = figura.col + smer_k
        indeks = tabla.red_kolona_u_indeks(red, kolona)

        ide(tabla, indeks, smer_r, smer_k, figura.color, smer_validni, jedeni)

        if jedeni:
            if not moranje:
                moranje = True
                validni = []

            for sletanje in smer_validni:
                lancano_validni = []
                lancano_pojedeni = {}

                lancano_kraljevic(
                    tabla,
                    sletanje,
                    figura.color,
                    jedeni.copy(),
                    lancano_validni,
                    lancano_pojedeni
                )

                if lancano_validni:
                    validni += lancano_validni
                    pojedeni.update(lancano_pojedeni)
                else:
                    validni.append(sletanje)
                    pojedeni[sletanje] = jedeni.copy()

        elif not moranje:
            validni += smer_validni

    return validni, pojedeni
def ide(tabla,indeks,smer_r,smer_k,boja,validni,pojedeni):
    if indeks is None or (tabla.tabla[indeks] is not None and tabla.tabla[indeks].color == boja):
        return
    if tabla.tabla[indeks] is None:
        validni.append(indeks)
    if tabla.tabla[indeks] is not None:
        sledeci_indeks = racun_novi_indeks(tabla,indeks,smer_r,smer_k)
        if  sledeci_indeks is None:
            return
        if tabla.tabla[sledeci_indeks]is not None:
            return
        
        validni.clear()
        pojedeni.append(indeks)
        
    novi_indeks = racun_novi_indeks(tabla,indeks,smer_r,smer_k)
    ide(tabla,novi_indeks,smer_r,smer_k,boja,validni,pojedeni)


def racun_novi_indeks(tabla,indeks,smer_r,smer_k):
    red, kolona = tabla.indeks_u_red_kolonu(indeks)
    red += smer_r
    kolona += smer_k
    return tabla.red_kolona_u_indeks(red, kolona)

def lancano_kraljevic(tabla, trenutni_indeks, boja, do_sada_pojedeni, validni, pojedeni):
    smerovi = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    nasao_nastavak = False

    red, kolona = tabla.indeks_u_red_kolonu(trenutni_indeks)

    for smer_r, smer_k in smerovi:
        smer_validni = []
        jedeni = []

        sledeci_red = red + smer_r
        sledeca_kolona = kolona + smer_k
        indeks = tabla.red_kolona_u_indeks(sledeci_red, sledeca_kolona)

        ide(tabla, indeks, smer_r, smer_k, boja, smer_validni, jedeni)

        if not jedeni:
            continue

        pojedena_figura = jedeni[0]

        if pojedena_figura in do_sada_pojedeni:
            continue

        nasao_nastavak = True

        for sletanje in smer_validni:
            novi_pojedeni = do_sada_pojedeni + [pojedena_figura]

            dublji_validni = []
            dublji_pojedeni = {}

            lancano_kraljevic(
                tabla,
                sletanje,
                boja,
                novi_pojedeni,
                dublji_validni,
                dublji_pojedeni
            )

            if dublji_validni:
                validni += dublji_validni
                pojedeni.update(dublji_pojedeni)
            else:
                validni.append(sletanje)
                pojedeni[sletanje] = novi_pojedeni

    if not nasao_nastavak:
        return