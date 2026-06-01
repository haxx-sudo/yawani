"""
Procedural asset generation — rich, charming game visuals drawn with Pygame.
All characters, environments, and UI are rendered programmatically.
"""
import pygame
import math
import random
from src.constants import *


class AssetManager:
    """Generates and caches all visual assets procedurally."""

    def __init__(self):
        self.cache = {}
        self.fonts = {}
        self._init_fonts()

    def _init_fonts(self):
        """Initialize font objects at various sizes."""
        self.fonts["title"] = pygame.font.SysFont("Arial", 64, bold=True)
        self.fonts["heading"] = pygame.font.SysFont("Arial", 36, bold=True)
        self.fonts["body"] = pygame.font.SysFont("Arial", 24)
        self.fonts["small"] = pygame.font.SysFont("Arial", 18)
        self.fonts["tiny"] = pygame.font.SysFont("Arial", 14)
        self.fonts["hud"] = pygame.font.SysFont("Consolas", 22, bold=True)
        self.fonts["hud_small"] = pygame.font.SysFont("Consolas", 16, bold=True)
        self.fonts["terminal"] = pygame.font.SysFont("Consolas", 20)
        self.fonts["big"] = pygame.font.SysFont("Arial", 48, bold=True)
        self.fonts["huge"] = pygame.font.SysFont("Arial", 80, bold=True)
        self.fonts["menu_sub"] = pygame.font.SysFont("Arial", 20, italic=True)

    def get_font(self, name):
        return self.fonts.get(name, self.fonts["body"])

    # =========================================================================
    # Drawing Helpers
    # =========================================================================
    def _gradient_v(self, surface, rect, c_top, c_bottom):
        """Draw a vertical gradient within rect on surface."""
        for y in range(rect.height):
            t = y / max(1, rect.height - 1)
            r = int(c_top[0] + (c_bottom[0] - c_top[0]) * t)
            g = int(c_top[1] + (c_bottom[1] - c_top[1]) * t)
            b = int(c_top[2] + (c_bottom[2] - c_top[2]) * t)
            pygame.draw.line(surface, (r, g, b),
                             (rect.x, rect.y + y),
                             (rect.x + rect.width - 1, rect.y + y))

    def _glow_circle(self, surface, center, radius, color, intensity=40):
        """Draw a soft radial glow."""
        glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        for r in range(radius, 0, -2):
            alpha = max(1, int(intensity * (r / radius)))
            pygame.draw.circle(glow, (*color[:3], alpha), (radius, radius), r)
        surface.blit(glow, (center[0] - radius, center[1] - radius))

    def gradient_round_rect(self, surface, rect, c_top, c_bottom,
                            border_radius=10, alpha=255):
        """Blit a vertical-gradient rounded rectangle onto surface."""
        w, h = rect.width, rect.height
        if w <= 0 or h <= 0:
            return
        grad = pygame.Surface((w, h), pygame.SRCALPHA)
        for y in range(h):
            t = y / max(1, h - 1)
            r = int(c_top[0] + (c_bottom[0] - c_top[0]) * t)
            g = int(c_top[1] + (c_bottom[1] - c_top[1]) * t)
            b = int(c_top[2] + (c_bottom[2] - c_top[2]) * t)
            pygame.draw.line(grad, (r, g, b, alpha), (0, y), (w, y))
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255),
                         (0, 0, w, h), border_radius=border_radius)
        grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surface.blit(grad, rect.topleft)

    def soft_shadow(self, surface, rect, border_radius=12, spread=8,
                    max_alpha=70):
        """Draw a soft blurred drop-shadow behind a rounded rect."""
        for i in range(spread, 0, -1):
            a = int(max_alpha * (1 - i / spread) ** 1.5)
            if a <= 0:
                continue
            sr = rect.inflate(i * 2, i * 2)
            shadow = pygame.Surface((sr.width, sr.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow, (0, 0, 0, a), shadow.get_rect(),
                             border_radius=border_radius + i)
            surface.blit(shadow, sr.topleft)

    def draw_glow_rect(self, surface, rect, color, border_radius=10,
                       layers=6, intensity=60):
        """Draw a soft outer glow/bloom around a rounded rect."""
        for i in range(layers, 0, -1):
            a = int(intensity * (i / layers) ** 2)
            gr = rect.inflate(i * 4, i * 4)
            glow = pygame.Surface((gr.width, gr.height), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*color[:3], a), glow.get_rect(),
                             border_radius=border_radius + i * 2)
            surface.blit(glow, gr.topleft)

    def _lighten(self, color, amount=40):
        """Return a lighter version of a color."""
        return tuple(min(255, c + amount) for c in color[:3])

    def _darken(self, color, amount=40):
        """Return a darker version of a color."""
        return tuple(max(0, c - amount) for c in color[:3])

    # =========================================================================
    # Character Generation — Charming pixel-people
    # =========================================================================
    def draw_customer(self, surface, x, y, skin_color, body_color, hair_color,
                      scale=1.0, facing_right=True):
        """Draw a detailed character at position (x, y)."""
        s = scale
        d = 1 if facing_right else -1

        # --- Shadow on ground ---
        shadow_surf = pygame.Surface((int(44 * s), int(12 * s)), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 45), shadow_surf.get_rect())
        surface.blit(shadow_surf, (x - int(22 * s), y + int(50 * s)))

        # --- Legs ---
        leg_y = y + int(30 * s)
        leg_h = int(22 * s)
        leg_w = int(9 * s)
        # Left leg
        pygame.draw.rect(surface, self._darken(body_color, 50),
                         (x - int(10 * s), leg_y, leg_w, leg_h),
                         border_radius=int(3 * s))
        # Right leg
        pygame.draw.rect(surface, self._darken(body_color, 50),
                         (x + int(2 * s), leg_y, leg_w, leg_h),
                         border_radius=int(3 * s))
        # Shoes
        shoe_color = (50, 40, 35)
        pygame.draw.ellipse(surface, shoe_color,
                            (x - int(12 * s), y + int(48 * s),
                             int(13 * s), int(7 * s)))
        pygame.draw.ellipse(surface, shoe_color,
                            (x + int(0 * s), y + int(48 * s),
                             int(13 * s), int(7 * s)))

        # --- Body / Torso ---
        body_rect = pygame.Rect(x - int(16 * s), y + int(2 * s),
                                int(32 * s), int(32 * s))
        pygame.draw.rect(surface, body_color, body_rect, border_radius=int(8 * s))
        # Body highlight (fabric sheen)
        hl = self._lighten(body_color, 30)
        pygame.draw.rect(surface, hl,
                         (x - int(11 * s), y + int(5 * s),
                          int(10 * s), int(24 * s)),
                         border_radius=int(4 * s))
        # Collar / neckline
        collar_color = self._lighten(body_color, 50)
        pygame.draw.arc(surface, collar_color,
                        (x - int(10 * s), y - int(2 * s),
                         int(20 * s), int(14 * s)),
                        0.3, 2.8, max(1, int(2 * s)))

        # --- Arms ---
        arm_color = body_color
        # Left arm
        arm_lx = x - int(19 * s)
        pygame.draw.rect(surface, arm_color,
                         (arm_lx, y + int(6 * s),
                          int(7 * s), int(24 * s)),
                         border_radius=int(3 * s))
        # Left hand
        pygame.draw.circle(surface, skin_color,
                           (arm_lx + int(3 * s), y + int(30 * s)),
                           int(4 * s))
        # Right arm
        arm_rx = x + int(13 * s)
        pygame.draw.rect(surface, arm_color,
                         (arm_rx, y + int(6 * s),
                          int(7 * s), int(24 * s)),
                         border_radius=int(3 * s))
        # Right hand
        pygame.draw.circle(surface, skin_color,
                           (arm_rx + int(4 * s), y + int(30 * s)),
                           int(4 * s))

        # --- Head ---
        head_r = int(16 * s)
        head_cx = x
        head_cy = y - int(8 * s)
        # Neck
        pygame.draw.rect(surface, skin_color,
                         (head_cx - int(5 * s), head_cy + head_r - int(4 * s),
                          int(10 * s), int(10 * s)))
        # Head circle
        pygame.draw.circle(surface, skin_color, (head_cx, head_cy), head_r)
        # Ear
        ear_x = head_cx + int(14 * s) * d
        pygame.draw.circle(surface, skin_color, (ear_x, head_cy + int(2 * s)),
                           int(4 * s))
        pygame.draw.circle(surface, self._darken(skin_color, 25),
                           (ear_x, head_cy + int(2 * s)),
                           int(3 * s))

        # --- Hair ---
        # Use a deterministic "style" based on hair color hash
        style = (hair_color[0] + hair_color[1] * 3) % 5
        if style == 0:
            # Short cropped
            pygame.draw.circle(surface, hair_color,
                               (head_cx, head_cy - int(2 * s)), head_r + 1)
            pygame.draw.rect(surface, skin_color,
                             (head_cx - head_r, head_cy,
                              head_r * 2, head_r),)
        elif style == 1:
            # Side swept
            hair_rect = pygame.Rect(head_cx - head_r - int(2 * s),
                                    head_cy - head_r - int(2 * s),
                                    head_r * 2 + int(4 * s),
                                    int(head_r * 1.3))
            pygame.draw.ellipse(surface, hair_color, hair_rect)
            # Side sweep
            pts = [(head_cx - head_r, head_cy - int(4 * s)),
                   (head_cx - head_r - int(6 * s), head_cy + int(4 * s)),
                   (head_cx - head_r + int(2 * s), head_cy + int(2 * s))]
            pygame.draw.polygon(surface, hair_color, pts)
        elif style == 2:
            # Spiky top
            for angle in range(-140, -30, 22):
                rad = math.radians(angle)
                sx = head_cx + int(math.cos(rad) * (head_r - 2))
                sy = head_cy + int(math.sin(rad) * (head_r - 2))
                ex = head_cx + int(math.cos(rad) * (head_r + int(8 * s)))
                ey = head_cy + int(math.sin(rad) * (head_r + int(8 * s)))
                pygame.draw.line(surface, hair_color, (sx, sy), (ex, ey),
                                 max(2, int(4 * s)))
            # Base cap
            pygame.draw.arc(surface, hair_color,
                            (head_cx - head_r, head_cy - head_r,
                             head_r * 2, head_r * 2),
                            0.5, 2.6, max(3, int(6 * s)))
        elif style == 3:
            # Flat top / buzz cut
            pygame.draw.rect(surface, hair_color,
                             (head_cx - head_r + int(2 * s),
                              head_cy - head_r,
                              head_r * 2 - int(4 * s),
                              int(head_r * 0.9)),
                             border_radius=int(4 * s))
        else:
            # Round bob
            pygame.draw.circle(surface, hair_color,
                               (head_cx, head_cy - int(4 * s)),
                               head_r + int(3 * s))
            pygame.draw.rect(surface, skin_color,
                             (head_cx - head_r - int(2 * s),
                              head_cy + int(2 * s),
                              head_r * 2 + int(4 * s), head_r))

        # --- Face ---
        # Eyebrows
        brow_color = self._darken(hair_color, 20)
        brow_y = head_cy - int(5 * s)
        pygame.draw.line(surface, brow_color,
                         (head_cx - int(8 * s), brow_y),
                         (head_cx - int(3 * s), brow_y - int(1 * s)),
                         max(1, int(2 * s)))
        pygame.draw.line(surface, brow_color,
                         (head_cx + int(3 * s), brow_y - int(1 * s)),
                         (head_cx + int(8 * s), brow_y),
                         max(1, int(2 * s)))

        # Eyes (bigger, more expressive)
        eye_y = head_cy - int(1 * s)
        for ex in [head_cx - int(6 * s), head_cx + int(6 * s)]:
            # White
            pygame.draw.circle(surface, (250, 250, 250), (ex, eye_y),
                               int(5 * s))
            # Iris
            iris_x = ex + int(1 * s * d)
            pygame.draw.circle(surface, (50, 90, 140), (iris_x, eye_y),
                               int(3 * s))
            # Pupil
            pygame.draw.circle(surface, COLOR_BLACK,
                               (iris_x, eye_y), int(1.5 * s))
            # Highlight
            pygame.draw.circle(surface, COLOR_WHITE,
                               (iris_x + int(1 * s), eye_y - int(1 * s)),
                               max(1, int(1 * s)))

        # Nose (subtle)
        nose_y = head_cy + int(3 * s)
        pygame.draw.circle(surface, self._darken(skin_color, 15),
                           (head_cx, nose_y), int(2 * s))

        # Mouth (small smile)
        mouth_y = head_cy + int(7 * s)
        pygame.draw.arc(surface, (180, 80, 80),
                        (head_cx - int(5 * s), mouth_y - int(3 * s),
                         int(10 * s), int(7 * s)),
                        3.4, 6.0, max(1, int(1.5 * s)))

        # --- Optional Accessories (deterministic by body color) ---
        acc_type = (body_color[0] * 7 + body_color[2]) % 5
        if acc_type == 0:
            # Glasses
            g_y = head_cy - int(1 * s)
            for gx in [head_cx - int(6 * s), head_cx + int(6 * s)]:
                pygame.draw.circle(surface, (60, 60, 60), (gx, g_y),
                                   int(6 * s), max(1, int(1.5 * s)))
            # Bridge
            pygame.draw.line(surface, (60, 60, 60),
                             (head_cx - int(2 * s), g_y),
                             (head_cx + int(2 * s), g_y),
                             max(1, int(1.5 * s)))
        elif acc_type == 1:
            # Tie
            tie_color = self._darken(body_color, 60)
            tie_pts = [
                (head_cx, y + int(4 * s)),
                (head_cx - int(5 * s), y + int(16 * s)),
                (head_cx, y + int(28 * s)),
                (head_cx + int(5 * s), y + int(16 * s)),
            ]
            pygame.draw.polygon(surface, tie_color, tie_pts)
            # Knot
            pygame.draw.circle(surface, tie_color,
                               (head_cx, y + int(4 * s)), int(3 * s))

    def draw_customer_emotion(self, surface, x, y, emotion, scale=1.0):
        """Draw an emotion bubble above the character."""
        s = scale
        bx, by = x, y - int(35 * s)
        bubble_r = int(14 * s)

        # Bubble background
        bubble_surf = pygame.Surface((bubble_r * 2 + 4, bubble_r * 2 + 12),
                                      pygame.SRCALPHA)
        # Bubble body
        pygame.draw.circle(bubble_surf, (255, 255, 255, 230),
                           (bubble_r + 2, bubble_r + 2), bubble_r)
        pygame.draw.circle(bubble_surf, (180, 180, 180),
                           (bubble_r + 2, bubble_r + 2), bubble_r,
                           max(1, int(1.5 * s)))
        # Tail dots
        pygame.draw.circle(bubble_surf, (255, 255, 255, 200),
                           (bubble_r + 2, bubble_r * 2 + 4),
                           int(3 * s))
        pygame.draw.circle(bubble_surf, (255, 255, 255, 150),
                           (bubble_r + 2, bubble_r * 2 + 9),
                           int(2 * s))

        surface.blit(bubble_surf, (bx - bubble_r - 2, by - bubble_r - 2))

        if emotion == "happy":
            # Green check
            pygame.draw.circle(surface, COLOR_GREEN, (bx, by), int(8 * s))
            # Checkmark
            pts = [(bx - int(4 * s), by),
                   (bx - int(1 * s), by + int(4 * s)),
                   (bx + int(5 * s), by - int(4 * s))]
            pygame.draw.lines(surface, COLOR_WHITE, False, pts,
                              max(2, int(2.5 * s)))
        elif emotion == "angry":
            # Red X
            pygame.draw.circle(surface, COLOR_RED, (bx, by), int(8 * s))
            offset = int(4 * s)
            pygame.draw.line(surface, COLOR_WHITE,
                             (bx - offset, by - offset),
                             (bx + offset, by + offset),
                             max(2, int(2.5 * s)))
            pygame.draw.line(surface, COLOR_WHITE,
                             (bx + offset, by - offset),
                             (bx - offset, by + offset),
                             max(2, int(2.5 * s)))
        elif emotion == "waiting":
            # Wrench icon
            wr_color = (100, 100, 110)
            pygame.draw.line(surface, wr_color,
                             (bx - int(5 * s), by + int(5 * s)),
                             (bx + int(3 * s), by - int(3 * s)),
                             max(2, int(3 * s)))
            pygame.draw.circle(surface, wr_color,
                               (bx + int(4 * s), by - int(4 * s)),
                               int(4 * s), max(1, int(2 * s)))
            # Question mark
            font = self.get_font("small")
            q = font.render("?", True, (80, 80, 90))
            surface.blit(q, (bx - int(3 * s), by - int(9 * s)))

    # =========================================================================
    # Workstation / Computer — Detailed desk with monitor
    # =========================================================================
    def draw_workstation(self, surface, x, y, w, h, screen_color=None,
                         has_customer=False):
        """Draw a workstation desk with monitor, keyboard, and details."""
        # --- Desk ---
        desk_h = h // 2 + 5
        desk_y = y + h - desk_h
        desk_rect = pygame.Rect(x, desk_y, w, desk_h)

        # Desk top surface (gradient wood)
        desk_surf = pygame.Surface((w, desk_h), pygame.SRCALPHA)
        self._gradient_v(desk_surf,
                         pygame.Rect(0, 0, w, desk_h),
                         COLOR_WOOD_LIGHT, COLOR_WOOD)
        # Wood grain lines
        for gy in range(4, desk_h, 8):
            alpha = random.randint(5, 15)
            pygame.draw.line(desk_surf, self._darken(COLOR_WOOD, alpha),
                             (3, gy), (w - 3, gy), 1)
        surface.blit(desk_surf, desk_rect.topleft)
        # Desk border
        pygame.draw.rect(surface, COLOR_WOOD_DARK, desk_rect,
                         border_radius=4, width=2)

        # Desk front edge (3D effect)
        edge_rect = pygame.Rect(x + 1, desk_y, w - 2, 6)
        pygame.draw.rect(surface, self._lighten(COLOR_WOOD_LIGHT, 15),
                         edge_rect, border_radius=2)

        # Desk legs
        leg_w = 8
        leg_h = 30
        leg_y = desk_y + desk_h
        pygame.draw.rect(surface, COLOR_WOOD_DARK,
                         (x + 10, leg_y - 2, leg_w, leg_h), border_radius=2)
        pygame.draw.rect(surface, COLOR_WOOD_DARK,
                         (x + w - 18, leg_y - 2, leg_w, leg_h), border_radius=2)

        # --- Monitor ---
        mon_w = int(w * 0.55)
        mon_h = int(h * 0.42)
        mon_x = x + (w - mon_w) // 2
        mon_y = desk_y - mon_h - 12

        # Monitor bezel
        bezel = 4
        pygame.draw.rect(surface, (35, 35, 40),
                         (mon_x - bezel, mon_y - bezel,
                          mon_w + bezel * 2, mon_h + bezel * 2),
                         border_radius=5)
        # Glossy top edge
        pygame.draw.line(surface, (70, 70, 80),
                         (mon_x - bezel + 2, mon_y - bezel + 1),
                         (mon_x + mon_w + bezel - 2, mon_y - bezel + 1), 1)

        # Screen
        sc = screen_color or (25, 35, 45)
        pygame.draw.rect(surface, sc, (mon_x, mon_y, mon_w, mon_h),
                         border_radius=2)

        # Screen reflection (subtle)
        refl = pygame.Surface((mon_w, mon_h // 3), pygame.SRCALPHA)
        refl.fill((255, 255, 255, 12))
        surface.blit(refl, (mon_x, mon_y))

        # Screen content hints (scan lines)
        if has_customer and screen_color:
            for sy in range(mon_y + 2, mon_y + mon_h - 2, 4):
                line_surf = pygame.Surface((mon_w - 4, 1), pygame.SRCALPHA)
                line_surf.fill((*self._lighten(sc, 20), 25))
                surface.blit(line_surf, (mon_x + 2, sy))
            # Blinking cursor
            if (pygame.time.get_ticks() // 500) % 2:
                pygame.draw.rect(surface, self._lighten(sc, 80),
                                 (mon_x + 8, mon_y + mon_h - 14, 8, 10))

        # Monitor stand (neck + base)
        stand_neck_w = 10
        stand_neck_h = 10
        stand_cx = mon_x + mon_w // 2
        pygame.draw.rect(surface, (45, 45, 50),
                         (stand_cx - stand_neck_w // 2,
                          mon_y + mon_h + bezel,
                          stand_neck_w, stand_neck_h))
        # Stand base (oval)
        base_w = 40
        base_h = 8
        pygame.draw.ellipse(surface, (50, 50, 55),
                            (stand_cx - base_w // 2,
                             mon_y + mon_h + bezel + stand_neck_h - 2,
                             base_w, base_h))

        # Brand LED dot
        led_color = COLOR_GREEN if has_customer else (60, 60, 65)
        pygame.draw.circle(surface, led_color,
                           (stand_cx, mon_y + mon_h + bezel - 2), 2)

        # Screen glow when occupied
        if has_customer and screen_color:
            self._glow_circle(surface,
                              (mon_x + mon_w // 2, mon_y + mon_h // 2),
                              mon_w, screen_color, 15)

        # --- Keyboard ---
        kb_w = int(w * 0.4)
        kb_h = 12
        kb_x = x + (w - kb_w) // 2
        kb_y = desk_y + 10
        pygame.draw.rect(surface, (55, 55, 60),
                         (kb_x, kb_y, kb_w, kb_h), border_radius=2)
        # Key rows
        for ky in range(kb_y + 2, kb_y + kb_h - 2, 4):
            for kx in range(kb_x + 3, kb_x + kb_w - 3, 6):
                pygame.draw.rect(surface, (75, 75, 80), (kx, ky, 4, 3))

        # --- Mouse ---
        mouse_x = kb_x + kb_w + 12
        mouse_y = desk_y + 12
        pygame.draw.ellipse(surface, (60, 60, 65),
                            (mouse_x, mouse_y, 14, 20), )
        pygame.draw.line(surface, (50, 50, 55),
                         (mouse_x + 7, mouse_y + 2),
                         (mouse_x + 7, mouse_y + 8), 1)

        # --- Coffee cup (sometimes) ---
        if has_customer and (x % 3 == 0):
            cup_x = x + 12
            cup_y = desk_y + 5
            # Cup body
            pygame.draw.rect(surface, (230, 230, 230),
                             (cup_x, cup_y, 12, 14), border_radius=2)
            # Handle
            pygame.draw.arc(surface, (230, 230, 230),
                            (cup_x + 10, cup_y + 3, 8, 8),
                            -1.2, 1.2, 2)
            # Coffee (brown fill)
            pygame.draw.rect(surface, (120, 70, 30),
                             (cup_x + 2, cup_y + 3, 8, 8), border_radius=1)
            # Steam
            tick = pygame.time.get_ticks() / 600
            for si in range(2):
                sx = cup_x + 4 + si * 5
                sy = cup_y - 4 - si * 3
                offset = math.sin(tick + si) * 3
                pygame.draw.arc(surface, (200, 200, 200, 100),
                                (int(sx + offset), sy, 4, 6),
                                0.5, 2.5, 1)

    # =========================================================================
    # Café Background — Atmospheric interior
    # =========================================================================
    def create_cafe_background(self):
        """Create a rich, atmospheric café background."""
        key = "cafe_bg"
        if key in self.cache:
            return self.cache[key]

        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        wall_h = SCREEN_HEIGHT // 2

        # === WALL ===
        # Base wall gradient (warm plaster)
        for y in range(wall_h):
            t = y / wall_h
            r = int(75 + 20 * t)
            g = int(55 + 12 * t)
            b = int(38 + 8 * t)
            pygame.draw.line(surf, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        # Brick accent strip (upper portion)
        brick_h = 100
        brick_w = 40
        brick_gap = 3
        for by in range(20, 20 + brick_h, 18 + brick_gap):
            row = (by - 20) // (18 + brick_gap)
            offset = (brick_w // 2 + brick_gap // 2) if row % 2 else 0
            for bx in range(-offset, SCREEN_WIDTH, brick_w + brick_gap):
                br = random.randint(100, 130)
                bg = random.randint(55, 70)
                bb = random.randint(40, 50)
                rect = pygame.Rect(bx, by, brick_w, 18)
                pygame.draw.rect(surf, (br, bg, bb), rect, border_radius=2)
                # Mortar lines (darker)
                pygame.draw.rect(surf, (55, 40, 30), rect,
                                 border_radius=2, width=1)

        # === PENDANT LIGHTS ===
        light_positions = [200, 500, 800]
        for lx in light_positions:
            # Wire
            pygame.draw.line(surf, (80, 80, 80), (lx, 0), (lx, 140), 2)
            # Lampshade (trapezoid)
            shade_pts = [(lx - 8, 135), (lx + 8, 135),
                         (lx + 20, 155), (lx - 20, 155)]
            pygame.draw.polygon(surf, (45, 42, 38), shade_pts)
            pygame.draw.polygon(surf, (65, 60, 52), shade_pts, 2)
            # Bulb
            pygame.draw.circle(surf, (255, 245, 200), (lx, 158), 7)
            pygame.draw.circle(surf, (255, 230, 170), (lx, 158), 6)
            # Soft warm glow beneath the bulb (gentle, no hard cone)
            glow_surf = pygame.Surface((180, 180), pygame.SRCALPHA)
            for gr in range(90, 0, -2):
                alpha = max(1, int(10 * (gr / 90)))
                pygame.draw.circle(glow_surf, (255, 200, 120, alpha),
                                   (90, 45), gr)
            surf.blit(glow_surf, (lx - 90, 135))

        # === CAFÉ SIGN (centered) ===
        sign_w, sign_h = 280, 65
        sign_x = SCREEN_WIDTH // 2 - sign_w // 2
        sign_y = 38
        # Sign board
        sign_rect = pygame.Rect(sign_x, sign_y, sign_w, sign_h)
        pygame.draw.rect(surf, (35, 28, 20), sign_rect, border_radius=10)
        # Inner gradient
        inner = sign_rect.inflate(-8, -8)
        self._gradient_v(surf, inner, (255, 200, 80), (230, 160, 50))
        pygame.draw.rect(surf, (180, 130, 40), inner,
                         border_radius=7, width=2)
        # Sign text (two lines, centered)
        sign_cx = sign_rect.centerx
        sign_color = (50, 30, 15)
        font_top = self.get_font("small")
        font_bot = self.get_font("heading")
        top = font_top.render("TECH SUPPORT", True, sign_color)
        bot = font_bot.render("CAFÉ", True, sign_color)
        top_y = sign_rect.centery - top.get_height() // 2 - 2
        bot_y = sign_rect.centery + 2
        surf.blit(top, top.get_rect(midtop=(sign_cx, top_y)))
        surf.blit(bot, bot.get_rect(midtop=(sign_cx, bot_y)))
        # Sign hanging chains
        for cx in [sign_x + 20, sign_x + sign_w - 20]:
            pygame.draw.line(surf, (90, 80, 70), (cx, 20), (cx, sign_y), 2)

        # === CHALKBOARD MENU (left wall) ===
        cb_rect = pygame.Rect(50, 145, 140, 180)
        pygame.draw.rect(surf, (30, 45, 30), cb_rect, border_radius=4)
        pygame.draw.rect(surf, COLOR_WOOD_DARK, cb_rect,
                         border_radius=4, width=4)
        # Chalk text
        chalk_font = self.get_font("tiny")
        menu_items = ["═══ MENU ═══", "", "Espresso   $3",
                      "Latte      $5", "Debug Tea  $4",
                      "Byte Cake  $6", "", "♥ WiFi Free"]
        cy = cb_rect.y + 12
        for item in menu_items:
            chalk = chalk_font.render(item, True, (200, 210, 195))
            surf.blit(chalk, (cb_rect.x + 12, cy))
            cy += 18
        # Chalk tray
        pygame.draw.rect(surf, COLOR_WOOD,
                         (cb_rect.x + 5, cb_rect.bottom - 2,
                          cb_rect.width - 10, 6), border_radius=2)

        # === SHELVES ===
        shelf_sets = [(700, 155, 160), (880, 175, 110)]
        for sx, sy, sw in shelf_sets:
            # Shelf board
            pygame.draw.rect(surf, COLOR_WOOD_LIGHT,
                             (sx, sy, sw, 8), border_radius=2)
            # Brackets
            for bx in [sx + 12, sx + sw - 12]:
                pygame.draw.polygon(surf, COLOR_WOOD,
                                    [(bx - 4, sy + 8), (bx + 4, sy + 8),
                                     (bx, sy + 22)])
            # Items on shelf
            items = random.randint(3, 5)
            ix = sx + 8
            for _ in range(items):
                iw = random.randint(10, 20)
                ih = random.randint(14, 30)
                ic = random.choice([
                    (180, 60, 50), (50, 130, 180), (60, 160, 80),
                    (200, 150, 60), (150, 80, 160), (180, 120, 70)
                ])
                pygame.draw.rect(surf, ic,
                                 (ix, sy - ih, iw, ih), border_radius=2)
                # Label line
                pygame.draw.rect(surf, self._lighten(ic, 40),
                                 (ix + 2, sy - ih + 4, iw - 4, 3))
                ix += iw + 5

        # === POTTED PLANT ===
        plant_x = SCREEN_WIDTH - 100
        plant_y = wall_h - 10
        # Pot
        pot_pts = [(plant_x - 12, plant_y - 30),
                   (plant_x + 12, plant_y - 30),
                   (plant_x + 16, plant_y),
                   (plant_x - 16, plant_y)]
        pygame.draw.polygon(surf, (180, 100, 60), pot_pts)
        pygame.draw.polygon(surf, (150, 80, 45), pot_pts, 2)
        # Soil
        pygame.draw.ellipse(surf, (80, 50, 30),
                            (plant_x - 12, plant_y - 34, 24, 10))
        # Leaves
        for angle in [-60, -30, 0, 25, 55]:
            rad = math.radians(angle)
            lx = plant_x + int(math.cos(rad) * 25)
            ly = plant_y - 35 + int(math.sin(rad) * -25)
            leaf_color = random.choice([(50, 160, 70), (40, 140, 55),
                                        (60, 180, 80)])
            pygame.draw.line(surf, leaf_color,
                             (plant_x, plant_y - 35), (lx, ly), 3)
            pygame.draw.circle(surf, leaf_color, (lx, ly), 6)

        # === WALL-FLOOR BORDER ===
        # Baseboard
        pygame.draw.rect(surf, COLOR_WOOD,
                         (0, wall_h - 8, SCREEN_WIDTH, 16))
        pygame.draw.rect(surf, self._lighten(COLOR_WOOD, 20),
                         (0, wall_h - 8, SCREEN_WIDTH, 4))
        pygame.draw.rect(surf, self._darken(COLOR_WOOD, 20),
                         (0, wall_h + 4, SCREEN_WIDTH, 4))

        # === FLOOR ===
        plank_h = 35
        for py in range(wall_h + 8, SCREEN_HEIGHT, plank_h):
            row = (py - wall_h) // plank_h
            t = (py - wall_h) / (SCREEN_HEIGHT - wall_h)
            base_r = int(85 - 20 * t)
            base_g = int(55 - 12 * t)
            base_b = int(32 - 8 * t)

            plank_w = 120
            offset = (plank_w // 2) if row % 2 else 0
            for px in range(-offset, SCREEN_WIDTH + plank_w, plank_w):
                variation = random.randint(-8, 8)
                pc = (base_r + variation, base_g + variation // 2,
                      base_b + variation // 3)
                rect = pygame.Rect(px, py, plank_w - 2, plank_h - 1)
                pygame.draw.rect(surf, pc, rect)
                # Wood grain
                for gy in range(rect.y + 4, rect.bottom - 2, 7):
                    grain_c = (pc[0] - 5, pc[1] - 3, pc[2] - 2)
                    pygame.draw.line(surf, grain_c,
                                     (rect.x + 2, gy),
                                     (rect.right - 2, gy), 1)
            # Plank border
            pygame.draw.line(surf, (50, 35, 20),
                             (0, py), (SCREEN_WIDTH, py), 1)

        # === DOOR (right side) ===
        door_w, door_h = 55, 110
        door_x = SCREEN_WIDTH - 75
        door_y = wall_h - door_h + 8
        # Door frame
        pygame.draw.rect(surf, COLOR_WOOD_DARK,
                         (door_x - 5, door_y - 5,
                          door_w + 10, door_h + 5), border_radius=3)
        # Door body
        door_rect = pygame.Rect(door_x, door_y, door_w, door_h)
        self._gradient_v(surf, door_rect,
                         (100, 70, 45), (80, 55, 35))
        # Door panels
        panel_inset = 6
        for py_off in [15, 58]:
            pr = pygame.Rect(door_x + panel_inset, door_y + py_off,
                             door_w - panel_inset * 2, 35)
            pygame.draw.rect(surf, self._darken(COLOR_WOOD, 10), pr,
                             border_radius=3, width=2)
        # Door handle
        pygame.draw.circle(surf, (200, 180, 80),
                           (door_x + 12, door_y + door_h // 2), 5)
        pygame.draw.circle(surf, (170, 150, 60),
                           (door_x + 12, door_y + door_h // 2), 5, 1)
        # "OPEN" sign
        open_font = self.get_font("tiny")
        open_text = open_font.render("OPEN", True, COLOR_GREEN)
        surf.blit(open_text, (door_x + 12, door_y + 5))

        # === AMBIENT LIGHTING OVERLAY ===
        # Edge vignette using nested rounded rects (darker towards corners)
        vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        steps = 60
        for i in range(steps):
            a = int(45 * (i / steps) ** 2)
            inset = int((steps - i) * 7)
            pygame.draw.rect(vignette, (0, 0, 0, a),
                             (inset, inset,
                              SCREEN_WIDTH - inset * 2,
                              SCREEN_HEIGHT - inset * 2),
                             border_radius=120, width=8)
        surf.blit(vignette, (0, 0))

        # Overall warm tint
        warm = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        warm.fill((255, 200, 130, 10))
        surf.blit(warm, (0, 0))

        self.cache[key] = surf
        return surf

    # =========================================================================
    # Hardware Components — Unique shapes per type
    # =========================================================================
    def create_component_sprite(self, name, color, width=100, height=60):
        """Create a detailed hardware component sprite."""
        key = f"component_{name}_{width}_{height}"
        if key in self.cache:
            return self.cache[key]

        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        body_rect = pygame.Rect(4, 4, width - 8, height - 8)

        # Component body with gradient
        self._gradient_v(surf, body_rect, self._lighten(color, 20), color)
        pygame.draw.rect(surf, self._darken(color, 50), body_rect,
                         border_radius=6, width=2)

        # Top highlight strip
        pygame.draw.rect(surf, self._lighten(color, 50),
                         (body_rect.x + 2, body_rect.y + 2,
                          body_rect.width - 4, 4), border_radius=2)

        # Type-specific details
        if "RAM" in name:
            # Notch in middle
            notch_x = width // 2 - 3
            pygame.draw.rect(surf, (0, 0, 0, 0),
                             (notch_x, height - 8, 6, 8))
            # Chip squares
            for cx in range(12, width - 12, 14):
                pygame.draw.rect(surf, self._darken(color, 30),
                                 (cx, 14, 10, 16), border_radius=1)
        elif "Graphics" in name or "GPU" in name:
            # Fan circle
            fan_cx = width // 2
            fan_cy = height // 2
            fan_r = min(width, height) // 3
            pygame.draw.circle(surf, self._darken(color, 20),
                               (fan_cx, fan_cy), fan_r)
            pygame.draw.circle(surf, self._lighten(color, 10),
                               (fan_cx, fan_cy), fan_r, 2)
            # Fan blades
            for a in range(0, 360, 60):
                rad = math.radians(a)
                pygame.draw.line(surf, self._darken(color, 40),
                                 (fan_cx, fan_cy),
                                 (fan_cx + int(math.cos(rad) * (fan_r - 3)),
                                  fan_cy + int(math.sin(rad) * (fan_r - 3))), 2)
        elif "CPU" in name:
            # Pin grid on bottom
            for px in range(10, width - 10, 5):
                for py in range(height - 14, height - 4, 5):
                    pygame.draw.rect(surf, (180, 170, 140), (px, py, 3, 3))
            # Die in center
            die_size = min(width, height) // 3
            pygame.draw.rect(surf, self._darken(color, 30),
                             (width // 2 - die_size // 2,
                              height // 2 - die_size // 2 - 3,
                              die_size, die_size), border_radius=2)
        elif "SSD" in name:
            # Label sticker
            pygame.draw.rect(surf, (240, 240, 240),
                             (10, 10, width - 20, height // 2 - 4),
                             border_radius=2)
            # Barcode lines
            for lx in range(14, width - 14, 3):
                h_line = random.randint(6, 14)
                pygame.draw.line(surf, (40, 40, 40),
                                 (lx, 14), (lx, 14 + h_line), 1)
        elif "Power" in name or "PSU" in name:
            # Cable connector holes
            for cy in range(14, height - 14, 10):
                pygame.draw.circle(surf, self._darken(color, 40),
                                   (width - 16, cy), 3)
            # Power symbol
            pygame.draw.circle(surf, self._lighten(color, 60),
                               (width // 3, height // 2), 10, 2)
            pygame.draw.line(surf, self._lighten(color, 60),
                             (width // 3, height // 2 - 12),
                             (width // 3, height // 2 - 4), 2)
        elif "Fan" in name or "Cool" in name:
            # Fan blades
            cx, cy = width // 2, height // 2
            r = min(width, height) // 2 - 8
            pygame.draw.circle(surf, self._darken(color, 15), (cx, cy), r)
            for a in range(0, 360, 45):
                rad = math.radians(a)
                pygame.draw.line(surf, color, (cx, cy),
                                 (cx + int(math.cos(rad) * r),
                                  cy + int(math.sin(rad) * r)), 3)
            pygame.draw.circle(surf, self._lighten(color, 30), (cx, cy), 6)

        # Pins on bottom edge
        for px in range(10, width - 10, 6):
            pygame.draw.rect(surf, (180, 170, 140), (px, height - 6, 3, 6))

        # Label text
        font = self.get_font("tiny")
        label = font.render(name, True, COLOR_WHITE)
        # Shadow
        shadow = font.render(name, True, (0, 0, 0))
        lx = (width - label.get_width()) // 2
        ly = height - 20
        surf.blit(shadow, (lx + 1, ly + 1))
        surf.blit(label, (lx, ly))

        self.cache[key] = surf
        return surf

    # =========================================================================
    # Virus — Menacing blob with personality
    # =========================================================================
    def create_virus_sprite(self, size=30):
        """Create a detailed virus sprite."""
        size = max(5, size)
        key = f"virus_{size}"
        if key in self.cache:
            return self.cache[key]

        dim = size * 2 + 20
        surf = pygame.Surface((dim, dim), pygame.SRCALPHA)
        cx, cy = dim // 2, dim // 2

        # Outer glow
        self._glow_circle(surf, (cx, cy), size + 8, (255, 50, 50), 20)

        # Body (gradient effect — darker edges)
        pygame.draw.circle(surf, (220, 40, 40), (cx, cy), size)
        pygame.draw.circle(surf, (255, 70, 70),
                           (cx - size // 4, cy - size // 4), size // 2)

        # Spikes with spheres
        for angle in range(0, 360, 40):
            rad = math.radians(angle)
            spike_len = size // 2 + 4
            sx = cx + int(math.cos(rad) * size)
            sy = cy + int(math.sin(rad) * size)
            ex = cx + int(math.cos(rad) * (size + spike_len))
            ey = cy + int(math.sin(rad) * (size + spike_len))
            pygame.draw.line(surf, (200, 50, 50), (sx, sy), (ex, ey),
                             max(2, size // 8))
            pygame.draw.circle(surf, (240, 70, 70), (ex, ey),
                               max(2, size // 6))

        # Angry face
        if size >= 12:
            # Angry eyebrows
            pygame.draw.line(surf, (100, 20, 20),
                             (cx - size // 3, cy - size // 4),
                             (cx - size // 8, cy - size // 3),
                             max(1, size // 10))
            pygame.draw.line(surf, (100, 20, 20),
                             (cx + size // 3, cy - size // 4),
                             (cx + size // 8, cy - size // 3),
                             max(1, size // 10))
            # Eyes
            eye_r = max(2, size // 5)
            for ex in [cx - size // 4, cx + size // 4]:
                pygame.draw.circle(surf, (255, 255, 200), (ex, cy - 2), eye_r)
                pygame.draw.circle(surf, (30, 0, 0),
                                   (ex, cy - 1), max(1, eye_r // 2))
            # Mouth (evil grin)
            if size >= 18:
                mouth_w = size // 2
                pygame.draw.arc(surf, (150, 20, 20),
                                (cx - mouth_w, cy + size // 6,
                                 mouth_w * 2, size // 3),
                                3.4, 6.1, max(1, size // 10))

        self.cache[key] = surf
        return surf

    # =========================================================================
    # Network Node — Styled with icon hints
    # =========================================================================
    def create_network_node(self, label, size=35, active=False,
                            highlighted=False):
        """Create a network node sprite with glow effects."""
        dim = size * 2 + 16
        surf = pygame.Surface((dim, dim), pygame.SRCALPHA)
        cx, cy = dim // 2, dim // 2

        # Determine color
        if active:
            color = COLOR_GREEN
        elif highlighted:
            color = COLOR_CYAN
        else:
            color = (80, 85, 90)

        # Outer glow
        if active or highlighted:
            self._glow_circle(surf, (cx, cy), size + 6, color, 30)

        # Node body (gradient)
        pygame.draw.circle(surf, color, (cx, cy), size)
        # Inner lighter circle
        pygame.draw.circle(surf, self._lighten(color, 35),
                           (cx - size // 5, cy - size // 5), size // 2)
        # Border ring
        border_c = self._lighten(color, 20) if active else self._darken(color, 20)
        pygame.draw.circle(surf, border_c, (cx, cy), size, 3)
        # Inner ring
        pygame.draw.circle(surf, self._lighten(color, 10),
                           (cx, cy), size - 6, 1)

        # Label (number)
        font = self.get_font("body")
        text = font.render(str(label), True, COLOR_WHITE)
        # Shadow
        shadow = font.render(str(label), True, (0, 0, 0))
        text_rect = text.get_rect(center=(cx, cy))
        surf.blit(shadow, text_rect.move(1, 1))
        surf.blit(text, text_rect)

        # Pulsing ring for highlighted (next to click)
        if highlighted:
            pulse = abs(math.sin(pygame.time.get_ticks() / 300)) * 0.6 + 0.4
            pulse_r = size + int(6 * pulse)
            alpha = int(180 * pulse)
            ring_surf = pygame.Surface((dim, dim), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (*COLOR_CYAN[:3], alpha),
                               (cx, cy), pulse_r, 2)
            surf.blit(ring_surf, (0, 0))

        return surf

    # =========================================================================
    # UI Helpers — Polished panels and bars
    # =========================================================================
    def draw_panel(self, surface, rect, color=None, border_color=None,
                   border_radius=12, alpha=230):
        """Draw a glass-like semi-transparent panel."""
        color = color or COLOR_PANEL
        border_color = border_color or COLOR_PANEL_BORDER

        # Soft drop shadow behind the panel for depth
        self.soft_shadow(surface, rect, border_radius=border_radius,
                         spread=10, max_alpha=60)

        panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

        # Main fill — subtle vertical gradient (lighter top → darker bottom)
        w, h = rect.width, rect.height
        top_c = self._lighten(color, 16)
        bot_c = self._darken(color, 10)
        for y in range(h):
            t = y / max(1, h - 1)
            r = int(top_c[0] + (bot_c[0] - top_c[0]) * t)
            g = int(top_c[1] + (bot_c[1] - top_c[1]) * t)
            b = int(top_c[2] + (bot_c[2] - top_c[2]) * t)
            pygame.draw.line(panel, (r, g, b, alpha), (0, y), (w, y))
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255),
                         (0, 0, w, h), border_radius=border_radius)
        panel.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        # Inner gradient (subtle lightening at top)
        inner = pygame.Surface((w - 4, h // 3), pygame.SRCALPHA)
        for y in range(inner.get_height()):
            a = int(26 * (1 - y / inner.get_height()))
            pygame.draw.line(inner, (255, 255, 255, a),
                             (0, y), (inner.get_width(), y))
        panel.blit(inner, (2, 2))

        # Border + brighter accent highlight along the top edge
        pygame.draw.rect(panel, (*border_color, 255),
                         (0, 0, w, h), border_radius=border_radius, width=2)
        pygame.draw.line(panel, (*self._lighten(border_color, 50), 180),
                         (border_radius, 1), (w - border_radius, 1), 1)

        # Inner shadow at bottom
        for i in range(4):
            a = max(1, 15 - i * 4)
            pygame.draw.line(panel, (0, 0, 0, a),
                             (border_radius, h - 3 - i),
                             (w - border_radius, h - 3 - i))

        surface.blit(panel, rect.topleft)

    def draw_progress_bar(self, surface, x, y, w, h, progress, color,
                          bg_color=None):
        """Draw a polished progress bar with glow and segments."""
        bg_color = bg_color or (30, 25, 20)
        progress = max(0.0, min(1.0, progress))

        # Background with inner shadow
        pygame.draw.rect(surface, bg_color, (x, y, w, h),
                         border_radius=h // 2)
        # Inner shadow
        pygame.draw.rect(surface, self._darken(bg_color, 15),
                         (x + 1, y + 1, w - 2, h // 2),
                         border_radius=h // 2)

        # Fill
        if progress > 0:
            fill_w = max(h, int(w * progress))
            # Gradient fill
            fill_surf = pygame.Surface((fill_w, h), pygame.SRCALPHA)
            self._gradient_v(fill_surf,
                             pygame.Rect(0, 0, fill_w, h),
                             self._lighten(color, 25), color)
            # Mask to rounded rect
            mask = pygame.Surface((fill_w, h), pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255, 255),
                             (0, 0, fill_w, h), border_radius=h // 2)
            fill_surf.blit(mask, (0, 0),
                           special_flags=pygame.BLEND_RGBA_MIN)
            surface.blit(fill_surf, (x, y))

            # Segment marks
            seg_interval = max(8, w // 10)
            for sx in range(x + seg_interval, x + fill_w - 2, seg_interval):
                pygame.draw.line(surface, (*self._darken(color, 30), 80),
                                 (sx, y + 2), (sx, y + h - 2), 1)

            # Shine highlight
            shine_h = max(1, h // 3)
            shine_surf = pygame.Surface((fill_w - 4, shine_h), pygame.SRCALPHA)
            shine_surf.fill((255, 255, 255, 40))
            surface.blit(shine_surf, (x + 2, y + 1))

        # Border
        pygame.draw.rect(surface, self._lighten(bg_color, 30),
                         (x, y, w, h), border_radius=h // 2, width=1)

    def draw_text_shadow(self, surface, text, font_name, x, y,
                         color=COLOR_TEXT, shadow_color=(0, 0, 0),
                         center=False):
        """Render text with a drop shadow."""
        font = self.get_font(font_name)
        shadow = font.render(text, True, shadow_color)
        text_surf = font.render(text, True, color)

        if center:
            rect = text_surf.get_rect(center=(x, y))
            shadow_rect = shadow.get_rect(center=(x + 2, y + 2))
        else:
            rect = text_surf.get_rect(topleft=(x, y))
            shadow_rect = shadow.get_rect(topleft=(x + 2, y + 2))

        surface.blit(shadow, shadow_rect)
        surface.blit(text_surf, rect)
        return rect
