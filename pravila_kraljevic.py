SMEROVI = [
    (-1, -1),
    (-1, 1),
    (1, -1),
    (1, 1)
]


def validni_potezi_kraljevic(tabla, figura):
    pocetni = tabla.red_kolona_u_indeks(
        figura.row,
        figura.col
    )

    jedenja = {}

    if figura.kolebanje==0 or  figura.marko:
        trazi_jedenja(
            tabla,
            figura,
            pocetni,
            pocetni,
            [],
            jedenja
        )

    if jedenja:
        return list(jedenja.keys()), jedenja

    validni = []

    for smer_red, smer_kolona in SMEROVI:
        sarac = figura.ima_relikviju("sarac")
        dodaj_prazna_polja(
            tabla,
            figura.row + smer_red,
            figura.col + smer_kolona,
            smer_red,
            smer_kolona,
            validni,
            sarac,
            figura.color
        )

    return validni, {}


def dodaj_prazna_polja(
    tabla,
    red,
    kolona,
    smer_red,
    smer_kolona,
    validni,
    sarac,
    boja
):
    indeks = tabla.red_kolona_u_indeks(red, kolona)

    if indeks is None:
        return

    if tabla.tabla[indeks] is not None and tabla.tabla[indeks].color == boja and sarac:
        skok = tabla.red_kolona_u_indeks(
            red + smer_red,
            kolona + smer_kolona
        )

        if skok is not None and tabla.tabla[skok] is None:
            validni.append(skok)

        return

    if tabla.tabla[indeks] is not None:
        return

    validni.append(indeks)

    dodaj_prazna_polja(
        tabla,
        red + smer_red,
        kolona + smer_kolona,
        smer_red,
        smer_kolona,
        validni,
        sarac,
        boja
    )


def trazi_jedenja(
    tabla,
    figura,
    trenutni,
    pocetni,
    pojedeni,
    rezultat
):
    nasao_nastavak = False
    red, kolona = tabla.indeks_u_red_kolonu(trenutni)

    for smer_red, smer_kolona in SMEROVI:
        protivnik = nadji_prvu_figuru(
            tabla,
            red + smer_red,
            kolona + smer_kolona,
            smer_red,
            smer_kolona,
            pocetni,
            pojedeni
        )

        if protivnik is None:
            continue

        protivnicka_figura = tabla.tabla[protivnik]

        


        if protivnicka_figura.oklop>0:
            continue

        if protivnicka_figura.color == figura.color:
            continue

        protivnik_red, protivnik_kolona = (
            tabla.indeks_u_red_kolonu(protivnik)
        )

        
        if figura.ima_relikviju("topuz"):
            rezultat[protivnik] = [protivnik]
            continue

        sletanje = tabla.red_kolona_u_indeks(
                protivnik_red + smer_red,
                protivnik_kolona + smer_kolona
            )

        if sletanje is None:
            continue

        if zauzeto(tabla, sletanje, pocetni, pojedeni):
            continue

        nasao_nastavak = True
        novi_pojedeni = pojedeni + [protivnik]

        trazi_jedenja(
            tabla,
            figura,
            sletanje,
            pocetni,
            novi_pojedeni,
            rezultat
        )

    if pojedeni and not nasao_nastavak:
        prethodni = rezultat.get(trenutni, [])

        if len(pojedeni) > len(prethodni):
            rezultat[trenutni] = pojedeni


def nadji_prvu_figuru(
    tabla,
    red,
    kolona,
    smer_red,
    smer_kolona,
    pocetni,
    pojedeni
):
    indeks = tabla.red_kolona_u_indeks(red, kolona)

    if indeks is None:
        return None

    if indeks == pocetni or indeks in pojedeni:
        return nadji_prvu_figuru(
            tabla,
            red + smer_red,
            kolona + smer_kolona,
            smer_red,
            smer_kolona,
            pocetni,
            pojedeni
        )

    if tabla.tabla[indeks] is not None:
        return indeks

    return nadji_prvu_figuru(
        tabla,
        red + smer_red,
        kolona + smer_kolona,
        smer_red,
        smer_kolona,
        pocetni,
        pojedeni
    )


def zauzeto(tabla, indeks, pocetni, pojedeni):
    if indeks == pocetni:
        return False

    if indeks in pojedeni:
        return False

    return tabla.tabla[indeks] is not None