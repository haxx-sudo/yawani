"""
On-screen controls for touch devices (menu + mute).
"""
import pygame
from src.constants import *
class MobileControls:
    """Top-corner touch buttons replacing keyboard shortcuts."""

    BTN = 48

    def __init__(self, game):
        self.game = game
        y = SCREEN_HEIGHT - 8 - self.BTN
        self.menu_rect = pygame.Rect(8, y, self.BTN, self.BTN)
        self.mute_rect = pygame.Rect(SCREEN_WIDTH - 8 - self.BTN, y,
                                     self.BTN, self.BTN)
        self.menu_pressed = False
        self.mute_pressed = False

    def handle_event(self, event):
        """Return True if the event was consumed."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.menu_rect.collidepoint(event.pos):
                self.menu_pressed = True
                return True
            if self.mute_rect.collidepoint(event.pos):
                self.mute_pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.menu_pressed:
                self.menu_pressed = False
                self._go_menu()
                return True
            if self.mute_pressed:
                self.mute_pressed = False
                self._toggle_mute()
                return True
        return False

    def _go_menu(self):
        scene = self.game.current_scene
        if scene == SCENE_MENU:
            return
        if scene == SCENE_CAFE:
            self.game.change_scene(SCENE_MENU)
            self.game.sounds.play("click")
        elif scene in (SCENE_UPGRADE, SCENE_GAMEOVER, SCENE_PACKET_TRACER):
            self.game.change_scene(SCENE_MENU)
            self.game.sounds.play("click")

    def _toggle_mute(self):
        if self.game.sounds.volume > 0:
            self.game.sounds.set_volume(0)
        else:
            self.game.sounds.set_volume(0.3)
        self.game.sounds.play("click")

    def draw(self, surface, assets):
        for rect in (self.menu_rect, self.mute_rect):
            pygame.draw.rect(surface, COLOR_PANEL_LIGHT, rect, border_radius=10)
            pygame.draw.rect(surface, COLOR_PANEL_BORDER, rect,
                             border_radius=10, width=2)

        mx, my = self.menu_rect.centerx, self.menu_rect.centery
        for dy in (-8, 0, 8):
            pygame.draw.line(surface, COLOR_CREAM,
                             (mx - 12, my + dy), (mx + 12, my + dy), 2)

        sx, sy = self.mute_rect.centerx, self.mute_rect.centery
        vol = self.game.sounds.volume
        color = COLOR_GREEN if vol > 0 else COLOR_GRAY
        pygame.draw.polygon(surface, color,
                            [(sx - 6, sy - 5), (sx - 2, sy - 5),
                             (sx + 6, sy - 10), (sx + 6, sy + 10),
                             (sx - 2, sy + 5), (sx - 6, sy + 5)])
        if vol > 0:
            pygame.draw.arc(surface, color,
                            (sx + 4, sy - 10, 16, 20), -0.8, 0.8, 2)
