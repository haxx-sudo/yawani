"""
Main Game class — initializes Pygame, manages scenes and state.
"""
import pygame
from src.constants import *
from src.utils.assets import AssetManager
from src.utils.sounds import SoundManager
from src.utils.mobile import MobileDisplay
from src.ui.mobile_controls import MobileControls
from src.scenes.menu import MenuScene
from src.scenes.cafe import CafeScene
from src.scenes.repair import RepairScene
from src.scenes.upgrade import UpgradeScene
from src.scenes.gameover import GameOverScene
from src.scenes.packet_tracer import PacketTracerScene


class Game:
    """Core game engine managing the main loop and scene transitions."""

    def __init__(self, force_mobile=False):
        pygame.init()
        self.mobile_display = MobileDisplay(force_mobile=force_mobile)
        self.mobile_display.setup()
        self.screen = self.mobile_display.screen
        self.render_surface = self.mobile_display.render_surface
        self.clock = pygame.time.Clock()
        self.running = True

        self.mobile_controls = (
            MobileControls(self) if self.mobile_display.mobile else None
        )

        # Shared resources
        self.assets = AssetManager()
        self.sounds = SoundManager()

        # Persistent game state
        self.money = STARTING_MONEY
        self.reputation = STARTING_REPUTATION
        self.high_score = 0
        self.upgrades = {
            "workstations": DEFAULT_WORKSTATIONS,
            "workstation_level": 0,
            "tools_level": 0,
            "tool_bonus": 0,
            "coffee_level": 0,
            "patience_bonus": 0,
            "diagnostic_level": 0,
            "diagnostic_hint": False,
            "reputation_level": 0,
        }

        # Scene management
        self.scenes = {
            SCENE_MENU: MenuScene(self),
            SCENE_CAFE: CafeScene(self),
            SCENE_REPAIR: RepairScene(self),
            SCENE_UPGRADE: UpgradeScene(self),
            SCENE_GAMEOVER: GameOverScene(self),
            SCENE_PACKET_TRACER: PacketTracerScene(self),
        }
        self.current_scene = SCENE_MENU
        self.scenes[SCENE_MENU].enter()

    def change_scene(self, scene_name, **kwargs):
        """Transition to a new scene."""
        if scene_name in self.scenes:
            self.scenes[scene_name].enter(**kwargs)
            self.current_scene = scene_name

    def start_new_game(self):
        """Reset state and start a new game."""
        self.money = STARTING_MONEY
        self.reputation = STARTING_REPUTATION
        self.upgrades = {
            "workstations": DEFAULT_WORKSTATIONS,
            "workstation_level": 0,
            "tools_level": 0,
            "tool_bonus": 0,
            "coffee_level": 0,
            "patience_bonus": 0,
            "diagnostic_level": 0,
            "diagnostic_hint": False,
            "reputation_level": 0,
        }
        if "cafe_bg" in self.assets.cache:
            del self.assets.cache["cafe_bg"]

        self.change_scene(SCENE_CAFE, level=1)

    def start_packet_tracer(self):
        """Open standalone Packet Tracer practice mode."""
        self.change_scene(SCENE_PACKET_TRACER, scenario_idx=0)

    def _handle_global_keys(self, event):
        """Keyboard shortcuts (desktop)."""
        if event.type != pygame.KEYDOWN:
            return False
        if event.key in (pygame.K_ESCAPE, pygame.K_AC_BACK):
            if self.current_scene == SCENE_CAFE:
                self.change_scene(SCENE_MENU)
            elif self.current_scene in (
                SCENE_UPGRADE, SCENE_GAMEOVER, SCENE_PACKET_TRACER,
            ):
                self.change_scene(SCENE_MENU)
            return True
        if event.key == pygame.K_m:
            if self.sounds.volume > 0:
                self.sounds.set_volume(0)
            else:
                self.sounds.set_volume(0.3)
            return True
        return False

    def run(self):
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)

            scene = self.scenes[self.current_scene]

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    continue

                event = self.mobile_display.translate_event(event)
                if event is None:
                    continue

                if self._handle_global_keys(event):
                    continue

                cafe_diag = (
                    self.current_scene == SCENE_CAFE
                    and getattr(scene, "showing_diagnosis", False)
                )
                skip_mobile = (
                    self.current_scene == SCENE_PACKET_TRACER or cafe_diag
                )
                if (self.mobile_controls
                        and not skip_mobile
                        and self.mobile_controls.handle_event(event)):
                    continue

                scene.handle_event(event)

            scene.update(dt)

            scene.draw(self.render_surface)
            if (self.mobile_controls
                    and self.current_scene != SCENE_PACKET_TRACER):
                self.mobile_controls.draw(self.render_surface, self.assets)

            self.mobile_display.present()

        pygame.quit()
