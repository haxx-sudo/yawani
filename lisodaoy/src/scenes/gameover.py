"""
Game Over scene — shows final stats and allows restart.
"""
import pygame
import math
from src.constants import *
from src.ui.button import Button
from src.ui.icons import IconDrawer


class GameOverScene:
    """Game over screen with stats and retry option."""

    def __init__(self, game):
        self.game = game
        self.won = False
        self.timer = 0

        btn_w = 260
        btn_x = SCREEN_WIDTH // 2 - btn_w // 2
        self.retry_button = Button(
            btn_x, 520, btn_w, 55, "PLAY AGAIN",
            font_name="heading", accent_color=COLOR_GREEN,
            icon_type="play", icon_size=16,
            callback=self._retry,
        )
        self.menu_button = Button(
            btn_x, 590, btn_w, 55, "MAIN MENU",
            font_name="heading", accent_color=COLOR_AMBER,
            icon_type="home", icon_size=16,
            callback=self._menu,
        )

    def enter(self, won=False, **kwargs):
        self.won = won
        self.timer = 0

        if self.game.money > self.game.high_score:
            self.game.high_score = self.game.money

    def _retry(self):
        self.game.start_new_game()

    def _menu(self):
        self.game.change_scene(SCENE_MENU)

    def handle_event(self, event):
        self.retry_button.handle_event(event)
        self.menu_button.handle_event(event)

    def update(self, dt):
        self.timer += dt
        self.retry_button.update(dt)
        self.menu_button.update(dt)

    def _draw_stat_row(self, screen, assets, panel_rect, y, icon_type,
                      label, value, icon_color):
        """Draw a stat line with procedural icon + label + value."""
        icon_x = panel_rect.x + 32
        icon_y = y + 14
        IconDrawer.draw(screen, icon_type, icon_x, icon_y, 12,
                        icon_color, timer=self.timer)

        font_body = assets.get_font("body")
        label_surf = font_body.render(label, True, COLOR_TEXT_DIM)
        screen.blit(label_surf, (panel_rect.x + 56, y + 4))

        font_val = assets.get_font("heading")
        val_surf = font_val.render(value, True, COLOR_AMBER)
        val_rect = val_surf.get_rect(right=panel_rect.right - 20, centery=y + 14)
        screen.blit(val_surf, val_rect)

    def draw(self, screen):
        screen.fill(COLOR_BG)
        assets = self.game.assets
        center_x = SCREEN_WIDTH // 2

        for i in range(20):
            x = (i * 97 + int(self.timer * 20)) % SCREEN_WIDTH
            y = 100 + i * 35
            size = 3 + i % 4
            alpha = 30 + int(20 * math.sin(self.timer * 2 + i))
            surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            color = COLOR_GREEN if self.won else COLOR_RED
            pygame.draw.circle(surf, (*color[:3], alpha), (size, size), size)
            screen.blit(surf, (x, y))

        if self.won:
            title_color = COLOR_AMBER
            title_text = "CONGRATULATIONS!"
            sub_text = f"You completed all {MAX_LEVEL} levels!"
        else:
            title_color = COLOR_RED
            title_text = "GAME OVER"
            sub_text = "Your reputation hit rock bottom!"

        glow_surf = pygame.Surface((500, 80), pygame.SRCALPHA)
        glow_a = int(30 + 15 * math.sin(self.timer * 2))
        pygame.draw.ellipse(glow_surf, (*title_color[:3], glow_a),
                            glow_surf.get_rect())
        screen.blit(glow_surf, (center_x - 250, 90))

        if self.won:
            IconDrawer.draw(screen, "star", center_x - 200, 115, 16,
                            COLOR_AMBER_GLOW, timer=self.timer)
            IconDrawer.draw(screen, "star", center_x + 200, 115, 16,
                            COLOR_AMBER_GLOW, timer=self.timer)

        assets.draw_text_shadow(screen, title_text, "title",
                                center_x, 120, title_color, center=True)
        assets.draw_text_shadow(screen, sub_text, "body",
                                center_x, 180, COLOR_TEXT_DIM, center=True)

        panel_rect = pygame.Rect(center_x - 180, 220, 360, 260)
        assets.draw_panel(screen, panel_rect, alpha=220)

        cafe_level = self.game.scenes[SCENE_CAFE].level
        stats = [
            ("money", "Total Earned", f"${self.game.money}", COLOR_AMBER),
            ("star", "Final Reputation", f"{int(self.game.reputation)}", COLOR_CYAN),
            ("chip", "Level Reached", f"{cafe_level}", COLOR_GREEN),
            ("trophy", "High Score", f"${self.game.high_score}", COLOR_AMBER_GLOW),
        ]

        y = panel_rect.y + 25
        for icon_type, label, value, icon_color in stats:
            self._draw_stat_row(screen, assets, panel_rect, y,
                                icon_type, label, value, icon_color)
            y += 55

        if self.game.money >= self.game.high_score and self.game.money > 0:
            hs_y = 490
            IconDrawer.draw(screen, "trophy", center_x - 130, hs_y, 14,
                            COLOR_AMBER_GLOW, timer=self.timer)
            IconDrawer.draw(screen, "star", center_x - 155, hs_y, 10,
                            COLOR_AMBER, timer=self.timer)
            IconDrawer.draw(screen, "star", center_x + 155, hs_y, 10,
                            COLOR_AMBER, timer=self.timer)
            assets.draw_text_shadow(screen, "NEW HIGH SCORE!",
                                    "body", center_x, hs_y,
                                    COLOR_AMBER_GLOW, center=True)
            IconDrawer.draw(screen, "trophy", center_x + 130, hs_y, 14,
                            COLOR_AMBER_GLOW, timer=self.timer)

        self.retry_button.draw(screen, assets)
        self.menu_button.draw(screen, assets)
