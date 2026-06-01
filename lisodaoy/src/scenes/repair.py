"""
Repair scene — four themed mini-games based on problem category.

Hardware:  Drag the correct component to the motherboard slot.
Software:  Pick the correct code fix from multiple choices.
Virus:     Click virus blobs before they spread.
Network:   Click network nodes in the correct order.
"""
import pygame
import math
import random
from src.constants import *
from src.ui.button import Button
from src.ui.particles import ParticleSystem
from src.utils.mobile import touch_radius_scale


class RepairScene:
    """Manages the four repair mini-games."""

    def __init__(self, game):
        self.game = game
        self.problem = None
        self.customer = None
        self.mode = None  # hardware, software, virus, network
        self.time_remaining = 0
        self.max_time = 0
        self.completed = False
        self.success = False
        self.result_timer = 0
        self.particles = ParticleSystem()

        # Mode-specific state
        self._hw_state = {}
        self._sw_state = {}
        self._vr_state = {}
        self._nw_state = {}
        self.level = 1

    def enter(self, problem=None, customer=None, level=1, **kwargs):
        """Start a repair mini-game."""
        self.problem = problem
        self.customer = customer
        self.mode = problem.category
        self.completed = False
        self.success = False
        self.result_timer = 0
        self.particles.clear()
        self.level = level

        # Time scales with problem difficulty and café level
        tool_bonus = self.game.upgrades.get("tool_bonus", 0)
        diff = problem.difficulty
        level_penalty = (level - 1) * MINIGAME_LEVEL_TIME_PENALTY
        self.max_time = (
            MINIGAME_BASE_TIME
            - (diff - 1) * MINIGAME_TIME_PER_DIFF
            - level_penalty
            + tool_bonus
        )
        self.max_time = max(5.0, self.max_time)
        self.time_remaining = self.max_time

        # Setup the specific mini-game
        if self.mode == "hardware":
            self._setup_hardware()
        elif self.mode == "software":
            self._setup_software()
        elif self.mode == "virus":
            self._setup_virus()
        elif self.mode == "network":
            self._setup_network()

    # =========================================================================
    # HARDWARE MINI-GAME — Component Swap
    # =========================================================================
    def _setup_hardware(self):
        """Setup the hardware component swap game."""
        data = self.problem.data
        correct_name = data.get("solution", "RAM Stick")

        # Find the correct component
        correct_comp = None
        for comp in HARDWARE_COMPONENTS:
            if comp["name"] == correct_name:
                correct_comp = comp
                break
        if not correct_comp:
            correct_comp = HARDWARE_COMPONENTS[0]

        # Pick 3 wrong components
        wrong = [c for c in HARDWARE_COMPONENTS
                 if c["name"] != correct_name]
        random.shuffle(wrong)
        wrong = wrong[:3]

        # All options shuffled
        options = [correct_comp] + wrong
        random.shuffle(options)

        # Component positions at bottom
        comp_rects = []
        total_w = len(options) * 120
        start_x = (SCREEN_WIDTH - total_w) // 2
        for i, comp in enumerate(options):
            rect = pygame.Rect(start_x + i * 120 + 10,
                               SCREEN_HEIGHT - 100, 100, 60)
            comp_rects.append(rect)

        # Motherboard slot position
        slot_rect = pygame.Rect(SCREEN_WIDTH // 2 - 55,
                                280, 110, 70)

        self._hw_state = {
            "correct": correct_comp,
            "options": options,
            "comp_rects": comp_rects,
            "slot_rect": slot_rect,
            "dragging": None,
            "drag_idx": -1,
            "drag_offset": (0, 0),
            "original_positions": [r.topleft for r in comp_rects],
            "shake_timer": 0,
            "placed": False,
        }

    def _handle_hardware_event(self, event):
        st = self._hw_state
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(st["comp_rects"]):
                if rect.collidepoint(event.pos) and not st["placed"]:
                    st["dragging"] = i
                    st["drag_idx"] = i
                    st["drag_offset"] = (event.pos[0] - rect.x,
                                         event.pos[1] - rect.y)
                    break

        elif event.type == pygame.MOUSEMOTION:
            if st["dragging"] is not None:
                idx = st["dragging"]
                st["comp_rects"][idx].x = event.pos[0] - st["drag_offset"][0]
                st["comp_rects"][idx].y = event.pos[1] - st["drag_offset"][1]

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if st["dragging"] is not None:
                idx = st["dragging"]
                comp = st["options"][idx]
                rect = st["comp_rects"][idx]

                # Check if dropped on slot
                if st["slot_rect"].colliderect(rect):
                    if comp["name"] == st["correct"]["name"]:
                        # Correct!
                        st["placed"] = True
                        rect.center = st["slot_rect"].center
                        self._mini_game_success()
                    else:
                        # Wrong component
                        st["shake_timer"] = 0.5
                        self.time_remaining -= 2.0
                        self.game.sounds.play("error")
                        # Return to original position
                        rect.topleft = st["original_positions"][idx]
                else:
                    # Return to original position
                    rect.topleft = st["original_positions"][idx]

                st["dragging"] = None

    def _update_hardware(self, dt):
        st = self._hw_state
        if st["shake_timer"] > 0:
            st["shake_timer"] -= dt

    def _draw_hardware(self, screen):
        st = self._hw_state
        assets = self.game.assets

        # Title
        assets.draw_text_shadow(screen, "HARDWARE REPAIR",
                                "heading", SCREEN_WIDTH // 2, 80,
                                COLOR_ORANGE, center=True)
        assets.draw_text_shadow(screen, "Drag the correct component to the slot!",
                                "body", SCREEN_WIDTH // 2, 120,
                                COLOR_TEXT_DIM, center=True)

        # Motherboard background
        mb_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 170, 300, 250)
        pygame.draw.rect(screen, (40, 80, 40), mb_rect, border_radius=8)
        pygame.draw.rect(screen, (60, 120, 60), mb_rect,
                         border_radius=8, width=2)
        # Circuit traces
        for i in range(5):
            y = 190 + i * 45
            pygame.draw.line(screen, (50, 100, 50),
                             (mb_rect.x + 20, y),
                             (mb_rect.x + mb_rect.width - 20, y), 1)

        # Slot (glowing)
        slot = st["slot_rect"]
        glow_alpha = int(128 + 127 * math.sin(pygame.time.get_ticks() / 200))
        glow_surf = pygame.Surface((slot.width + 20, slot.height + 20),
                                    pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (255, 200, 50, glow_alpha // 3),
                         glow_surf.get_rect(), border_radius=8)
        screen.blit(glow_surf, (slot.x - 10, slot.y - 10))

        if not st["placed"]:
            pygame.draw.rect(screen, COLOR_AMBER, slot,
                             border_radius=6, width=3)
            assets.draw_text_shadow(screen, "DROP HERE",
                                    "small", slot.centerx, slot.centery,
                                    COLOR_AMBER, center=True)
        else:
            pygame.draw.rect(screen, COLOR_GREEN, slot,
                             border_radius=6, width=3)

        # Shake effect
        shake_x = 0
        if st["shake_timer"] > 0:
            shake_x = int(math.sin(st["shake_timer"] * 40) * 5)

        # Components
        for i, (comp, rect) in enumerate(zip(st["options"],
                                              st["comp_rects"])):
            if i == st["dragging"]:
                # Draw shadow under dragged component
                shadow = pygame.Rect(rect.x + 4, rect.y + 4,
                                     rect.width, rect.height)
                pygame.draw.rect(screen, (0, 0, 0, 80), shadow,
                                 border_radius=6)

            draw_rect = rect.move(shake_x if i != st.get("dragging") else 0, 0)
            sprite = assets.create_component_sprite(
                comp["name"], comp["color"],
                rect.width, rect.height)
            screen.blit(sprite, draw_rect.topleft)

    # =========================================================================
    # SOFTWARE MINI-GAME — Code Fix
    # =========================================================================
    def _setup_software(self):
        data = self.problem.data
        bug_line = data.get("bug_line", "error = True")
        fix = data.get("fix", "error = False")
        wrong_fixes = data.get("wrong_fixes", ["error = None", "error = 0",
                                                 "error = 'maybe'"])

        # Build code context
        code_lines = [
            "#!/usr/bin/env python3",
            "import system_config",
            "",
            "def configure():",
            f"    {bug_line}  # ← BUG HERE",
            "    apply_settings()",
            "    return True",
            "",
            "configure()",
        ]

        # Create options
        options = [{"text": fix, "correct": True}]
        for wf in wrong_fixes[:3]:
            options.append({"text": wf, "correct": False})
        random.shuffle(options)

        # Create buttons
        buttons = []
        btn_w = 350
        btn_h = 45
        start_y = 480
        for i, opt in enumerate(options):
            btn = Button(
                SCREEN_WIDTH // 2 - btn_w // 2,
                start_y + i * (btn_h + 10),
                btn_w, btn_h,
                opt["text"],
                font_name="terminal",
                accent_color=COLOR_CYAN,
                icon_type="code",
                icon_size=14,
            )
            btn._correct = opt["correct"]
            buttons.append(btn)

        self._sw_state = {
            "code_lines": code_lines,
            "bug_line": bug_line,
            "buttons": buttons,
            "flash_color": None,
            "flash_timer": 0,
        }

    def _handle_software_event(self, event):
        st = self._sw_state
        for btn in st["buttons"]:
            if btn.handle_event(event):
                if btn._correct:
                    self._mini_game_success()
                else:
                    self.time_remaining -= 2.5
                    st["flash_color"] = COLOR_RED
                    st["flash_timer"] = 0.3
                    self.game.sounds.play("error")
                    # Disable wrong button
                    btn.enabled = False

    def _update_software(self, dt):
        st = self._sw_state
        for btn in st["buttons"]:
            btn.update(dt)
        if st["flash_timer"] > 0:
            st["flash_timer"] -= dt

    def _draw_software(self, screen):
        st = self._sw_state
        assets = self.game.assets

        # Title
        assets.draw_text_shadow(screen, "SOFTWARE FIX",
                                "heading", SCREEN_WIDTH // 2, 80,
                                COLOR_CYAN, center=True)
        assets.draw_text_shadow(screen, "Select the correct fix for the bug!",
                                "body", SCREEN_WIDTH // 2, 120,
                                COLOR_TEXT_DIM, center=True)

        # Terminal window
        term_rect = pygame.Rect(SCREEN_WIDTH // 2 - 240, 160, 480, 280)
        pygame.draw.rect(screen, (15, 15, 20), term_rect, border_radius=8)
        pygame.draw.rect(screen, (40, 40, 50), term_rect,
                         border_radius=8, width=2)

        # Terminal title bar
        title_bar = pygame.Rect(term_rect.x, term_rect.y,
                                term_rect.width, 25)
        pygame.draw.rect(screen, (40, 40, 50), title_bar,
                         border_top_left_radius=8,
                         border_top_right_radius=8)
        # Window buttons
        for i, color in enumerate([(255, 95, 86), (255, 189, 46),
                                    (39, 201, 63)]):
            pygame.draw.circle(screen, color,
                               (term_rect.x + 15 + i * 20,
                                term_rect.y + 12), 5)

        # Code lines
        font = assets.get_font("terminal")
        y = term_rect.y + 35
        for line in st["code_lines"]:
            is_bug = "BUG HERE" in line
            color = COLOR_RED if is_bug else COLOR_GREEN
            if is_bug:
                # Highlight background
                highlight = pygame.Surface(
                    (term_rect.width - 20, 22), pygame.SRCALPHA)
                highlight.fill((255, 0, 0, 30))
                screen.blit(highlight, (term_rect.x + 10, y - 2))

            text = font.render(line, True, color)
            screen.blit(text, (term_rect.x + 15, y))
            y += 24

        # Flash effect
        if st["flash_timer"] > 0:
            flash = pygame.Surface(
                (term_rect.width, term_rect.height), pygame.SRCALPHA)
            a = int(100 * (st["flash_timer"] / 0.3))
            flash.fill((*st["flash_color"][:3], a))
            screen.blit(flash, term_rect.topleft)

        # Fix options label
        assets.draw_text_shadow(screen, "Choose the fix:",
                                "body", SCREEN_WIDTH // 2, 460,
                                COLOR_TEXT_DIM, center=True)

        # Buttons
        for btn in st["buttons"]:
            btn.draw(screen, assets)

    # =========================================================================
    # VIRUS MINI-GAME — Click to Destroy
    # =========================================================================
    def _setup_virus(self):
        data = self.problem.data
        diff = data.get("difficulty", 1)
        target_kills = (
            VIRUS_TARGET_KILLS
            + (diff - 1) * VIRUS_EXTRA_PER_DIFF
            + (self.level - 1) * VIRUS_EXTRA_PER_LEVEL
        )

        self._vr_state = {
            "viruses": [],
            "kills": 0,
            "target_kills": target_kills,
            "spawn_timer": 1.0,  # delay before first spawn
            "spawn_interval": max(
                0.3,
                VIRUS_SPAWN_RATE - diff * 0.15 - self.level * 0.04,
            ),
            "virus_name": data.get("virus_name", "Malware"),
            "pop_effects": [],  # (x, y, timer)
        }

        # Spawn initial viruses
        for _ in range(3):
            self._spawn_virus()

    def _spawn_virus(self):
        margin = 80
        diff = self.problem.difficulty
        virus = {
            "x": random.randint(margin, SCREEN_WIDTH - margin),
            "y": random.randint(180, SCREEN_HEIGHT - 150),
            "size": random.randint(18, 28),
            "grow_rate": random.uniform(3, 8) + diff * 0.4 + self.level * 0.15,
            "max_size": random.randint(45, 60) + diff * 3,
            "vx": random.uniform(-30, 30),
            "vy": random.uniform(-20, 20),
            "alive": True,
        }
        self._vr_state["viruses"].append(virus)

    def _handle_virus_event(self, event):
        st = self._vr_state
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for virus in st["viruses"]:
                if not virus["alive"]:
                    continue
                dx = mx - virus["x"]
                dy = my - virus["y"]
                hit_r = virus["size"] * touch_radius_scale()
                if dx * dx + dy * dy <= hit_r * hit_r:
                    virus["alive"] = False
                    st["kills"] += 1
                    st["pop_effects"].append({
                        "x": virus["x"], "y": virus["y"],
                        "timer": 0.3,
                    })
                    self.particles.emit_sparkles(
                        virus["x"], virus["y"], COLOR_GREEN, 8)
                    self.game.sounds.play("pop")

                    # Check win
                    if st["kills"] >= st["target_kills"]:
                        self._mini_game_success()
                    break

    def _update_virus(self, dt):
        st = self._vr_state

        # Remove dead viruses
        st["viruses"] = [v for v in st["viruses"] if v["alive"]]

        # Spawn new viruses
        st["spawn_timer"] -= dt
        if st["spawn_timer"] <= 0:
            self._spawn_virus()
            st["spawn_timer"] = st["spawn_interval"]

        # Update viruses
        for virus in st["viruses"]:
            virus["size"] = min(virus["max_size"],
                                virus["size"] + virus["grow_rate"] * dt)
            virus["x"] += virus["vx"] * dt
            virus["y"] += virus["vy"] * dt

            # Bounce off walls
            if virus["x"] < 60 or virus["x"] > SCREEN_WIDTH - 60:
                virus["vx"] *= -1
            if virus["y"] < 160 or virus["y"] > SCREEN_HEIGHT - 120:
                virus["vy"] *= -1

            # Split if too big
            if virus["size"] >= virus["max_size"]:
                virus["size"] = virus["max_size"] * 0.6
                self._spawn_virus()

        # Update pop effects
        st["pop_effects"] = [
            {**p, "timer": p["timer"] - dt}
            for p in st["pop_effects"] if p["timer"] > 0
        ]

    def _draw_virus(self, screen):
        st = self._vr_state
        assets = self.game.assets

        # Title
        assets.draw_text_shadow(screen, f"VIRUS SCAN: {st['virus_name']}",
                                "heading", SCREEN_WIDTH // 2, 80,
                                COLOR_RED, center=True)

        # Kill counter
        progress = st["kills"] / max(1, st["target_kills"])
        assets.draw_text_shadow(
            screen,
            f"Eliminated: {st['kills']}/{st['target_kills']}",
            "body", SCREEN_WIDTH // 2, 120,
            COLOR_TEXT_DIM, center=True)
        assets.draw_progress_bar(screen,
                                  SCREEN_WIDTH // 2 - 100, 145,
                                  200, 12, progress, COLOR_GREEN)

        # Scan lines effect
        scan_y = (pygame.time.get_ticks() // 3) % SCREEN_HEIGHT
        scan_surf = pygame.Surface((SCREEN_WIDTH, 3), pygame.SRCALPHA)
        scan_surf.fill((0, 255, 100, 20))
        screen.blit(scan_surf, (0, scan_y))

        # Viruses
        for virus in st["viruses"]:
            if virus["alive"]:
                sprite = assets.create_virus_sprite(int(virus["size"]))
                screen.blit(sprite,
                            (int(virus["x"]) - virus["size"],
                             int(virus["y"]) - virus["size"]))

        # Pop effects
        for pop in st["pop_effects"]:
            t = max(0.0, min(1.0, pop["timer"] / 0.3))
            r = int(30 * (1 - t))
            if r < 2:
                continue
            alpha = max(0, min(255, int(200 * t)))
            surf = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (0, 255, 100, alpha),
                               (r + 1, r + 1), r, 2)
            screen.blit(surf, (int(pop["x"]) - r - 1,
                               int(pop["y"]) - r - 1))

    # =========================================================================
    # NETWORK MINI-GAME — Node Sequence
    # =========================================================================
    def _setup_network(self):
        data = self.problem.data
        diff = data.get("difficulty", 1)
        num_nodes = data.get(
            "node_count",
            NETWORK_BASE_NODES + (diff - 1) * NETWORK_EXTRA_PER_DIFF,
        )
        num_nodes += (self.level - 1) // 3
        num_nodes = min(num_nodes, 12)

        # Generate node positions in a nice layout
        nodes = []
        margin = 100
        for i in range(num_nodes):
            attempts = 0
            while attempts < 50:
                x = random.randint(margin, SCREEN_WIDTH - margin)
                y = random.randint(220, SCREEN_HEIGHT - 160)
                # Check minimum distance from other nodes
                too_close = False
                for n in nodes:
                    dx = x - n["x"]
                    dy = y - n["y"]
                    if dx * dx + dy * dy < 90 * 90:
                        too_close = True
                        break
                if not too_close:
                    break
                attempts += 1

            nodes.append({
                "x": x, "y": y,
                "label": i + 1,
                "active": False,
                "highlighted": False,
            })

        self._nw_state = {
            "nodes": nodes,
            "current_idx": 0,  # which node to click next (0-indexed)
            "connections": [],  # list of (from_idx, to_idx) for drawn lines
            "wrong_flash": 0,
        }

    def _handle_network_event(self, event):
        st = self._nw_state
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for i, node in enumerate(st["nodes"]):
                dx = mx - node["x"]
                dy = my - node["y"]
                hit_r = 40 * touch_radius_scale()
                if dx * dx + dy * dy <= hit_r * hit_r:
                    if i == st["current_idx"]:
                        # Correct node!
                        node["active"] = True
                        if st["current_idx"] > 0:
                            st["connections"].append(
                                (st["current_idx"] - 1, st["current_idx"]))
                        st["current_idx"] += 1
                        self.game.sounds.play("click")
                        self.particles.emit_sparkles(
                            node["x"], node["y"], COLOR_GREEN, 10)

                        # Check win
                        if st["current_idx"] >= len(st["nodes"]):
                            self._mini_game_success()
                    else:
                        # Wrong node
                        st["wrong_flash"] = 0.4
                        self.time_remaining -= 1.5
                        self.game.sounds.play("error")
                    break

    def _update_network(self, dt):
        st = self._nw_state
        if st["wrong_flash"] > 0:
            st["wrong_flash"] -= dt

        # Highlight the next node to click
        for i, node in enumerate(st["nodes"]):
            node["highlighted"] = (i == st["current_idx"])

    def _draw_network(self, screen):
        st = self._nw_state
        assets = self.game.assets

        # Title
        assets.draw_text_shadow(screen, "NETWORK REPAIR",
                                "heading", SCREEN_WIDTH // 2, 80,
                                COLOR_GREEN, center=True)
        assets.draw_text_shadow(
            screen, "Click nodes in order (1, 2, 3...) to restore connection!",
            "body", SCREEN_WIDTH // 2, 120,
            COLOR_TEXT_DIM, center=True)

        # Progress
        total = len(st["nodes"])
        done = st["current_idx"]
        assets.draw_text_shadow(
            screen, f"Connected: {done}/{total}",
            "body", SCREEN_WIDTH // 2, 155,
            COLOR_TEXT_DIM, center=True)

        # Draw connections (completed)
        for from_idx, to_idx in st["connections"]:
            n1 = st["nodes"][from_idx]
            n2 = st["nodes"][to_idx]
            # Glow line
            for w in [6, 3, 1]:
                alpha = 60 if w == 6 else (150 if w == 3 else 255)
                surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT),
                                       pygame.SRCALPHA)
                pygame.draw.line(surf, (*COLOR_GREEN[:3], alpha),
                                 (n1["x"], n1["y"]), (n2["x"], n2["y"]), w)
                screen.blit(surf, (0, 0))

        # Draw nodes
        for node in st["nodes"]:
            sprite = assets.create_network_node(
                node["label"], 30,
                active=node["active"],
                highlighted=node["highlighted"])
            screen.blit(sprite,
                        (node["x"] - sprite.get_width() // 2,
                         node["y"] - sprite.get_height() // 2))

        # Wrong flash
        if st["wrong_flash"] > 0:
            flash = pygame.Surface(
                (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            a = int(60 * (st["wrong_flash"] / 0.4))
            flash.fill((255, 0, 0, a))
            screen.blit(flash, (0, 0))

    # =========================================================================
    # Common Mini-game Logic
    # =========================================================================
    def _mini_game_success(self):
        """Called when any mini-game is completed successfully."""
        self.success = True
        self.completed = True
        self.result_timer = 1.8
        self.particles.emit_sparkles(SCREEN_WIDTH // 2,
                                      SCREEN_HEIGHT // 2,
                                      COLOR_GREEN, 30)
        self.game.sounds.play_success()

    def _mini_game_fail(self):
        """Called when time runs out."""
        self.success = False
        self.completed = True
        self.result_timer = 1.8
        self.game.sounds.play("error")

    def handle_event(self, event):
        if self.completed:
            return

        if self.mode == "hardware":
            self._handle_hardware_event(event)
        elif self.mode == "software":
            self._handle_software_event(event)
        elif self.mode == "virus":
            self._handle_virus_event(event)
        elif self.mode == "network":
            self._handle_network_event(event)

    def update(self, dt):
        self.particles.update(dt)

        if self.completed:
            self.result_timer -= dt
            if self.result_timer <= 0:
                # Return to café
                cafe = self.game.scenes[SCENE_CAFE]
                cafe.on_return_from_repair(self.customer, self.success)
                self.game.current_scene = SCENE_CAFE
            return

        # Timer countdown
        self.time_remaining -= dt
        if self.time_remaining <= 0:
            self.time_remaining = 0
            self._mini_game_fail()
            return

        # Tick sound for low time
        if self.time_remaining < 5 and int(self.time_remaining * 2) % 2 == 0:
            pass  # tick is too annoying, skip

        # Mode-specific update
        if self.mode == "hardware":
            self._update_hardware(dt)
        elif self.mode == "software":
            self._update_software(dt)
        elif self.mode == "virus":
            self._update_virus(dt)
        elif self.mode == "network":
            self._update_network(dt)

    def draw(self, screen):
        # Dark background
        screen.fill(COLOR_BG)

        # Subtle grid pattern
        grid_color = (35, 25, 18)
        for gx in range(0, SCREEN_WIDTH, 30):
            pygame.draw.line(screen, grid_color,
                             (gx, 0), (gx, SCREEN_HEIGHT))
        for gy in range(0, SCREEN_HEIGHT, 30):
            pygame.draw.line(screen, grid_color,
                             (0, gy), (SCREEN_WIDTH, gy))

        # Mode-specific draw
        if self.mode == "hardware":
            self._draw_hardware(screen)
        elif self.mode == "software":
            self._draw_software(screen)
        elif self.mode == "virus":
            self._draw_virus(screen)
        elif self.mode == "network":
            self._draw_network(screen)

        # Timer bar at top
        self._draw_timer(screen)

        # Particles
        self.particles.draw(screen, self.game.assets)

        # Result overlay
        if self.completed:
            self._draw_result(screen)

    def _draw_timer(self, screen):
        """Draw the countdown timer bar."""
        assets = self.game.assets
        progress = self.time_remaining / self.max_time
        color = COLOR_GREEN if progress > 0.3 else (
            COLOR_YELLOW if progress > 0.15 else COLOR_RED)

        # Timer bar background
        bar_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 35)
        pygame.draw.rect(screen, (20, 15, 10), bar_rect)

        # Fill
        fill_w = int(SCREEN_WIDTH * progress)
        if fill_w > 0:
            pygame.draw.rect(screen, color, (0, 0, fill_w, 35))
            # Glow at end
            glow = pygame.Surface((20, 35), pygame.SRCALPHA)
            glow.fill((*color[:3], 100))
            screen.blit(glow, (fill_w - 10, 0))

        # Timer text
        secs = max(0, self.time_remaining)
        timer_text = f"{secs:.1f}s"
        assets.draw_text_shadow(screen, timer_text, "hud",
                                SCREEN_WIDTH // 2, 18,
                                COLOR_WHITE, center=True)

        # Bottom border
        pygame.draw.line(screen, COLOR_PANEL_BORDER,
                         (0, 35), (SCREEN_WIDTH, 35), 2)

    def _draw_result(self, screen):
        """Draw success/fail result overlay."""
        dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 160))
        screen.blit(dim, (0, 0))

        assets = self.game.assets
        if self.success:
            assets.draw_text_shadow(screen, "✓ FIXED!",
                                    "title", SCREEN_WIDTH // 2,
                                    SCREEN_HEIGHT // 2 - 20,
                                    COLOR_GREEN, center=True)
        else:
            assets.draw_text_shadow(screen, "✗ TIME'S UP!",
                                    "title", SCREEN_WIDTH // 2,
                                    SCREEN_HEIGHT // 2 - 20,
                                    COLOR_RED, center=True)
