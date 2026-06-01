"""
Café scene — main gameplay with customers, workstations, and diagnosis.
"""
import pygame
import random
from src.constants import *
from src.ui.icons import IconDrawer
from src.entities.customer import Customer
from src.entities.workstation import Workstation
from src.entities.problem import (
    ProblemGenerator, CATEGORIES, CATEGORY_LABELS, CATEGORY_ICONS,
)
from src.ui.hud import HUD
from src.ui.button import Button
from src.ui.particles import ParticleSystem


class CafeScene:
    """Main gameplay scene — manage customers and diagnose problems."""

    def __init__(self, game):
        self.game = game
        self.hud = HUD()
        self.particles = ParticleSystem()
        self.problem_gen = ProblemGenerator()

        # State
        self.level = 1
        self.customers = []
        self.workstations = []
        self.customers_served = 0
        self.customers_total = 0
        self.customers_spawned = 0
        self.spawn_timer = 0
        self.customer_id_counter = 0
        self.level_complete = False
        self.level_complete_timer = 0
        self.level_time_limit = None
        self.level_time_remaining = None

        # Diagnosis popup state
        self.selected_customer = None
        self.showing_diagnosis = False
        self.diagnosis_buttons = []
        self.diagnosis_panel_rect = None
        self._click_cooldown = 0.0

        # Level transition
        self.transition_alpha = 0
        self.transitioning = False

    def enter(self, level=1, **kwargs):
        """Enter the café scene for a specific level."""
        self.level = level
        self.customers.clear()
        self.particles.clear()
        self.customers_served = 0
        self.customers_spawned = 0
        self.customer_id_counter = 0
        self.spawn_timer = 2.0  # Initial delay before first customer
        self.level_complete = False
        self.level_complete_timer = 0
        self.selected_customer = None
        self.showing_diagnosis = False
        self.transition_alpha = 255
        self.transitioning = True

        self.customers_total = get_level_customers(self.level)
        self.level_time_limit = get_level_time_limit(self.level)
        self.level_time_remaining = self.level_time_limit

        # Set up workstations
        self._setup_workstations()

        # Reset problem generator
        self.problem_gen.reset()

    def _setup_workstations(self):
        """Create workstations based on upgrade level."""
        self.workstations.clear()
        num_stations = self.game.upgrades.get("workstations",
                                               DEFAULT_WORKSTATIONS)
        total_width = num_stations * WORKSTATION_WIDTH + \
            (num_stations - 1) * 20
        start_x = (SCREEN_WIDTH - total_width) // 2

        for i in range(num_stations):
            x = start_x + i * (WORKSTATION_WIDTH + 20)
            ws = Workstation(i, x, WORKSTATION_Y)
            self.workstations.append(ws)

    def _get_patience(self):
        """Calculate customer patience for current level."""
        patience = BASE_PATIENCE - (self.level - 1) * PATIENCE_PER_LEVEL_REDUCE
        patience += self.game.upgrades.get("patience_bonus", 0)
        return max(MIN_PATIENCE, patience)

    def _spawn_customer(self):
        """Spawn a new customer if there's room."""
        # Find an empty workstation
        empty = [ws for ws in self.workstations
                 if not ws.occupied and ws.active]
        if not empty:
            return

        ws = random.choice(empty)
        problem = self.problem_gen.generate_single(self.level)
        patience = self._get_patience()
        self.customer_id_counter += 1

        customer = Customer(problem, patience, self.customer_id_counter)
        ws.assign_customer(customer)
        self.customers.append(customer)
        self.customers_spawned += 1

        self.game.sounds.play("arrive")

    def _open_diagnosis(self, customer):
        """Open diagnosis popup for a customer."""
        self.selected_customer = customer
        self.showing_diagnosis = True

        # Create diagnosis panel
        panel_w = 420
        panel_h = 400
        panel_x = SCREEN_WIDTH // 2 - panel_w // 2
        panel_y = SCREEN_HEIGHT // 2 - panel_h // 2
        self.diagnosis_panel_rect = pygame.Rect(panel_x, panel_y,
                                                panel_w, panel_h)

        # Create category buttons (below difficulty stars + instruction)
        self.diagnosis_buttons = []
        btn_w = 180
        btn_h = 54
        categories = CATEGORIES.copy()
        buttons_top = panel_y + 248

        # If diagnostic scanner upgrade, highlight the correct category
        has_scanner = self.game.upgrades.get("diagnostic_hint", False)

        for i, cat in enumerate(categories):
            row = i // 2
            col = i % 2
            bx = panel_x + 20 + col * (btn_w + 15)
            by = buttons_top + row * (btn_h + 12)

            accent = CATEGORY_COLORS.get(cat, COLOR_AMBER)

            # If scanner upgrade, dim wrong answers
            if has_scanner and cat == customer.problem.category:
                accent = COLOR_GREEN

            btn = Button(
                bx, by, btn_w, btn_h,
                CATEGORY_LABELS[cat],
                font_name="body",
                accent_color=accent,
                border_color=accent,
                icon_type=CATEGORY_ICONS[cat],
                icon_size=15,
            )
            btn._category = cat  # attach category data
            self.diagnosis_buttons.append(btn)

    def _close_diagnosis(self):
        """Close diagnosis popup."""
        self.showing_diagnosis = False
        self.selected_customer = None
        self.diagnosis_buttons.clear()

    def _handle_diagnosis(self, category):
        """Handle diagnosis selection."""
        customer = self.selected_customer
        if not customer:
            return

        correct = customer.problem.category
        if category == correct:
            # Correct diagnosis! Go to repair mini-game
            customer.start_repair()
            self.game.sounds.play("click")
            self._close_diagnosis()
            self.game.change_scene(SCENE_REPAIR,
                                    problem=customer.problem,
                                    customer=customer,
                                    level=self.level)
        else:
            # Wrong diagnosis — time penalty
            customer.patience -= WRONG_DIAGNOSIS_PENALTY
            self.game.sounds.play("error")
            self.particles.emit_text(
                SCREEN_WIDTH // 2,
                self.diagnosis_panel_rect.y - 10,
                "Wrong diagnosis! -3s",
                COLOR_RED, "body"
            )

    def _complete_repair(self, customer, success):
        """Called when returning from repair scene."""
        if success:
            # Calculate reward
            difficulty = customer.problem.difficulty
            reward = BASE_REWARD + difficulty * BONUS_PER_DIFFICULTY
            speed_bonus = int(customer.patience_ratio * 30)
            total_reward = reward + speed_bonus

            self.game.money += total_reward
            self.game.reputation = min(MAX_REPUTATION,
                                       self.game.reputation + REPUTATION_GAIN)
            self.customers_served += 1
            customer.finish_repair(True)

            # Particles
            cx = int(customer.x)
            cy = int(customer.y)
            self.particles.emit_sparkles(cx, cy, COLOR_AMBER, 20)
            self.particles.emit_money(cx, cy - 50, total_reward)
            self.particles.emit_reputation(cx + 40, cy - 30,
                                            REPUTATION_GAIN, True)
            self.game.sounds.play("money")
        else:
            # Failed repair
            self.game.reputation = max(MIN_REPUTATION,
                                       self.game.reputation - REPUTATION_LOSS // 2)
            customer.finish_repair(False)
            self.game.sounds.play("error")

    def _handle_angry_customer(self, customer):
        """Handle customer leaving angry."""
        self.game.reputation = max(MIN_REPUTATION,
                                   self.game.reputation - REPUTATION_LOSS)
        self.particles.emit_puff(int(customer.x), int(customer.y),
                                  COLOR_RED, 12)
        self.particles.emit_reputation(int(customer.x),
                                        int(customer.y) - 50,
                                        -REPUTATION_LOSS, False)
        self.game.sounds.play("angry")

    def handle_event(self, event):
        """Handle input events."""
        if self.transitioning:
            return

        if self._click_cooldown > 0:
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                return

        if self.showing_diagnosis:
            # Category buttons first (before "click outside" dismiss)
            for btn in self.diagnosis_buttons:
                if btn.handle_event(event):
                    self._handle_diagnosis(btn._category)
                    return

            # Dismiss only on release outside panel (avoid stealing button taps)
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if not self.diagnosis_panel_rect.collidepoint(event.pos):
                    on_button = any(
                        btn._hit_rect().collidepoint(event.pos)
                        for btn in self.diagnosis_buttons
                    )
                    if not on_button:
                        self._close_diagnosis()
                        self.game.sounds.play("click")
            return

        if self.level_complete:
            return

        # One tap per release (avoids duplicate finger + mouse events)
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for customer in self.customers:
                if customer.state == "waiting":
                    click_rect = customer.get_click_rect()
                    if click_rect.collidepoint(event.pos):
                        self._open_diagnosis(customer)
                        self._click_cooldown = 0.25
                        self.game.sounds.play("click")
                        return

    def update(self, dt):
        """Update game state."""
        self._click_cooldown = max(0.0, self._click_cooldown - dt)

        # Fade in transition
        if self.transitioning:
            self.transition_alpha = max(0, self.transition_alpha - 400 * dt)
            if self.transition_alpha <= 0:
                self.transitioning = False
            return

        if self.level_complete:
            self.level_complete_timer -= dt
            if self.level_complete_timer <= 0:
                if self.level >= MAX_LEVEL:
                    self.game.change_scene(SCENE_GAMEOVER, won=True)
                else:
                    self.game.change_scene(SCENE_UPGRADE, level=self.level)
            return

        # Update HUD
        self.hud.update(dt, self.game.money, self.game.reputation)

        # Level rush timer (harder levels from 6+)
        if self.level_time_remaining is not None:
            self.level_time_remaining -= dt
            if self.level_time_remaining <= 0:
                self.game.reputation = max(
                    MIN_REPUTATION,
                    self.game.reputation - REPUTATION_LOSS * 2,
                )
                self.particles.emit_text(
                    SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                    "Out of time!", COLOR_RED, "heading",
                )
                self.game.sounds.play("error")
                self.game.change_scene(SCENE_GAMEOVER, won=False)
                return

        # Spawn customers
        if self.customers_spawned < self.customers_total:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                self._spawn_customer()
                self.spawn_timer = get_level_spawn_interval(self.level)

        # Update customers
        angry_customers = []
        for customer in self.customers:
            prev_state = customer.state
            customer.update(dt)

            # Detect customer becoming angry
            if prev_state == "waiting" and customer.state == "angry":
                angry_customers.append(customer)

        for customer in angry_customers:
            self._handle_angry_customer(customer)

        # Release workstations for gone customers
        for ws in self.workstations:
            if ws.customer and ws.customer.state == "gone":
                ws.release_customer()

        # Remove gone customers
        self.customers = [c for c in self.customers if c.state != "gone"]

        # Update particles
        self.particles.update(dt)

        # Update diagnosis buttons
        if self.showing_diagnosis:
            for btn in self.diagnosis_buttons:
                btn.update(dt)

        # Check game over (reputation too low)
        if self.game.reputation <= MIN_REPUTATION:
            self.game.change_scene(SCENE_GAMEOVER, won=False)
            return

        # Check level complete
        all_done = (self.customers_spawned >= self.customers_total and
                    len(self.customers) == 0)
        if all_done and not self.level_complete:
            self.level_complete = True
            self.level_complete_timer = 2.5
            self.game.sounds.play("level_up")

    def draw(self, screen):
        """Draw the café scene."""
        # Background
        bg = self.game.assets.create_cafe_background()
        screen.blit(bg, (0, 0))

        # Workstations
        for ws in self.workstations:
            ws.draw(screen, self.game.assets)

        # Customers
        for customer in self.customers:
            customer.draw(screen, self.game.assets)

        # HUD
        self.hud.draw(screen, self.game.assets,
                      self.game.money, self.game.reputation,
                      self.level, self.customers_served,
                      self.customers_total,
                      level_time=self.level_time_remaining)

        # Particles
        self.particles.draw(screen, self.game.assets)

        # Diagnosis popup
        if self.showing_diagnosis and self.selected_customer:
            self._draw_diagnosis_popup(screen)

        # Level complete overlay
        if self.level_complete:
            self._draw_level_complete(screen)

        # Transition fade
        if self.transitioning and self.transition_alpha > 0:
            fade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade.fill(COLOR_BLACK)
            fade.set_alpha(int(self.transition_alpha))
            screen.blit(fade, (0, 0))

    def _draw_diagnosis_popup(self, screen):
        """Draw the diagnosis selection popup."""
        # Dim background
        dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 140))
        screen.blit(dim, (0, 0))

        assets = self.game.assets
        pr = self.diagnosis_panel_rect

        # Panel
        assets.draw_panel(screen, pr, alpha=240)

        # Title
        assets.draw_text_shadow(screen, "DIAGNOSE THE PROBLEM",
                                "heading", pr.centerx, pr.y + 30,
                                COLOR_AMBER, center=True)

        # Customer's complaint
        customer = self.selected_customer
        problem = customer.problem

        # Symptom
        y = pr.y + 70
        assets.draw_text_shadow(screen, f'"{problem.symptom}"',
                                "body", pr.centerx, y,
                                COLOR_CREAM, center=True)
        # Detail
        y += 35
        assets.draw_text_shadow(screen, problem.detail,
                                "small", pr.centerx, y,
                                COLOR_TEXT_DIM, center=True)

        # Difficulty stars (drawn — not Unicode)
        y += 32
        assets.draw_text_shadow(screen, "Difficulty",
                                "small", pr.centerx, y,
                                COLOR_TEXT_DIM, center=True)
        IconDrawer.draw_difficulty_row(
            screen, pr.centerx, y + 22, problem.difficulty,
            max_stars=5, size=11,
            filled_color=COLOR_AMBER,
            empty_color=COLOR_PANEL_BORDER,
        )

        # Instruction
        y += 48
        assets.draw_text_shadow(screen, "Select the problem category:",
                                "small", pr.centerx, y,
                                COLOR_TEXT_DIM, center=True)

        # Category buttons
        for btn in self.diagnosis_buttons:
            btn.draw(screen, assets)

    def _draw_level_complete(self, screen):
        """Draw level complete overlay."""
        dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 160))
        screen.blit(dim, (0, 0))

        assets = self.game.assets
        assets.draw_text_shadow(
            screen, f"{get_level_display_name(self.level).upper()} COMPLETE!",
            "title", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
            COLOR_AMBER, center=True)
        assets.draw_text_shadow(
            screen, f"Level {self.level} — {self.customers_total} customers served",
            "body", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 5,
            COLOR_CREAM, center=True)
        assets.draw_text_shadow(
            screen,
            f"Customers served: {self.customers_served}/{self.customers_total}",
            "heading", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30,
            COLOR_CREAM, center=True)

    def on_return_from_repair(self, customer, success):
        """Called when returning from the repair scene."""
        self._complete_repair(customer, success)
