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
            nova_tabla,lanac = self.odigraj_na_kopiji_table(tabla,potez)
            ocena = self.minimax(nova_tabla,6,-inf,+inf,False)
            
            if ocena>najbolja_ocena:
                najbolja_ocena = ocena
                najbolji_potez = potez
        
        red,kolona = tabla.indeks_u_red_kolonu(najbolji_potez.krajnji_indeks)
        pomeranje = tabla.pomeri(najbolji_potez.figura,red,kolona,najbolji_potez.pojedeni)


    def evaluacija(self, tabla):
        score = 0

        for i, figura in enumerate(tabla.tabla):
            if figura is None:
                continue

            red, kolona = tabla.indeks_u_red_kolonu(i)
            vrednost = 3 if not figura.kraljevic else 5

            if not figura.kraljevic:
                if figura.color == BLACK:
                    vrednost += red * 0.1
                else:
                    vrednost += (7 - red) * 0.1


            if kolona == 0 or kolona == 7:
                vrednost += 0.5


            if 2 <= kolona <= 5:
                vrednost += 0.3

            if figura.color == BLACK:
                score += vrednost
            else:
                score -= vrednost

        black_potezi = len(svi_potezi(tabla, BLACK))
        white_potezi = len(svi_potezi(tabla, WHITE))
        score += (black_potezi - white_potezi) * 0.05


        black_jedenja = sum(1 for p in svi_potezi(tabla, BLACK) if p.pojedeni)
        white_jedenja = sum(1 for p in svi_potezi(tabla, WHITE) if p.pojedeni)
        score += (black_jedenja - white_jedenja) * 0.3

        return score

    def odigraj_na_kopiji_table(self,tabla,potez):
        nova_tabla = self.kopija_table(tabla)
        novi_red,nova_kolona = tabla.indeks_u_red_kolonu(potez.krajnji_indeks)
        nova_figura = nova_tabla.tabla[potez.pocetni_indeks]

        pomeri = nova_tabla.pomeri(nova_figura,novi_red,nova_kolona,potez.pojedeni)
        nova_figura = nova_tabla.tabla[potez.krajnji_indeks]

        lanac=False

        for sledeci in svi_potezi(nova_tabla,nova_figura.color):
            if sledeci.figura==nova_figura and sledeci.pojedeni:
                lanac=True
        return nova_tabla,lanac
    
    def kopija_table(self,tabla):
        nova = Tabla()
        for i,f in enumerate(tabla.tabla):
            if f is not None:
                nova_figura = Figura(f.row,f.col,f.color)
                nova_figura.kraljevic = f.kraljevic
                nova.tabla[i] = nova_figura
        return nova


    def minimax(self,tabla,dubina,alfa,beta,maxFigura):
        if dubina ==0:
            return self.evaluacija(tabla)
        else:
            if maxFigura:
                potezi = svi_potezi(tabla,BLACK)
                if not potezi:
                    return self.evaluacija(tabla)
                maximum = -inf
                
                for potez in potezi:
                    nova_tabla,lanac = self.odigraj_na_kopiji_table(tabla,potez)
                    ocena = self.minimax(nova_tabla,dubina-1,alfa,beta,False)
                    maximum = max(ocena,maximum)
                    alfa = max(alfa, ocena)
                    if alfa >= beta:
                        break
                return maximum
            else:
                potezi = svi_potezi(tabla,WHITE)
                if not potezi:
                    return self.evaluacija(tabla)
                minimum = inf

                for potez in potezi:
                    nova_tabla,lanac = self.odigraj_na_kopiji_table(tabla,potez)
                    ocena = self.minimax(nova_tabla,dubina-1,alfa,beta,True)
                    beta =min(beta,ocena)
                    minimum = min(ocena,minimum)
                    if beta<=alfa:
                        break
                return minimum
