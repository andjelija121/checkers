import pygame
from konstante import SQUARE_SIZE, GOLD, LIGHT_GOLD


class Figura:
    PADDING = 10
    OUTLINE = 2

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.kraljevic = False
        self.marko=False
        self.relikvije = []
        self.oklop = 0
        self.kolebanje = 0

    def postani_kraljevic(self):
        self.kraljevic = True

    def ima_relikviju(self,kljuc):
        for r in self.relikvije:
            if r.kljuc == kljuc:
                return True
        return False

    def nacrtaj(self, prozor):
        radius = SQUARE_SIZE // 2 - self.PADDING
        x = self.col * SQUARE_SIZE + SQUARE_SIZE // 2
        y = self.row * SQUARE_SIZE + SQUARE_SIZE // 2

        is_white = self.color == (232, 216, 192)
        border_color = (196, 168, 130) if is_white else (10, 6, 6)
        shine_color = (255, 255, 255, 115) if is_white else (255, 255, 255, 30)

        shadow_surf = pygame.Surface((radius * 2 + 10, radius * 2 + 10), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surf, (0, 0, 0, 90), (radius + 5, radius + 8), radius + self.OUTLINE)
        prozor.blit(shadow_surf, (x - radius - 2, y - radius - 3))

        pygame.draw.circle(prozor, border_color, (x, y), radius + self.OUTLINE)
        pygame.draw.circle(prozor, self.color, (x, y), radius)

        shine_surf = pygame.Surface((radius, radius), pygame.SRCALPHA)
        shine_r = max(1, radius // 4)
        pygame.draw.circle(shine_surf, shine_color, (shine_r, shine_r), shine_r)
        prozor.blit(shine_surf, (x - radius // 2, y - radius // 2))

        if self.kraljevic:
            self.nacrtaj_kraljevica(prozor, x, y, radius, is_white)

        if self.marko:
            self.nacrtaj_marka(prozor, x, y, radius)

        self.nacrtaj_oznake_relikvija(prozor, x, y, radius)

    def nacrtaj_oznake_relikvija(self, prozor, x, y, radius):
        if not self.relikvije:
            return

        jedinstvene_relikvije = []
        vidjeni_kljucevi = set()

        for relikvija in self.relikvije:
            if relikvija.kljuc in vidjeni_kljucevi:
                continue
            vidjeni_kljucevi.add(relikvija.kljuc)
            jedinstvene_relikvije.append(relikvija)

        broj_oznaka = len(jedinstvene_relikvije)
        razmak = 18
        pocetak_x = x - ((broj_oznaka - 1) * razmak) // 2
        oznaka_y = y + radius - 1
        font = pygame.font.SysFont("arial", 11, bold=True)

        for i, relikvija in enumerate(jedinstvene_relikvije):
            centar = (pocetak_x + i * razmak, oznaka_y)
            boja = getattr(relikvija, "boja", GOLD)
            oznaka = getattr(relikvija, "oznaka", "?")

            pygame.draw.circle(prozor, (32, 22, 18), centar, 9)
            pygame.draw.circle(prozor, boja, centar, 7)
            tekst = font.render(oznaka, True, (255, 250, 235))
            prozor.blit(tekst, tekst.get_rect(center=centar))

    def nacrtaj_marka(self, prozor, x, y, radius):
        pygame.draw.circle(prozor, (175, 28, 28), (x, y), radius - 5, 4)
        font = pygame.font.SysFont("arial", 17, bold=True)
        oznaka = font.render("М", True, (255, 235, 170))
        prozor.blit(oznaka, oznaka.get_rect(center=(x, y + 17)))

    def nacrtaj_kraljevica(self, prozor, x, y, radius, is_white):
        ring_r = int(radius * 0.62)
        pygame.draw.circle(prozor, GOLD, (x, y), ring_r, 2)

        crown_color = (255, 215, 0) if is_white else (212, 160, 0)
        crown_border = (184, 134, 11) if is_white else (139, 105, 20)

        crown_w = radius * 0.72
        crown_h = radius * 0.42
        crown_y = y - radius * 0.08
        spikes = 5

        points = [(x - crown_w, crown_y + crown_h * 0.45)]

        for i in range(spikes * 2 + 1):
            px = x - crown_w + (crown_w * 2) * (i / (spikes * 2))

            if i % 2 == 0:
                py = crown_y - crown_h * (0.55 + 0.2 * (i == spikes))
            else:
                py = crown_y + crown_h * 0.08

            points.append((px, py))

        points.append((x + crown_w, crown_y + crown_h * 0.45))

        pygame.draw.polygon(prozor, crown_color, points)
        pygame.draw.polygon(prozor, crown_border, points, 1)

        gem_surf = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(gem_surf, (*LIGHT_GOLD, 255), (5, 5), 4)
        prozor.blit(gem_surf, (x - 5, int(crown_y - crown_h * 0.55) - 5))
