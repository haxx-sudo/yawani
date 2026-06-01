"""
Sound generation using Pygame mixer — simple procedural sound effects.
"""
import pygame
import struct
import math


class SoundManager:
    """Generates and plays simple sound effects."""

    def __init__(self):
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self.enabled = True
        except pygame.error:
            self.enabled = False
            print("Warning: Sound could not be initialized.")
        self.cache = {}
        self.volume = 0.3
        if self.enabled:
            self._generate_sounds()

    def _generate_tone(self, frequency, duration, volume=0.3, wave="sine"):
        """Generate a tone as a pygame Sound object."""
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        buf = []

        for i in range(n_samples):
            t = i / sample_rate
            if wave == "sine":
                val = math.sin(2 * math.pi * frequency * t)
            elif wave == "square":
                val = 1.0 if math.sin(2 * math.pi * frequency * t) > 0 else -1.0
            elif wave == "sawtooth":
                val = 2 * (t * frequency - math.floor(t * frequency + 0.5))
            else:
                val = math.sin(2 * math.pi * frequency * t)

            # Apply envelope (fade in/out)
            env = 1.0
            fade_samples = int(n_samples * 0.1)
            if i < fade_samples:
                env = i / fade_samples
            elif i > n_samples - fade_samples:
                env = (n_samples - i) / fade_samples

            sample = int(val * volume * 32767 * env)
            sample = max(-32768, min(32767, sample))
            buf.append(struct.pack('<h', sample))

        raw = b''.join(buf)
        sound = pygame.mixer.Sound(buffer=raw)
        sound.set_volume(self.volume)
        return sound

    def _generate_sounds(self):
        """Pre-generate all game sounds."""
        # Click sound - short high beep
        self.cache["click"] = self._generate_tone(800, 0.05, 0.2)

        # Success - ascending two-tone
        s1 = self._generate_tone(523, 0.12, 0.3)  # C5
        s2 = self._generate_tone(659, 0.15, 0.3)  # E5
        self.cache["success_low"] = s1
        self.cache["success_high"] = s2

        # Error - low buzz
        self.cache["error"] = self._generate_tone(200, 0.2, 0.25, "square")

        # Money - coin sound (high ding)
        self.cache["money"] = self._generate_tone(1200, 0.08, 0.2)

        # Customer arrive - door bell
        self.cache["arrive"] = self._generate_tone(900, 0.1, 0.15)

        # Customer angry - low tone
        self.cache["angry"] = self._generate_tone(150, 0.3, 0.2, "sawtooth")

        # Virus pop
        self.cache["pop"] = self._generate_tone(600, 0.04, 0.2)

        # Level complete - fanfare
        self.cache["level_up"] = self._generate_tone(784, 0.2, 0.3)  # G5

        # Timer warning
        self.cache["tick"] = self._generate_tone(1000, 0.03, 0.1)

    def play(self, name):
        """Play a named sound effect."""
        if not self.enabled:
            return
        sound = self.cache.get(name)
        if sound:
            sound.play()

    def play_success(self):
        """Play a two-note success jingle."""
        if not self.enabled:
            return
        self.play("success_low")
        pygame.time.set_timer(pygame.USEREVENT + 99, 120, loops=1)
        # The second note will be triggered by the timer in game loop
        # For simplicity, just play both with a channel delay
        try:
            ch = pygame.mixer.find_channel()
            if ch:
                ch.play(self.cache.get("success_high", self.cache["click"]))
        except Exception:
            self.play("success_high")

    def set_volume(self, vol):
        """Set master volume (0.0 - 1.0)."""
        self.volume = max(0.0, min(1.0, vol))
        for sound in self.cache.values():
            sound.set_volume(self.volume)
