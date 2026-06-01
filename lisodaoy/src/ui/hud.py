"""
Heads-up display — shows money, reputation, level, and timer.
"""
import pygame
from src.constants import *


class HUD:
    """Renders the in-game HUD bar at the top of the screen."""

    def __init__(self):
        self.flash_money = 0  # flash timer when money changes
        self.flash_rep = 0
        self.last_money = 0
        self.last_rep = 0

    def update(self, dt, money, reputation):
        """Update flash effects."""
        if money != self.last_money:
            self.flash_money = 0.5
            self.last_money = money
        if reputation != self.last_rep:
            self.flash_rep = 0.5
            self.last_rep = reputation

        self.flash_money = max(0, self.flash_money - dt)
        self.flash_rep = max(0, self.flash_rep - dt)

    def draw(self, surface, assets, money, reputation, level,
             customers_served, customers_total, level_time=None):
        """Draw the HUD bar."""
        # Background bar — vertical gradient for depth
        bar_h = 55
        bar_surf = pygame.Surface((SCREEN_WIDTH, bar_h), pygame.SRCALPHA)
        for y in range(bar_h):
            t = y / (bar_h - 1)
            a = int(232 - 40 * t)
            shade = int(26 - 12 * t)
            pygame.draw.line(bar_surf, (shade, shade - 4, shade - 8, a),
                             (0, y), (SCREEN_WIDTH, y))
        # Glowing bottom accent line
        glow = pygame.Surface((SCREEN_WIDTH, 8), pygame.SRCALPHA)
        for i in range(8):
            a = int(60 * (1 - i / 8))
            pygame.draw.line(glow, (*COLOR_AMBER, a),
                             (0, 7 - i), (SCREEN_WIDTH, 7 - i))
        bar_surf.blit(glow, (0, bar_h - 8))
        pygame.draw.line(bar_surf, COLOR_AMBER_GLOW,
                         (0, bar_h - 1), (SCREEN_WIDTH, bar_h - 1), 2)
        surface.blit(bar_surf, (0, 0))

        # Money
        money_color = COLOR_AMBER_GLOW if self.flash_money > 0 else COLOR_AMBER
        assets.draw_text_shadow(surface, f"${money}",
                                "hud", 20, 28, money_color, center=True)

        # Reputation bar
        rep_x = 160
        rep_label_color = COLOR_CYAN_GLOW if self.flash_rep > 0 else COLOR_CYAN
        assets.draw_text_shadow(surface, "REP", "small", rep_x, 12,
                                COLOR_TEXT_DIM)
        assets.draw_progress_bar(surface, rep_x + 40, 12, 120, 14,
                                 reputation / MAX_REPUTATION,
                                 COLOR_CYAN if reputation > 25 else COLOR_RED)
        # Rep value
        font = assets.get_font("tiny")
        rep_text = font.render(f"{int(reputation)}", True, COLOR_WHITE)
        surface.blit(rep_text, (rep_x + 42 + 50, 14))

        # Level (+ rush timer when active)
        level_label = f"Lv{level} {get_level_display_name(level)}"
        if level_time is not None:
            timer_color = COLOR_TEXT if level_time > 30 else COLOR_RED
            assets.draw_text_shadow(
                surface, level_label, "small",
                SCREEN_WIDTH // 2, 14, COLOR_TEXT_DIM, center=True)
            assets.draw_text_shadow(
                surface, f"{int(max(0, level_time))}s",
                "hud", SCREEN_WIDTH // 2, 32, timer_color, center=True)
        else:
            assets.draw_text_shadow(
                surface, level_label, "hud",
                SCREEN_WIDTH // 2, 28, COLOR_CREAM, center=True)

        # Customer progress
        progress_text = f"Served: {customers_served}/{customers_total}"
        assets.draw_text_shadow(surface, progress_text,
                                "small", SCREEN_WIDTH - 250, 12,
                                COLOR_TEXT_DIM)
        progress = customers_served / max(1, customers_total)
        assets.draw_progress_bar(surface, SCREEN_WIDTH - 250, 32, 140, 10,
                                 progress, COLOR_GREEN)

