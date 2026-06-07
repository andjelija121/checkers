from math import inf

from figura import Figura
from konstante import BLACK, WHITE
from pravila import svi_potezi
from tabla import Tabla

class Ai:
    def __init__(self):
        pass

    def ai_potez(self,tabla):
        najbolja_ocena=-inf
        najbolji_potez = None

        for potez in svi_potezi(tabla,BLACK):
            nova_tabla = self.odigraj_na_kopiji_table(tabla,potez)
            ocena = self.minimax(nova_tabla,3,False)
            
            if ocena>najbolja_ocena:
                najbolja_ocena = ocena
                najbolji_potez = potez
        
        red,kolona = tabla.indeks_u_red_kolonu(najbolji_potez.krajnji_indeks)
        pomeranje = tabla.pomeri(najbolji_potez.figura,red,kolona,najbolji_potez.pojedeni)
        if pomeranje:
            print("idegas")

    def evaluacija(self,tabla):
        score = 0

        for figura in tabla.tabla:
            if figura is None:
                continue

            vrednost = 3
            if figura.kraljevic:
                vrednost = 5

            if figura.color == BLACK:
                score += vrednost
            else:
                score -= vrednost

        return score

    def odigraj_na_kopiji_table(self,tabla,potez):
        nova_tabla = self.kopija_table(tabla)
        novi_red,nova_kolona = tabla.indeks_u_red_kolonu(potez.krajnji_indeks)
        nova_figura = nova_tabla.tabla[potez.pocetni_indeks]
        pomeri = nova_tabla.pomeri(nova_figura,novi_red,nova_kolona,potez.pojedeni)
        return nova_tabla
    
    def kopija_table(self,tabla):
        nova = Tabla()
        for i,f in enumerate(tabla.tabla):
            if f is not None:
                nova_figura = Figura(f.row,f.col,f.color)
                nova_figura.kraljevic = f.kraljevic
                nova.tabla[i] = nova_figura
        return nova


    def minimax(self,tabla,dubina,maxFigura):
        if dubina ==0:
            return self.evaluacija(tabla)
        else:
            if maxFigura:
                potezi = svi_potezi(tabla,BLACK)
                maximum = -inf
                
                for potez in potezi:
                    nova_tabla = self.odigraj_na_kopiji_table(tabla,potez)
                    ocena = self.minimax(nova_tabla,dubina-1,False)
                    maximum = max(ocena,maximum)
                return maximum
            else:
                potezi = svi_potezi(tabla,WHITE)
                minimum = inf

                for potez in potezi:
                    nova_tabla = self.odigraj_na_kopiji_table(tabla,potez)
                    ocena = self.minimax(nova_tabla,dubina-1,True)
                    minimum = min(ocena,minimum)
                return minimum