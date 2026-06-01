"""
Reusable button widget with hover effects and glow animation.
"""
import pygame
from src.constants import *
from src.ui.icons import IconDrawer
from src.utils.mobile import is_mobile, touch_padding


class Button:
    """Interactive button with hover glow and press animation."""

    def __init__(self, x, y, width, height, text, font_name="body",
                 color=COLOR_PANEL_LIGHT, hover_color=COLOR_PANEL_HOVER,
                 text_color=COLOR_TEXT, border_color=COLOR_PANEL_BORDER,
                 accent_color=COLOR_AMBER, border_radius=10,
                 callback=None, enabled=True, icon_type=None, icon_size=18):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_name = font_name
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_color = border_color
        self.accent_color = accent_color
        self.border_radius = border_radius
        self.callback = callback
        self.enabled = enabled
        self.icon_type = icon_type
        self.icon_size = icon_size
        self.icon_timer = 0.0

        self.hovered = False
        self.pressed = False
        self.press_offset = 0
        self.glow_alpha = 0
        self.glow_dir = 1

    def _hit_rect(self):
        pad = touch_padding()
        return self.rect.inflate(pad, pad) if pad else self.rect

    def handle_event(self, event):
        """Handle mouse/touch events. Returns True if clicked."""
        if not self.enabled:
            return False

        hit = self._hit_rect()
        if event.type == pygame.MOUSEMOTION:
            self.hovered = hit.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if hit.collidepoint(event.pos):
                self.pressed = True
                self.hovered = True
                if is_mobile():
                    if self.callback:
                        self.callback()
                    return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed:
                self.pressed = False
                if is_mobile():
                    return False
                on_target = hit.collidepoint(event.pos)
                if on_target:
                    if self.callback:
                        self.callback()
                    return True
            self.pressed = False
        return False

    def update(self, dt):
        """Update hover glow animation."""
        self.icon_timer += dt
        if self.hovered:
            self.glow_alpha = min(80, self.glow_alpha + 300 * dt)
        else:
            self.glow_alpha = max(0, self.glow_alpha - 200 * dt)

        if self.pressed:
            self.press_offset = min(3, self.press_offset + 30 * dt)
        else:
            self.press_offset = max(0, self.press_offset - 20 * dt)

    def draw(self, surface, assets):
        """Draw the button."""
        offset = int(self.press_offset)
        draw_rect = self.rect.move(0, offset)

        # Shadow
        if not self.pressed:
            shadow_rect = self.rect.move(3, 3)
            shadow_surf = pygame.Surface(
                (shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, (0, 0, 0, 50),
                             shadow_surf.get_rect(),
                             border_radius=self.border_radius)
            surface.blit(shadow_surf, shadow_rect.topleft)

        # Outer bloom when hovered
        if self.glow_alpha > 0 and self.enabled:
            assets.draw_glow_rect(
                surface, draw_rect, self.accent_color,
                border_radius=self.border_radius,
                layers=5, intensity=int(self.glow_alpha * 0.55))

        # Button background (vertical gradient)
        bg_color = self.hover_color if self.hovered else self.color
        if not self.enabled:
            bg_color = COLOR_GRAY_DARK
        top_c = assets._lighten(bg_color, 22)
        bot_c = assets._darken(bg_color, 14)
        assets.gradient_round_rect(surface, draw_rect, top_c, bot_c,
                                   border_radius=self.border_radius)

        # Top sheen highlight
        sheen = pygame.Surface((draw_rect.width - 6, draw_rect.height // 2),
                               pygame.SRCALPHA)
        sheen.fill((255, 255, 255, 22 if self.enabled else 8))
        surface.blit(sheen, (draw_rect.x + 3, draw_rect.y + 2))

        # Accent line at top
        accent = self.accent_color if self.enabled else COLOR_GRAY
        accent_rect = pygame.Rect(draw_rect.x + 8, draw_rect.y + 2,
                                  draw_rect.width - 16, 3)
        pygame.draw.rect(surface, accent, accent_rect, border_radius=2)

        # Inner glow tint overlay
        if self.glow_alpha > 0 and self.enabled:
            glow = pygame.Surface(
                (draw_rect.width, draw_rect.height), pygame.SRCALPHA)
            glow_color = (*self.accent_color, int(self.glow_alpha * 0.45))
            pygame.draw.rect(glow, glow_color, glow.get_rect(),
                             border_radius=self.border_radius)
            surface.blit(glow, draw_rect.topleft)

        # Border
        border = self.accent_color if self.hovered and self.enabled \
            else self.border_color
        pygame.draw.rect(surface, border, draw_rect,
                         border_radius=self.border_radius, width=2)

        # Icon + text
        font = assets.get_font(self.font_name)
        text_color = self.text_color if self.enabled else COLOR_GRAY
        text_surf = font.render(self.text, True, text_color)

        if self.icon_type:
            icon_x = draw_rect.x + 28
            icon_color = self.accent_color if self.enabled else COLOR_GRAY
            IconDrawer.draw(surface, self.icon_type, icon_x, draw_rect.centery,
                            self.icon_size, icon_color, timer=self.icon_timer)
            text_x = draw_rect.x + 52 + (draw_rect.width - 52) // 2
            text_rect = text_surf.get_rect(center=(text_x, draw_rect.centery))
        else:
            text_rect = text_surf.get_rect(center=draw_rect.center)
        surface.blit(text_surf, text_rect)

    def set_position(self, x, y):
        """Move button to new position."""
        self.rect.topleft = (x, y)
