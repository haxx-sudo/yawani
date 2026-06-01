"""
Customer entity — appearance, patience, states, movement.
"""
import pygame
import random
import math
from src.constants import *
from src.utils.mobile import touch_padding


class Customer:
    """A customer who brings a broken computer to the café."""

    def __init__(self, problem, patience, customer_id):
        self.id = customer_id
        self.problem = problem
        self.patience = patience
        self.max_patience = patience

        # Appearance (randomized)
        self.body_color = random.choice(CUSTOMER_BODY_COLORS)
        self.skin_color = random.choice(SKIN_COLORS)
        self.hair_color = random.choice(HAIR_COLORS)

        # Position & movement
        self.x = SCREEN_WIDTH + 30  # start off-screen right
        self.y = SCREEN_HEIGHT // 2 + 60
        self.target_x = 0
        self.target_y = 0
        self.speed = 200  # pixels per second
        self.facing_right = False

        # State machine
        # States: entering, waiting, being_served, happy, angry, leaving
        self.state = "entering"
        self.workstation_idx = -1

        # Animation
        self.bob_timer = random.uniform(0, math.pi * 2)
        self.bob_speed = random.uniform(2.0, 4.0)

        # Leave timer (how long happy/angry state lasts before leaving)
        self.leave_timer = 0
        self.leave_duration = 1.5

        # Served flag
        self.served = False
        self.repair_success = False

    @property
    def patience_ratio(self):
        """Return patience as 0.0 to 1.0."""
        return max(0.0, self.patience / self.max_patience)

    @property
    def is_done(self):
        """Customer has finished (served or left angry)."""
        return self.state == "gone"

    def set_workstation(self, idx, x, y):
        """Assign customer to a workstation position."""
        self.workstation_idx = idx
        self.target_x = x
        self.target_y = y - 15  # stand slightly above desk

    def start_repair(self):
        """Customer is now being served."""
        self.state = "being_served"

    def finish_repair(self, success):
        """Repair completed (or failed)."""
        self.repair_success = success
        self.served = True
        if success:
            self.state = "happy"
        else:
            self.state = "angry"
        self.leave_timer = self.leave_duration

    def update(self, dt):
        """Update customer state, movement, patience."""
        self.bob_timer += self.bob_speed * dt

        if self.state == "entering":
            # Move toward workstation
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 5:
                self.x += (dx / dist) * self.speed * dt
                self.y += (dy / dist) * self.speed * dt
                self.facing_right = dx < 0
            else:
                self.x = self.target_x
                self.y = self.target_y
                self.state = "waiting"

        elif self.state == "waiting":
            # Patience drains
            self.patience -= dt
            if self.patience <= 0:
                self.patience = 0
                self.state = "angry"
                self.leave_timer = self.leave_duration

        elif self.state == "being_served":
            # Patience still drains but slower
            self.patience -= dt * 0.3

        elif self.state in ("happy", "angry"):
            self.leave_timer -= dt
            if self.leave_timer <= 0:
                self.state = "leaving"
                self.target_x = SCREEN_WIDTH + 60
                self.target_y = SCREEN_HEIGHT // 2 + 60

        elif self.state == "leaving":
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 5:
                self.x += (dx / dist) * self.speed * 1.5 * dt
                self.y += (dy / dist) * self.speed * 1.5 * dt
                self.facing_right = dx > 0
            else:
                self.state = "gone"

    def draw(self, surface, assets):
        """Draw the customer."""
        if self.state == "gone":
            return

        # Bob animation
        bob_y = math.sin(self.bob_timer) * 2
        draw_x = int(self.x)
        draw_y = int(self.y + bob_y)

        # Draw character
        scale = 1.0
        if self.state == "happy":
            # Slight bounce
            scale = 1.0 + abs(math.sin(self.bob_timer * 3)) * 0.05
        elif self.state == "angry":
            # Shake
            draw_x += int(math.sin(self.bob_timer * 15) * 3)

        assets.draw_customer(surface, draw_x, draw_y,
                             self.skin_color, self.body_color,
                             self.hair_color, scale, self.facing_right)

        # Patience bar (only when waiting or being served)
        if self.state in ("waiting", "being_served"):
            bar_width = 40
            bar_height = 6
            bar_x = draw_x - bar_width // 2
            bar_y = draw_y - 40

            # Choose color based on patience level
            ratio = self.patience_ratio
            if ratio > 0.6:
                bar_color = COLOR_GREEN
            elif ratio > 0.3:
                bar_color = COLOR_YELLOW
            else:
                bar_color = COLOR_RED

            assets.draw_progress_bar(surface, bar_x, bar_y,
                                     bar_width, bar_height,
                                     ratio, bar_color)

        # Emotion indicator
        if self.state == "waiting":
            assets.draw_customer_emotion(surface, draw_x, draw_y,
                                         "waiting", scale)
        elif self.state == "happy":
            assets.draw_customer_emotion(surface, draw_x, draw_y,
                                         "happy", scale)
        elif self.state == "angry":
            assets.draw_customer_emotion(surface, draw_x, draw_y,
                                         "angry", scale)

    def get_click_rect(self):
        """Get the clickable area for this customer."""
        r = pygame.Rect(int(self.x) - 25, int(self.y) - 25, 50, 80)
        pad = touch_padding()
        return r.inflate(pad, pad) if pad else r
