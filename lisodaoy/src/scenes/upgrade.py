"""
Upgrade shop scene — spend money on café improvements between levels.
"""
import pygame
import math
from src.constants import *
from src.ui.button import Button
from src.ui.particles import ParticleSystem
from src.ui.icons import IconDrawer


class UpgradeScene:
    """Between-level upgrade shop."""

    def __init__(self, game):
        self.game = game
        self.level = 1
        self.buttons = []
        self.continue_button = None
        self.particles = ParticleSystem()
        self.scroll_y = 0
        self.timer = 0

    def enter(self, level=1, **kwargs):
        """Enter the upgrade scene."""
        self.level = level
        self.particles.clear()
        self.timer = 0
        self._build_buttons()

    def _build_buttons(self):
        """Create upgrade buttons based on current state."""
        self.buttons = []
        upgrades = self.game.upgrades

        x = SCREEN_WIDTH // 2 - 200
        y = 178
        btn_w = 400
        btn_h = 60
        row_gap = 32  # space below each button for its description

        for key, config in UPGRADES.items():
            current_level = upgrades.get(f"{key}_level", 0)
            max_level = config["max_level"]

            if current_level >= max_level:
                label = f"{config['name']} — MAX"
                cost = 0
                can_buy = False
            else:
                cost = config["costs"][current_level]
                can_buy = self.game.money >= cost
                label = f"{config['name']} — ${cost}"

            btn = Button(
                x, y, btn_w, btn_h,
                label,
                font_name="body",
                accent_color=COLOR_GREEN if can_buy else COLOR_GRAY,
                enabled=can_buy and current_level < max_level,
                icon_type=config["icon"],
                icon_size=16,
            )
            btn._upgrade_key = key
            btn._cost = cost
            btn._config = config
            btn._current_level = current_level
            self.buttons.append(btn)

            y += btn_h + row_gap

        # Continue button
        self.continue_button = Button(
            SCREEN_WIDTH // 2 - 140, y + 14, 280, 58,
            "NEXT LEVEL",
            font_name="heading",
            accent_color=COLOR_AMBER,
            icon_type="play",
            icon_size=16,
            callback=self._next_level,
        )

    def _purchase_upgrade(self, key, cost, config):
        """Apply an upgrade purchase."""
        upgrades = self.game.upgrades
        current = upgrades.get(f"{key}_level", 0)

        if self.game.money < cost or current >= config["max_level"]:
            return

        self.game.money -= cost
        upgrades[f"{key}_level"] = current + 1

        # Apply effect
        if key == "workstation":
            upgrades["workstations"] = DEFAULT_WORKSTATIONS + current + 1
        elif key == "tools":
            upgrades["tool_bonus"] = (current + 1) * 3
        elif key == "coffee":
            upgrades["patience_bonus"] = (current + 1) * 3
        elif key == "diagnostic":
            upgrades["diagnostic_hint"] = True
        elif key == "reputation":
            self.game.reputation = min(MAX_REPUTATION,
                                       self.game.reputation + 10)

        self.game.sounds.play("money")
        self.particles.emit_sparkles(SCREEN_WIDTH // 2, 300,
                                      COLOR_AMBER, 20)

        # Rebuild buttons
        self._build_buttons()

    def _next_level(self):
        """Proceed to next level."""
        self.game.change_scene(SCENE_CAFE, level=self.level + 1)

    def handle_event(self, event):
        for btn in self.buttons:
            if btn.handle_event(event):
                key = btn._upgrade_key
                cost = btn._cost
                config = btn._config
                self._purchase_upgrade(key, cost, config)
                return

        self.continue_button.handle_event(event)

    def update(self, dt):
        self.timer += dt
        for btn in self.buttons:
            btn.update(dt)
        self.continue_button.update(dt)
        self.particles.update(dt)

    def draw(self, screen):
        screen.fill(COLOR_BG)

        # Subtle background pattern
        for i in range(0, SCREEN_WIDTH, 40):
            for j in range(0, SCREEN_HEIGHT, 40):
                alpha = int(5 + 3 * math.sin(i * 0.1 + j * 0.1 + self.timer))
                pygame.draw.rect(screen, (30 + alpha, 22 + alpha, 15),
                                 (i, j, 40, 40))

        assets = self.game.assets

        # Title
        assets.draw_text_shadow(screen, "UPGRADE SHOP",
                                "title", SCREEN_WIDTH // 2, 50,
                                COLOR_AMBER, center=True)

        # Level completed info
        assets.draw_text_shadow(
            screen, f"Level {self.level} complete! Prepare for Level {self.level + 1}",
            "body", SCREEN_WIDTH // 2, 100,
            COLOR_TEXT_DIM, center=True)

        # Money display
        money_y = 140
        IconDrawer.draw(screen, "money",
                        SCREEN_WIDTH // 2 - 55, money_y, 16,
                        COLOR_AMBER, timer=self.timer)
        assets.draw_text_shadow(screen, f"${self.game.money}",
                                "heading", SCREEN_WIDTH // 2 + 10, money_y,
                                COLOR_AMBER, center=True)

        # Upgrade buttons
        for btn in self.buttons:
            btn.draw(screen, assets)

            # Show upgrade level dots
            key = btn._upgrade_key
            current = btn._current_level
            max_lvl = btn._config["max_level"]
            dots_x = btn.rect.right + 15
            dots_y = btn.rect.centery

            for d in range(max_lvl):
                color = COLOR_GREEN if d < current else COLOR_GRAY_DARK
                pygame.draw.circle(screen, color,
                                   (dots_x + d * 18, dots_y), 6)
                pygame.draw.circle(screen, COLOR_PANEL_BORDER,
                                   (dots_x + d * 18, dots_y), 6, 1)

            # Description (centered under the button, clear of the next row)
            desc_font = assets.get_font("small")
            desc = desc_font.render(btn._config["description"], True,
                                    COLOR_TEXT_DIM)
            desc_rect = desc.get_rect(
                midtop=(btn.rect.centerx, btn.rect.bottom + 7))
            screen.blit(desc, desc_rect)

        # Continue button
        self.continue_button.draw(screen, assets)

        # Particles
        self.particles.draw(screen, assets)
