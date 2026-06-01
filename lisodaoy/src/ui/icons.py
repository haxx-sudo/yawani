"""
Procedural UI icons — drawn with Pygame (no emoji / external assets).
"""
import pygame
import math


class IconDrawer:
    """Draw small icons for buttons, cards, and HUD."""

    @staticmethod
    def draw(surface, icon_type, cx, cy, size, color, alpha=255, timer=0):
        """Draw an icon centered at (cx, cy)."""
        fn = {
            "play": IconDrawer._play,
            "quit": IconDrawer._quit,
            "monitor": IconDrawer._monitor,
            "wrench": IconDrawer._wrench,
            "coffee": IconDrawer._coffee,
            "chip": IconDrawer._chip,
            "virus": IconDrawer._virus,
            "gear": IconDrawer._gear,
            "network": IconDrawer._network,
            "workstation": IconDrawer._workstation,
            "scanner": IconDrawer._scanner,
            "star": IconDrawer._star,
            "money": IconDrawer._money,
            "code": IconDrawer._code,
            "home": IconDrawer._home,
            "trophy": IconDrawer._trophy,
            "pt_pc": IconDrawer._pt_pc,
            "pt_switch": IconDrawer._pt_switch,
            "pt_router": IconDrawer._pt_router,
            "pt_server": IconDrawer._pt_server,
            "pt_cloud": IconDrawer._pt_cloud,
            "pt_firewall": IconDrawer._pt_firewall,
            "pt_ap": IconDrawer._pt_ap,
        }.get(icon_type)
        if fn:
            fn(surface, cx, cy, size, color, alpha, timer)

    @staticmethod
    def _surf(size):
        return pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)

    @staticmethod
    def _blit(surface, surf, cx, cy, size):
        surface.blit(surf, (cx - size, cy - size))

    @staticmethod
    def _play(surface, cx, cy, size, color, alpha, timer):
        s = IconDrawer._surf(size)
        lx, ly = size, size
        pts = [
            (lx - size // 3, ly - size // 2),
            (lx + size // 2, ly),
            (lx - size // 3, ly + size // 2),
        ]
        pygame.draw.polygon(s, (*color[:3], alpha), pts)
        IconDrawer._blit(surface, s, cx, cy, size)

    @staticmethod
    def _quit(surface, cx, cy, size, color, alpha, timer):
        s = IconDrawer._surf(size)
        lx, ly = size, size
        off = size // 3
        w = max(2, size // 6)
        pygame.draw.line(s, (*color[:3], alpha),
                         (lx - off, ly - off), (lx + off, ly + off), w)
        pygame.draw.line(s, (*color[:3], alpha),
                         (lx + off, ly - off), (lx - off, ly + off), w)
        IconDrawer._blit(surface, s, cx, cy, size)

    @staticmethod
    def _monitor(surface, cx, cy, size, color, alpha, timer):
        s = IconDrawer._surf(size)
        lx, ly = size, size
        bw, bh = int(size * 1.1), int(size * 0.8)
        pygame.draw.rect(s, (55, 55, 65, alpha),
                         (lx - bw // 2, ly - bh // 2, bw, bh), border_radius=3)
        sw, sh = bw - 6, bh - 6
        pygame.draw.rect(s, (*color[:3], alpha),
                         (lx - sw // 2, ly - sh // 2, sw, sh), border_radius=2)
        pygame.draw.rect(s, (255, 255, 255, alpha // 4),
                         (lx - sw // 2 + 2, ly - sh // 2 + 2, sw // 2, sh // 3))
        for i in range(3):
            lw = sw // 3 + i * 4
            pygame.draw.line(s, (0, 255, 120, alpha // 2),
                             (lx - sw // 2 + 4, ly - sh // 2 + 6 + i * 5),
                             (lx - sw // 2 + 4 + lw, ly - sh // 2 + 6 + i * 5), 1)
        pygame.draw.rect(s, (55, 55, 65, alpha),
                         (lx - 3, ly + bh // 2, 6, 5))
        pygame.draw.rect(s, (65, 65, 75, alpha),
                         (lx - 10, ly + bh // 2 + 4, 20, 4), border_radius=2)
        IconDrawer._blit(surface, s, cx, cy, size)

    @staticmethod
    def _wrench(surface, cx, cy, size, color, alpha, timer):
        s = IconDrawer._surf(size)
        lx, ly = size, size
        c = (*color[:3], alpha)
        pygame.draw.line(s, c,
                         (lx - size // 2, ly + size // 2),
                         (lx + size // 3, ly - size // 3),
                         max(2, size // 5))
        head_x, head_y = lx + size // 3, ly - size // 3
        pygame.draw.circle(s, c, (head_x, head_y), size // 3,
                           max(2, size // 8))
        IconDrawer._blit(surface, s, cx, cy, size)

    @staticmethod
    def _coffee(surface, cx, cy, size, color, alpha, timer):
        s = IconDrawer._surf(size)
        lx, ly = size, size
        cup_w, cup_h = int(size * 0.75), int(size * 0.85)
        cup_x, cup_y = lx - cup_w // 2, ly - cup_h // 4
        pygame.draw.rect(s, (240, 240, 240, alpha),
                         (cup_x, cup_y, cup_w, cup_h), border_radius=3)
        pygame.draw.rect(s, (140, 80, 30, alpha),
                         (cup_x + 2, cup_y + cup_h // 4,
                          cup_w - 4, cup_h * 3 // 4 - 2), border_radius=2)
        pygame.draw.arc(s, (240, 240, 240, alpha),
                        (cup_x + cup_w - 2, cup_y + cup_h // 4,
                         size // 2, cup_h // 2),
                        -1.3, 1.3, max(2, size // 8))
        for i in range(2):
            wave = math.sin(timer * 2 + i * 1.5) * 3
            pygame.draw.arc(s, (255, 255, 255, alpha // 3),
                            (int(cup_x + cup_w // 4 + wave) - 2,
                             cup_y - 8, 5, 10), 0.5, 2.5, 1)
        IconDrawer._blit(surface, s, cx, cy, size)

    @staticmethod
    def _chip(surface, cx, cy, size, color, alpha, timer):
        s = IconDrawer._surf(size)
        lx, ly = size, size
        cs = int(size * 0.65)
        pygame.draw.rect(s, (*color[:3], alpha),
                         (lx - cs // 2, ly - cs // 2, cs, cs), border_radius=2)
        ds = cs // 2
        pygame.draw.rect(s, (60, 140, 120, alpha),
                         (lx - ds // 2, ly - ds // 2, ds, ds), border_radius=1)
        pin_c = (180, 170, 140, alpha)
        for i in range(-cs // 2 + 4, cs // 2 - 2, 5):
            pygame.draw.line(s, pin_c, (lx + i, ly - cs // 2),
                             (lx + i, ly - cs // 2 - 5), 1)
            pygame.draw.line(s, pin_c, (lx + i, ly + cs // 2),
                             (lx + i, ly + cs // 2 + 5), 1)
            pygame.draw.line(s, pin_c, (lx - cs // 2, ly + i),
                             (lx - cs // 2 - 5, ly + i), 1)
            pygame.draw.line(s, pin_c, (lx + cs // 2, ly + i),
                             (lx + cs // 2 + 5, ly + i), 1)
        IconDrawer._blit(surface, s, cx, cy, size)

    @staticmethod
    def _virus(surface, cx, cy, size, color, alpha, timer):
        s = IconDrawer._surf(size)
        lx, ly = size, size
        r = int(size * 0.4)
        body = (*color[:3], alpha)
        pygame.draw.circle(s, body, (lx, ly), r)
        pygame.draw.circle(s, (255, 80, 80, alpha // 2),
                           (lx - r // 3, ly - r // 3), r // 2)
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            sx = lx + int(math.cos(rad) * r)
            sy = ly + int(math.sin(rad) * r)
            ex = lx + int(math.cos(rad) * (r + 5))
            ey = ly + int(math.sin(rad) * (r + 5))
            pygame.draw.line(s, body, (sx, sy), (ex, ey), 2)
            pygame.draw.circle(s, body, (ex, ey), 2)
        for ex_off in [-r // 3, r // 3]:
            pygame.draw.circle(s, (255, 255, 200, alpha),
                               (lx + ex_off, ly - 2), 2)
            pygame.draw.circle(s, (50, 0, 0, alpha),
                               (lx + ex_off, ly - 1), 1)
        IconDrawer._blit(surface, s, cx, cy, size)

    @staticmethod
    def _gear(surface, cx, cy, size, color, alpha, timer):
        s = IconDrawer._surf(size)
        lx, ly = size, size
        r_outer, r_inner = int(size * 0.45), int(size * 0.28)
        teeth = 8
        points = []
        for i in range(teeth * 2):
            angle = (i * math.pi / teeth) + timer * 0.5
            r = r_outer if i % 2 == 0 else r_inner
            points.append((lx + int(math.cos(angle) * r),
                           ly + int(math.sin(angle) * r)))
        if len(points) >= 3:
            pygame.draw.polygon(s, (*color[:3], alpha), points)
        pygame.draw.circle(s, (30, 25, 15, alpha), (lx, ly), r_inner // 2)
        IconDrawer._blit(surface, s, cx, cy, size)

    @staticmethod
    def _network(surface, cx, cy, size, color, alpha, timer):
        s = IconDrawer._surf(size)
        lx, ly = size, size
        c = (*color[:3], alpha)
        nodes = [
            (lx, ly - size // 3),
            (lx - size // 3, ly + size // 4),
            (lx + size // 3, ly + size // 4),
            (lx, ly + size // 3),
        ]
        for a, b in [(0, 1), (0, 2), (1, 3), (2, 3), (1, 2)]:
            pygame.draw.line(s, c, nodes[a], nodes[b], max(1, size // 10))
        for nx, ny in nodes:
            pygame.draw.circle(s, c, (nx, ny), max(3, size // 6))
            pygame.draw.circle(s, (255, 255, 255, alpha // 3),
                              (nx - 1, ny - 1), max(2, size // 8))
        IconDrawer._blit(surface, s, cx, cy, size)

    @staticmethod
    def _workstation(surface, cx, cy, size, color, alpha, timer):
        s = IconDrawer._surf(size)
        lx, ly = size, size
        # Desk
        pygame.draw.rect(s, (100, 70, 45, alpha),
                         (lx - size // 2, ly + size // 6,
                          size, size // 5), border_radius=2)
        # Monitor on desk
        mw, mh = int(size * 0.7), int(size * 0.5)
        pygame.draw.rect(s, (40, 40, 50, alpha),
                         (lx - mw // 2, ly - mh // 2 - 2, mw, mh),
                         border_radius=2)
        pygame.draw.rect(s, (*color[:3], alpha),
                         (lx - mw // 2 + 3, ly - mh // 2 + 1,
                          mw - 6, mh - 6), border_radius=1)
        IconDrawer._blit(surface, s, cx, cy, size)

    @staticmethod
    def _scanner(surface, cx, cy, size, color, alpha, timer):
        s = IconDrawer._surf(size)
        lx, ly = size, size
        c = (*color[:3], alpha)
        # Lens
        pygame.draw.circle(s, c, (lx - 2, ly), size // 3, max(2, size // 8))
        pygame.draw.circle(s, (255, 255, 255, alpha // 3),
                           (lx - 4, ly - 2), size // 6)
        # Handle
        pygame.draw.rect(s, c,
                         (lx + size // 6, ly + size // 6,
                          size // 3, max(2, size // 6)),
                         border_radius=2)
        IconDrawer._blit(surface, s, cx, cy, size)

    @staticmethod
    def _star(surface, cx, cy, size, color, alpha, timer):
        s = IconDrawer._surf(size)
        lx, ly = size, size
        points = []
        for i in range(10):
            angle = -math.pi / 2 + i * math.pi / 5
            r = size * 0.45 if i % 2 == 0 else size * 0.2
            points.append((lx + int(math.cos(angle) * r),
                           ly + int(math.sin(angle) * r)))
        pygame.draw.polygon(s, (*color[:3], alpha), points)
        IconDrawer._blit(surface, s, cx, cy, size)

    @staticmethod
    def _money(surface, cx, cy, size, color, alpha, timer):
        s = IconDrawer._surf(size)
        lx, ly = size, size
        r = int(size * 0.42)
        pygame.draw.circle(s, (*color[:3], alpha), (lx, ly), r)
        pygame.draw.circle(s, (255, 230, 100, alpha // 2),
                           (lx - r // 3, ly - r // 3), r // 2)
        font = pygame.font.SysFont("Arial", max(10, size), bold=True)
        sign = font.render("$", True, (50, 35, 15, alpha))
        sr = sign.get_rect(center=(lx, ly))
        s.blit(sign, sr)
        IconDrawer._blit(surface, s, cx, cy, size)

    @staticmethod
    def _star_points(cx, cy, size):
        """Five-point star polygon vertices."""
        points = []
        for i in range(10):
            angle = -math.pi / 2 + i * math.pi / 5
            r = size * 0.9 if i % 2 == 0 else size * 0.38
            points.append((cx + int(math.cos(angle) * r),
                           cy + int(math.sin(angle) * r)))
        return points

    @staticmethod
    def draw_difficulty_row(surface, center_x, center_y, level,
                            max_stars=5, size=12,
                            filled_color=(255, 185, 50),
                            empty_color=(70, 58, 45)):
        """Draw filled + empty stars for difficulty (1–max_stars)."""
        level = max(0, min(max_stars, int(level)))
        gap = int(size * 2.2)
        row_w = (max_stars - 1) * gap
        start_x = center_x - row_w // 2

        for i in range(max_stars):
            cx = start_x + i * gap
            pts = IconDrawer._star_points(cx, center_y, size)
            if i < level:
                pygame.draw.polygon(surface, filled_color, pts)
                pygame.draw.polygon(surface,
                                    tuple(min(255, c + 40) for c in filled_color[:3]),
                                    pts, 1)
                # Highlight gleam
                pygame.draw.circle(surface, (255, 230, 160),
                                   (cx - size // 3, center_y - size // 4),
                                   max(1, size // 5))
            else:
                pygame.draw.polygon(surface, empty_color, pts, 2)

    @staticmethod
    def _home(surface, cx, cy, size, color, alpha, timer):
        s = IconDrawer._surf(size)
        lx, ly = size, size
        c = (*color[:3], alpha)
        # Roof
        pygame.draw.polygon(s, c, [
            (lx, ly - size // 2),
            (lx - size // 2, ly - size // 6),
            (lx + size // 2, ly - size // 6),
        ])
        # Body
        pygame.draw.rect(s, c,
                         (lx - size // 3, ly - size // 6,
                          size * 2 // 3, size // 2 + 2))
        # Door
        pygame.draw.rect(s, (30, 25, 15, alpha),
                         (lx - size // 8, ly + size // 8,
                          size // 4, size // 3))
        IconDrawer._blit(surface, s, cx, cy, size)

    @staticmethod
    def _trophy(surface, cx, cy, size, color, alpha, timer):
        s = IconDrawer._surf(size)
        lx, ly = size, size
        c = (*color[:3], alpha)
        # Cup
        pygame.draw.rect(s, c,
                         (lx - size // 3, ly - size // 3,
                          size * 2 // 3, size // 3), border_radius=2)
        pygame.draw.rect(s, c, (lx - size // 4, ly + 2, size // 2, 4))
        # Handles
        pygame.draw.arc(s, c,
                        (lx - size // 2 - 2, ly - size // 4,
                         size // 3, size // 2),
                        1.5, 4.5, 2)
        pygame.draw.arc(s, c,
                        (lx + size // 3, ly - size // 4,
                         size // 3, size // 2),
                        4.8, 7.8, 2)
        # Base
        pygame.draw.rect(s, c,
                         (lx - size // 2, ly + size // 3,
                          size, size // 6), border_radius=1)
        IconDrawer._blit(surface, s, cx, cy, size)

    @staticmethod
    def _code(surface, cx, cy, size, color, alpha, timer):
        s = IconDrawer._surf(size)
        lx, ly = size, size
        c = (*color[:3], alpha)
        # Brackets </>
        off = size // 4
        pygame.draw.line(s, c, (lx - off, ly - off), (lx - off // 2, ly), 2)
        pygame.draw.line(s, c, (lx - off, ly + off), (lx - off // 2, ly), 2)
        pygame.draw.line(s, c, (lx + off, ly - off), (lx + off // 2, ly), 2)
        pygame.draw.line(s, c, (lx + off, ly + off), (lx + off // 2, ly), 2)
        pygame.draw.line(s, c, (lx - 2, ly), (lx + 2, ly), 2)
        IconDrawer._blit(surface, s, cx, cy, size)

    # -------------------------------------------------------------------------
    # Cisco Packet Tracer device icons
    # -------------------------------------------------------------------------
    @staticmethod
    def _pt_pc(surface, cx, cy, size, color, alpha, timer):
        s = IconDrawer._surf(size)
        lx, ly = size, size
        c = (*color[:3], alpha)
        mw, mh = int(size * 1.0), int(size * 0.72)
        # Monitor bezel
        pygame.draw.rect(s, (40, 48, 60, alpha),
                         (lx - mw // 2, ly - mh // 2 - 3, mw, mh),
                         border_radius=3)
        # Screen
        pygame.draw.rect(s, c,
                         (lx - mw // 2 + 3, ly - mh // 2, mw - 6, mh - 8),
                         border_radius=2)
        # Screen glow
        pygame.draw.rect(s, (255, 255, 255, alpha // 5),
                         (lx - mw // 2 + 5, ly - mh // 2 + 2,
                          (mw - 10) // 2, (mh - 12) // 2))
        # Stand + base
        pygame.draw.rect(s, (60, 70, 85, alpha), (lx - 3, ly + mh // 2 - 6, 6, 6))
        pygame.draw.rect(s, (60, 70, 85, alpha),
                         (lx - mw // 4, ly + mh // 2, mw // 2, 4),
                         border_radius=2)
        IconDrawer._blit(surface, s, cx, cy, size)

    @staticmethod
    def _pt_switch(surface, cx, cy, size, color, alpha, timer):
        s = IconDrawer._surf(size)
        lx, ly = size, size
        c = (*color[:3], alpha)
        bw, bh = int(size * 1.2), int(size * 0.62)
        body = pygame.Rect(lx - bw // 2, ly - bh // 2, bw, bh)
        pygame.draw.rect(s, c, body, border_radius=4)
        pygame.draw.rect(s, (255, 255, 255, alpha // 6),
                         (body.x, body.y, bw, bh // 2), border_radius=4)
        # Bidirectional arrows (switch symbol)
        ar = (245, 250, 255, alpha)
        ay1, ay2 = ly - bh // 6, ly + bh // 6
        pygame.draw.line(s, ar, (lx - bw // 3, ay1), (lx + bw // 3, ay1), 2)
        pygame.draw.polygon(s, ar, [(lx + bw // 3, ay1),
                                    (lx + bw // 3 - 4, ay1 - 3),
                                    (lx + bw // 3 - 4, ay1 + 3)])
        pygame.draw.line(s, ar, (lx + bw // 3, ay2), (lx - bw // 3, ay2), 2)
        pygame.draw.polygon(s, ar, [(lx - bw // 3, ay2),
                                    (lx - bw // 3 + 4, ay2 - 3),
                                    (lx - bw // 3 + 4, ay2 + 3)])
        IconDrawer._blit(surface, s, cx, cy, size)

    @staticmethod
    def _pt_router(surface, cx, cy, size, color, alpha, timer):
        s = IconDrawer._surf(size)
        lx, ly = size, size
        c = (*color[:3], alpha)
        r = int(size * 0.6)
        pygame.draw.circle(s, c, (lx, ly), r)
        pygame.draw.circle(s, (255, 255, 255, alpha // 7), (lx, ly - r // 4), r)
        # Four routing arrows
        ar = (245, 250, 255, alpha)
        a = int(r * 0.55)
        # left + right
        pygame.draw.line(s, ar, (lx - a, ly - a // 2), (lx + a, ly - a // 2), 2)
        pygame.draw.polygon(s, ar, [(lx + a, ly - a // 2),
                                    (lx + a - 4, ly - a // 2 - 3),
                                    (lx + a - 4, ly - a // 2 + 3)])
        pygame.draw.line(s, ar, (lx + a, ly + a // 2), (lx - a, ly + a // 2), 2)
        pygame.draw.polygon(s, ar, [(lx - a, ly + a // 2),
                                    (lx - a + 4, ly + a // 2 - 3),
                                    (lx - a + 4, ly + a // 2 + 3)])
        IconDrawer._blit(surface, s, cx, cy, size)

    @staticmethod
    def _pt_server(surface, cx, cy, size, color, alpha, timer):
        s = IconDrawer._surf(size)
        lx, ly = size, size
        c = (*color[:3], alpha)
        bw, bh = int(size * 0.85), int(size * 1.05)
        x0, y0 = lx - bw // 2, ly - bh // 2
        pygame.draw.rect(s, c, (x0, y0, bw, bh), border_radius=3)
        # Rack units with status LEDs
        for i in range(3):
            uy = y0 + 5 + i * (bh // 3)
            pygame.draw.rect(s, (20, 28, 40, alpha),
                             (x0 + 4, uy, bw - 8, bh // 3 - 6), border_radius=1)
            led = (0, 255, 120, alpha) if (i + int(timer * 2)) % 2 == 0 else (
                255, 200, 60, alpha)
            pygame.draw.circle(s, led, (x0 + 9, uy + (bh // 3 - 6) // 2), 2)
        IconDrawer._blit(surface, s, cx, cy, size)

    @staticmethod
    def _pt_cloud(surface, cx, cy, size, color, alpha, timer):
        s = IconDrawer._surf(size)
        lx, ly = size, size
        c = (*color[:3], alpha)
        pygame.draw.circle(s, c, (lx - size // 3, ly + size // 8), size // 3)
        pygame.draw.circle(s, c, (lx + size // 3, ly + size // 8), size // 3)
        pygame.draw.circle(s, c, (lx, ly - size // 6), int(size * 0.38))
        pygame.draw.rect(s, c,
                         (lx - size // 2, ly, size, size // 3),
                         border_radius=4)
        pygame.draw.circle(s, (255, 255, 255, alpha // 6),
                           (lx, ly - size // 6), int(size * 0.32))
        IconDrawer._blit(surface, s, cx, cy, size)

    @staticmethod
    def _pt_firewall(surface, cx, cy, size, color, alpha, timer):
        s = IconDrawer._surf(size)
        lx, ly = size, size
        c = (*color[:3], alpha)
        bw, bh = int(size * 1.1), int(size * 0.9)
        x0, y0 = lx - bw // 2, ly - bh // 2
        # Brick wall
        brick_h = bh // 4
        for row in range(4):
            ry = y0 + row * brick_h
            offset = (bw // 4) if row % 2 else 0
            pygame.draw.rect(s, c, (x0, ry, bw, brick_h - 1), border_radius=1)
            for bx in range(-1, 3):
                gx = x0 + offset + bx * (bw // 2)
                pygame.draw.line(s, (30, 20, 18, alpha),
                                 (gx, ry), (gx, ry + brick_h - 1), 1)
            pygame.draw.line(s, (30, 20, 18, alpha),
                             (x0, ry), (x0 + bw, ry), 1)
        # Flame accent
        fl = (255, 140, 40, alpha)
        pygame.draw.polygon(s, fl, [
            (lx, y0 - 6), (lx + 5, y0 + 2), (lx, y0 + 5), (lx - 5, y0 + 2)])
        IconDrawer._blit(surface, s, cx, cy, size)

    @staticmethod
    def _pt_ap(surface, cx, cy, size, color, alpha, timer):
        s = IconDrawer._surf(size)
        lx, ly = size, size
        c = (*color[:3], alpha)
        # Dome base
        pygame.draw.rect(s, c, (lx - size // 2, ly + size // 6,
                                size, size // 4), border_radius=3)
        pygame.draw.circle(s, c, (lx, ly + size // 6), size // 3)
        # Wi-Fi waves
        wv = (245, 250, 255, alpha)
        for i, rad in enumerate((size // 4, size // 2, int(size * 0.7))):
            pygame.draw.arc(s, wv,
                            (lx - rad, ly - rad // 2, rad * 2, rad * 2),
                            3.6, 5.8, 2)
        pygame.draw.circle(s, wv, (lx, ly + size // 6), max(2, size // 8))
        IconDrawer._blit(surface, s, cx, cy, size)
