"""
Mobile display scaling and touch input for phones/tablets.
"""
import os
import pygame
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT


def is_mobile():
    """True on Android builds or when TECH_CAFE_MOBILE=1 / --mobile."""
    if os.environ.get("TECH_CAFE_MOBILE") == "1":
        return True
    if "ANDROID_ARGUMENT" in os.environ or "ANDROID_PRIVATE" in os.environ:
        return True
    return False


def touch_padding():
    """Extra hit area around buttons on touch devices."""
    return 24 if is_mobile() else 0


def touch_radius_scale():
    """Scale tap targets for mini-games (virus blobs, nodes)."""
    return 1.35 if is_mobile() else 1.0


class MobileDisplay:
    """
    Renders the game at a fixed virtual resolution and scales to the device.
  Touch coordinates are mapped back into game space.
    """

    def __init__(self, force_mobile=False):
        self.mobile = force_mobile or is_mobile()
        self.game_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.display_size = self.game_size
        self.scale = 1.0
        self.offset = (0, 0)
        self.scaled_size = self.game_size
        self.screen = None
        self.render_surface = None

    @property
    def needs_scale(self):
        return self.display_size != self.game_size

    def setup(self):
        """Create the window and internal render surface."""
        pygame.display.set_caption("Tech Support Café")
        if self.mobile:
            pygame.mouse.set_visible(False)
            info = pygame.display.Info()
            w = max(info.current_w, 480)
            h = max(info.current_h, 320)
            flags = pygame.FULLSCREEN
            try:
                self.screen = pygame.display.set_mode((w, h), flags)
            except pygame.error:
                self.screen = pygame.display.set_mode((w, h))
            self.display_size = self.screen.get_size()
        else:
            self.screen = pygame.display.set_mode(self.game_size, pygame.RESIZABLE)
            self.display_size = self.screen.get_size()

        self.render_surface = pygame.Surface(self.game_size)
        self._recompute_scale()

    def _recompute_scale(self):
        gw, gh = self.game_size
        dw, dh = self.display_size
        self.scale = min(dw / gw, dh / gh)
        self.scaled_size = (max(1, int(gw * self.scale)),
                            max(1, int(gh * self.scale)))
        self.offset = ((dw - self.scaled_size[0]) // 2,
                       (dh - self.scaled_size[1]) // 2)

    def display_to_game(self, pos):
        """Map screen pixel to virtual game coordinates."""
        x, y = pos
        gx = (x - self.offset[0]) / self.scale
        gy = (y - self.offset[1]) / self.scale
        gx = max(0, min(SCREEN_WIDTH - 1, gx))
        gy = max(0, min(SCREEN_HEIGHT - 1, gy))
        return (int(gx), int(gy))

    def _finger_pos(self, event):
        dw, dh = self.display_size
        return (int(event.x * dw), int(event.y * dh))

    def _finger_to_mouse(self, event):
        pos = self.display_to_game(self._finger_pos(event))
        if event.type == pygame.FINGERDOWN:
            etype = pygame.MOUSEBUTTONDOWN
            button = 1
        elif event.type == pygame.FINGERUP:
            etype = pygame.MOUSEBUTTONUP
            button = 1
        else:
            etype = pygame.MOUSEMOTION
            button = 0
        return pygame.event.Event(etype, {"pos": pos, "button": button})

    def translate_event(self, event):
        """Return a game-space event, or None to drop duplicates."""
        if event.type == pygame.VIDEORESIZE:
            self.display_size = event.size
            self.screen = pygame.display.set_mode(self.display_size, pygame.RESIZABLE)
            self._recompute_scale()
            return None

        if event.type in (pygame.FINGERDOWN, pygame.FINGERUP, pygame.FINGERMOTION):
            if self.mobile or self.needs_scale:
                return self._finger_to_mouse(event)
            return None

        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP,
                          pygame.MOUSEMOTION):
            # Android sends both FINGER* and touch-flagged mouse — skip dupes
            if self.mobile and getattr(event, "touch", False):
                return None
            if self.needs_scale or self.mobile:
                pos = self.display_to_game(event.pos)
                data = dict(event.dict)
                data["pos"] = pos
                return pygame.event.Event(event.type, data)
            return event

        return event

    def present(self):
        """Scale the game framebuffer to the device screen."""
        if not self.needs_scale:
            self.screen.blit(self.render_surface, (0, 0))
        else:
            self.screen.fill((0, 0, 0))
            scaled = pygame.transform.smoothscale(
                self.render_surface, self.scaled_size)
            self.screen.blit(scaled, self.offset)
        pygame.display.flip()
