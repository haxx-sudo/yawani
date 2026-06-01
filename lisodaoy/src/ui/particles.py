"""
Particle effects system — sparkles, floating text, puffs.
"""
import pygame
import math
import random
from src.constants import *


class Particle:
    """A single particle with position, velocity, lifetime, and appearance."""

    def __init__(self, x, y, vx, vy, lifetime, color, size=4,
                 gravity=0, fade=True, shape="circle"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.color = color
        self.size = size
        self.gravity = gravity
        self.fade = fade
        self.shape = shape  # "circle", "square", "star"
        self.alive = True

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, surface):
        if not self.alive:
            return
        t = self.lifetime / self.max_lifetime
        alpha = int(255 * t) if self.fade else 255
        current_size = max(1, int(self.size * t))

        if alpha <= 0 or current_size <= 0:
            return

        color = (*self.color[:3], min(255, alpha))
        s = current_size * 2 + 4
        particle_surf = pygame.Surface((s, s), pygame.SRCALPHA)

        if self.shape == "circle":
            pygame.draw.circle(particle_surf, color, (s // 2, s // 2),
                               current_size)
        elif self.shape == "square":
            pygame.draw.rect(particle_surf, color,
                             (s // 2 - current_size, s // 2 - current_size,
                              current_size * 2, current_size * 2))
        elif self.shape == "star":
            # Simple 4-point star
            cx, cy = s // 2, s // 2
            points = []
            for i in range(8):
                angle = i * math.pi / 4
                r = current_size if i % 2 == 0 else current_size // 2
                points.append((cx + int(math.cos(angle) * r),
                                cy + int(math.sin(angle) * r)))
            if len(points) >= 3:
                pygame.draw.polygon(particle_surf, color, points)

        surface.blit(particle_surf, (int(self.x) - s // 2,
                                     int(self.y) - s // 2))


class FloatingText:
    """Floating text that rises and fades."""

    def __init__(self, x, y, text, color=COLOR_AMBER, font_name="body",
                 rise_speed=60, lifetime=1.5):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.font_name = font_name
        self.rise_speed = rise_speed
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.alive = True

    def update(self, dt):
        self.y -= self.rise_speed * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, surface, assets):
        if not self.alive:
            return
        t = self.lifetime / self.max_lifetime
        alpha = int(255 * t)

        font = assets.get_font(self.font_name)
        text_surf = font.render(self.text, True, self.color)
        text_surf.set_alpha(alpha)
        rect = text_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(text_surf, rect)


class ParticleSystem:
    """Manages multiple particle effects."""

    def __init__(self):
        self.particles = []
        self.floating_texts = []

    def emit_sparkles(self, x, y, color=COLOR_AMBER, count=15):
        """Emit a burst of sparkle particles."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 180)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            size = random.randint(2, 5)
            lifetime = random.uniform(0.4, 1.0)
            shape = random.choice(["circle", "star"])
            p = Particle(x, y, vx, vy, lifetime, color, size,
                         gravity=100, shape=shape)
            self.particles.append(p)

    def emit_money(self, x, y, amount):
        """Show floating money text."""
        text = f"+${amount}"
        ft = FloatingText(x, y, text, COLOR_AMBER, "heading",
                          rise_speed=80, lifetime=1.8)
        self.floating_texts.append(ft)

    def emit_reputation(self, x, y, amount, positive=True):
        """Show floating reputation change."""
        prefix = "+" if positive else ""
        text = f"{prefix}{amount} REP"
        color = COLOR_CYAN if positive else COLOR_RED
        ft = FloatingText(x, y, text, color, "body",
                          rise_speed=60, lifetime=1.5)
        self.floating_texts.append(ft)

    def emit_puff(self, x, y, color=(180, 180, 180), count=10):
        """Emit a puff cloud (customer leaving angry)."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(20, 80)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 30
            size = random.randint(4, 10)
            lifetime = random.uniform(0.5, 1.2)
            p = Particle(x, y, vx, vy, lifetime, color, size,
                         gravity=-20, shape="circle")
            self.particles.append(p)

    def emit_text(self, x, y, text, color=COLOR_TEXT, font_name="body"):
        """Show generic floating text."""
        ft = FloatingText(x, y, text, color, font_name)
        self.floating_texts.append(ft)

    def update(self, dt):
        """Update all particles and remove dead ones."""
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive]

        for ft in self.floating_texts:
            ft.update(dt)
        self.floating_texts = [ft for ft in self.floating_texts if ft.alive]

    def draw(self, surface, assets=None):
        """Draw all particles and floating text."""
        for p in self.particles:
            p.draw(surface)
        if assets:
            for ft in self.floating_texts:
                ft.draw(surface, assets)

    def clear(self):
        """Remove all particles."""
        self.particles.clear()
        self.floating_texts.clear()
