"""
Workstation entity — desk slots where customers sit for repairs.
"""
import pygame
from src.constants import *


class Workstation:
    """A workstation in the café where a customer can be served."""

    def __init__(self, index, x, y, width=WORKSTATION_WIDTH,
                 height=WORKSTATION_HEIGHT):
        self.index = index
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.occupied = False
        self.customer = None

        # Screen state
        self.screen_color = (30, 40, 50)  # default dim screen
        self.active = True  # whether this workstation is unlocked

    def assign_customer(self, customer):
        """Assign a customer to this workstation."""
        self.customer = customer
        self.occupied = True
        customer.set_workstation(self.index,
                                self.x + self.width // 2,
                                self.y)
        # Set screen color based on problem category
        cat = customer.problem.category
        self.screen_color = CATEGORY_COLORS.get(cat, (30, 40, 50))

    def release_customer(self):
        """Free this workstation."""
        self.customer = None
        self.occupied = False
        self.screen_color = (30, 40, 50)

    def draw(self, surface, assets):
        """Draw the workstation."""
        if not self.active:
            return

        has_customer = self.occupied and self.customer is not None
        assets.draw_workstation(surface, self.x, self.y,
                                self.width, self.height,
                                self.screen_color, has_customer)

        # Draw workstation number
        font = assets.get_font("tiny")
        label = font.render(f"WS-{self.index + 1}", True, COLOR_TEXT_DIM)
        label_rect = label.get_rect(
            centerx=self.x + self.width // 2,
            top=self.y + self.height + 5)
        surface.blit(label, label_rect)

    def get_click_rect(self):
        """Clickable area includes the customer area above the desk."""
        return pygame.Rect(self.x, self.y - 60,
                           self.width, self.height + 60)
