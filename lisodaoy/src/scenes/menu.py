"""
Title/Menu scene — premium animated start screen with drawn icons.
"""
import pygame
import math
import random
from src.constants import *
from src.ui.button import Button
from src.ui.icons import IconDrawer


class MenuScene:
    """Main menu with animated icons, atmospheric background, and polish."""

    def __init__(self, game):
        self.game = game
        self.timer = 0

        # Floating tech particles
        self.particles = []
        for _ in range(60):
            self.particles.append({
                "x": random.randint(0, SCREEN_WIDTH),
                "y": random.randint(0, SCREEN_HEIGHT),
                "speed": random.uniform(8, 35),
                "size": random.randint(1, 4),
                "color": random.choice([
                    COLOR_CYAN, COLOR_AMBER, COLOR_GREEN, COLOR_MAGENTA,
                    COLOR_ORANGE, COLOR_PURPLE,
                ]),
                "alpha_offset": random.uniform(0, math.pi * 2),
                "drift": random.uniform(-8, 8),
            })

        # Floating icon objects (orbit around title area)
        self.floating_icons = []
        icon_defs = [
            {"type": "monitor", "orbit_r": 220, "speed": 0.3, "offset": 0},
            {"type": "wrench", "orbit_r": 250, "speed": -0.25, "offset": 1.2},
            {"type": "coffee", "orbit_r": 200, "speed": 0.35, "offset": 2.5},
            {"type": "chip", "orbit_r": 240, "speed": -0.2, "offset": 3.8},
            {"type": "virus", "orbit_r": 230, "speed": 0.28, "offset": 5.0},
            {"type": "gear", "orbit_r": 210, "speed": -0.32, "offset": 6.1},
        ]
        for d in icon_defs:
            self.floating_icons.append(d)

        # Buttons — width matches the feature-card row below for alignment
        btn_w = 452
        btn_h = 62
        btn_x = SCREEN_WIDTH // 2 - btn_w // 2
        self.play_button = Button(
            btn_x, 430, btn_w, btn_h, "START GAME",
            font_name="heading", accent_color=COLOR_GREEN,
            icon_type="play", icon_size=16,
            callback=self._start_game
        )
        self.pt_button = Button(
            btn_x, 500, btn_w, btn_h, "PACKET TRACER",
            font_name="heading", accent_color=COLOR_CYAN,
            icon_type="network", icon_size=16,
            callback=self._start_packet_tracer,
        )
        self.quit_button = Button(
            btn_x, 570, btn_w, btn_h, "QUIT",
            font_name="heading", accent_color=COLOR_RED,
            icon_type="quit", icon_size=16,
            callback=self._quit_game
        )

    def enter(self, **kwargs):
        self.timer = 0

    def _start_game(self):
        self.game.start_new_game()

    def _start_packet_tracer(self):
        self.game.start_packet_tracer()

    def _quit_game(self):
        self.game.running = False

    def handle_event(self, event):
        self.play_button.handle_event(event)
        self.pt_button.handle_event(event)
        self.quit_button.handle_event(event)

    def update(self, dt):
        self.timer += dt
        self.play_button.update(dt)
        self.pt_button.update(dt)
        self.quit_button.update(dt)

        for p in self.particles:
            p["y"] += p["speed"] * dt
            p["x"] += p["drift"] * dt
            if p["y"] > SCREEN_HEIGHT + 5:
                p["y"] = -5
                p["x"] = random.randint(0, SCREEN_WIDTH)
            if p["x"] < -5 or p["x"] > SCREEN_WIDTH + 5:
                p["x"] = random.randint(0, SCREEN_WIDTH)
                p["y"] = -5

    # =========================================================================
    # Feature cards at bottom
    # =========================================================================
    def _draw_feature_cards(self, screen, assets):
        """Draw 4 small feature cards showing mini-game types."""
        card_data = [
            ("wrench", "Hardware", "Swap components", COLOR_ORANGE),
            ("monitor", "Software", "Fix the code", COLOR_CYAN),
            ("virus", "Virus", "Scan & destroy", COLOR_RED),
            ("network", "Network", "Trace the route", COLOR_GREEN),
        ]
        # Match the button row width (452) so edges line up
        total_w = 452
        gap = 12
        card_w = (total_w - (len(card_data) - 1) * gap) // len(card_data)
        card_h = 75
        start_x = SCREEN_WIDTH // 2 - total_w // 2
        card_y = 640

        for i, (icon_type, title, desc, color) in enumerate(card_data):
            cx = start_x + i * (card_w + gap)
            rect = pygame.Rect(cx, card_y, card_w, card_h)

            # Card background
            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            pygame.draw.rect(card_surf, (35, 28, 20, 180),
                             (0, 0, card_w, card_h), border_radius=8)
            # Color accent line at top
            pygame.draw.rect(card_surf, (*color[:3], 200),
                             (6, 2, card_w - 12, 3), border_radius=2)
            # Border
            pygame.draw.rect(card_surf, (*color[:3], 80),
                             (0, 0, card_w, card_h), border_radius=8, width=1)
            screen.blit(card_surf, rect.topleft)

            # Icon
            IconDrawer.draw(screen, icon_type,
                            cx + card_w // 2, card_y + 22,
                            14, color, timer=self.timer)

            # Title
            font_sm = assets.get_font("small")
            t_surf = font_sm.render(title, True, COLOR_CREAM)
            screen.blit(t_surf,
                        (cx + card_w // 2 - t_surf.get_width() // 2,
                         card_y + 36))

            # Desc
            font_t = assets.get_font("tiny")
            d_surf = font_t.render(desc, True, COLOR_TEXT_DIM)
            screen.blit(d_surf,
                        (cx + card_w // 2 - d_surf.get_width() // 2,
                         card_y + 55))

    # =========================================================================
    # Main Draw
    # =========================================================================
    def draw(self, screen):
        # === Background gradient ===
        for y in range(SCREEN_HEIGHT):
            t = y / SCREEN_HEIGHT
            r = int(25 + 18 * t)
            g = int(18 + 10 * t)
            b = int(12 + 5 * t)
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        # === Grid pattern (subtle) ===
        grid_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for gx in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(grid_surf, (255, 255, 255, 5),
                             (gx, 0), (gx, SCREEN_HEIGHT))
        for gy in range(0, SCREEN_HEIGHT, 50):
            pygame.draw.line(grid_surf, (255, 255, 255, 5),
                             (0, gy), (SCREEN_WIDTH, gy))
        screen.blit(grid_surf, (0, 0))

        # === Floating particles ===
        for p in self.particles:
            alpha = int(100 + 120 * math.sin(
                self.timer * 2 + p["alpha_offset"]))
            alpha = max(20, min(255, alpha))
            s = p["size"]
            psurf = pygame.Surface((s * 2 + 2, s * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(psurf, (*p["color"][:3], alpha),
                               (s + 1, s + 1), s)
            # Tiny glow
            if s >= 2:
                pygame.draw.circle(psurf, (*p["color"][:3], alpha // 4),
                                   (s + 1, s + 1), s + 2)
            screen.blit(psurf, (int(p["x"]) - s - 1, int(p["y"]) - s - 1))

        # === Floating icons orbiting around center ===
        center_x = SCREEN_WIDTH // 2
        center_y = 230
        for icon in self.floating_icons:
            angle = self.timer * icon["speed"] + icon["offset"]
            ix = center_x + int(math.cos(angle) * icon["orbit_r"])
            iy = center_y + int(math.sin(angle) * icon["orbit_r"] * 0.35)
            # Fade based on vertical position (further = dimmer)
            depth = (math.sin(angle) + 1) / 2  # 0 to 1
            alpha = int(60 + 140 * (1 - depth))
            icon_size = int(22 + 10 * (1 - depth))

            draw_fn = {
                "monitor": lambda s, x, y, sz, a: IconDrawer.draw(
                    s, "monitor", x, y, sz, COLOR_CYAN, a, self.timer),
                "wrench": lambda s, x, y, sz, a: IconDrawer.draw(
                    s, "wrench", x, y, sz, COLOR_ORANGE, a, self.timer),
                "coffee": lambda s, x, y, sz, a: IconDrawer.draw(
                    s, "coffee", x, y, sz, COLOR_AMBER, a, self.timer),
                "chip": lambda s, x, y, sz, a: IconDrawer.draw(
                    s, "chip", x, y, sz, COLOR_GREEN, a, self.timer),
                "virus": lambda s, x, y, sz, a: IconDrawer.draw(
                    s, "virus", x, y, sz, COLOR_RED, a, self.timer),
                "gear": lambda s, x, y, sz, a: IconDrawer.draw(
                    s, "gear", x, y, sz, COLOR_AMBER, a, self.timer),
            }.get(icon["type"])
            if draw_fn:
                draw_fn(screen, ix, iy, icon_size, alpha)

        assets = self.game.assets

        # === Title area (aligned as one centered block) ===
        center_x = SCREEN_WIDTH // 2
        title_y = int(160 + math.sin(self.timer * 1.2) * 6)
        cafe_y = title_y + 58

        font_title = assets.get_font("title")
        font_huge = assets.get_font("huge")
        w_top = font_title.size("TECH SUPPORT")[0]
        w_bot = font_huge.size("CAFÉ")[0]
        block_w = max(w_top, w_bot)
        line_w = block_w + 48

        # Large glow behind title block
        glow_surf = pygame.Surface((line_w + 80, 180), pygame.SRCALPHA)
        glow_alpha = int(25 + 15 * math.sin(self.timer * 1.8))
        pygame.draw.ellipse(glow_surf, (255, 185, 50, glow_alpha),
                            glow_surf.get_rect())
        screen.blit(glow_surf, (center_x - glow_surf.get_width() // 2,
                                title_y - 55))

        # Decorative lines matched to title width
        line_y = title_y - 35
        line_surf = pygame.Surface((line_w, 3), pygame.SRCALPHA)
        for lx in range(line_w):
            t = 1 - abs(lx - line_w // 2) / max(1, line_w // 2)
            a = int(120 * t)
            pygame.draw.line(line_surf, (255, 200, 80, a),
                             (lx, 0), (lx, 2))
        screen.blit(line_surf, (center_x - line_w // 2, line_y))

        assets.draw_text_shadow(screen, "TECH SUPPORT", "title",
                                center_x, title_y, COLOR_CREAM, center=True)
        assets.draw_text_shadow(screen, "CAFÉ", "huge",
                                center_x, cafe_y, COLOR_AMBER, center=True)

        cup_gap = w_bot // 2 + 28
        for side in (-1, 1):
            IconDrawer.draw(screen, "coffee", center_x + side * cup_gap,
                            cafe_y, 20, COLOR_AMBER, 160, self.timer)

        line_y2 = cafe_y + 35
        screen.blit(line_surf, (center_x - line_w // 2, line_y2))

        # === Subtitle ===
        sub_alpha = int(180 + 60 * math.sin(self.timer * 2.5))
        font = assets.get_font("menu_sub")
        sub = font.render("Diagnose problems. Fix computers. Save the day.",
                          True, COLOR_TEXT_DIM)
        sub.set_alpha(sub_alpha)
        sub_rect = sub.get_rect(center=(center_x, cafe_y + 60))
        screen.blit(sub, sub_rect)

        # === High score ===
        if self.game.high_score > 0:
            hs_y = 420
            # Trophy icon
            IconDrawer.draw(screen, "star",
                            SCREEN_WIDTH // 2 - 120, hs_y, 14,
                            COLOR_AMBER_GLOW, timer=self.timer)
            assets.draw_text_shadow(
                screen, f"Best Score: ${self.game.high_score}",
                "body", SCREEN_WIDTH // 2, hs_y, COLOR_AMBER_GLOW,
                center=True)
            IconDrawer.draw(screen, "star",
                            SCREEN_WIDTH // 2 + 120, hs_y, 14,
                            COLOR_AMBER_GLOW, timer=self.timer)

        # === Buttons ===
        self.play_button.draw(screen, assets)
        self.pt_button.draw(screen, assets)
        self.quit_button.draw(screen, assets)

        # === Feature cards ===
        self._draw_feature_cards(screen, assets)

        # === Controls hint ===
        controls_y = SCREEN_HEIGHT - 35
        font_t = assets.get_font("tiny")
        if self.game.mobile_display.mobile:
            hint = "Tap to play  |  Top buttons: Menu & Mute"
        else:
            hint = "ESC: Menu  |  M: Mute  |  Mouse: Play"
        ctrl = font_t.render(hint, True, (80, 65, 50))
        ctrl_rect = ctrl.get_rect(center=(SCREEN_WIDTH // 2, controls_y))
        screen.blit(ctrl, ctrl_rect)

        # Version
        ver = font_t.render("v1.0", True, (55, 45, 35))
        screen.blit(ver, (SCREEN_WIDTH - 40, SCREEN_HEIGHT - 22))
