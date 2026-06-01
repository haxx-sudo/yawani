"""
Tech Support Café — Entry point.

Desktop:
  python main.py
  Mouse click — interact | ESC — menu | M — mute

Mobile / touch testing:
  python main.py --mobile

Packet Tracer practice (from main menu):
  Click PACKET TRACER — trace routes & fix IPs like Cisco PT

Android APK (Linux or WSL with buildozer):
  buildozer android debug deploy run
"""
import os
import sys
from src.game import Game


def main():
    force_mobile = "--mobile" in sys.argv
    if force_mobile:
        os.environ["TECH_CAFE_MOBILE"] = "1"
    game = Game(force_mobile=force_mobile)
    game.run()


if __name__ == "__main__":
    main()
