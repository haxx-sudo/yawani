"""
Problem definitions — symptoms, categories, solutions, and difficulty.
"""
import random
from src.constants import get_difficulty_range


# =============================================================================
# Problem Database
# =============================================================================

PROBLEMS = {
    "hardware": [
        {
            "symptom": "Computer won't turn on at all!",
            "detail": "No lights, no fan spin, completely dead.",
            "solution": "Power Supply",
            "difficulty": 1,
        },
        {
            "symptom": "Screen keeps flickering and showing artifacts.",
            "detail": "Random colored lines appear during use.",
            "solution": "Graphics Card",
            "difficulty": 2,
        },
        {
            "symptom": "Computer beeps and won't boot.",
            "detail": "Three short beeps on startup, black screen.",
            "solution": "RAM Stick",
            "difficulty": 2,
        },
        {
            "symptom": "Everything is extremely slow and laggy.",
            "detail": "Programs take forever to load from disk.",
            "solution": "SSD Drive",
            "difficulty": 3,
        },
        {
            "symptom": "Computer shuts down randomly after a few minutes.",
            "detail": "Gets very hot before shutting off.",
            "solution": "Cooling Fan",
            "difficulty": 3,
        },
        {
            "symptom": "Weird clicking sounds from inside the case.",
            "detail": "Performance drops and files are corrupting.",
            "solution": "SSD Drive",
            "difficulty": 4,
        },
        {
            "symptom": "Blue screen every time I try to run a game.",
            "detail": "Error mentions display driver crash.",
            "solution": "Graphics Card",
            "difficulty": 4,
        },
        {
            "symptom": "Computer freezes during heavy processing.",
            "detail": "CPU usage spikes to 100% then everything locks.",
            "solution": "CPU Chip",
            "difficulty": 5,
        },
        {
            "symptom": "Monitor says 'No Signal' but PC is on.",
            "detail": "Fans spin, keyboard lights work, black screen.",
            "solution": "Graphics Card",
            "difficulty": 2,
        },
        {
            "symptom": "Laptop won't charge past 15%.",
            "detail": "Battery icon flashes even when plugged in.",
            "solution": "Power Supply",
            "difficulty": 2,
        },
        {
            "symptom": "USB ports stopped working entirely.",
            "detail": "Mouse and keyboard don't respond on any port.",
            "solution": "CPU Chip",
            "difficulty": 3,
        },
        {
            "symptom": "Loud coil whine and stuttering in games.",
            "detail": "Happens when the GPU is under load.",
            "solution": "Power Supply",
            "difficulty": 4,
        },
        {
            "symptom": "RAM error after installing new sticks.",
            "detail": "BIOS only sees half the installed memory.",
            "solution": "RAM Stick",
            "difficulty": 3,
        },
        {
            "symptom": "PC powers on then instantly shuts off.",
            "detail": "Repeats in a loop every two seconds.",
            "solution": "Power Supply",
            "difficulty": 5,
        },
        {
            "symptom": "Fans roar but the PC stays frozen on the logo.",
            "detail": "Never reaches the boot menu, just a still screen.",
            "solution": "RAM Stick",
            "difficulty": 3,
        },
        {
            "symptom": "Stutters and frame drops only while gaming.",
            "detail": "GPU temps hit 95\u00b0C within minutes.",
            "solution": "Cooling Fan",
            "difficulty": 4,
        },
        {
            "symptom": "Operating system reinstall fails halfway.",
            "detail": "Disk read errors reported during copy.",
            "solution": "SSD Drive",
            "difficulty": 4,
        },
        {
            "symptom": "Random freezes when many tabs are open.",
            "detail": "Memory diagnostic flags failing addresses.",
            "solution": "RAM Stick",
            "difficulty": 4,
        },
        {
            "symptom": "Thermal throttling under any real workload.",
            "detail": "Clock speed drops to a crawl when warm.",
            "solution": "CPU Chip",
            "difficulty": 5,
        },
        {
            "symptom": "Display works in safe mode only.",
            "detail": "Garbled output once full drivers load.",
            "solution": "Graphics Card",
            "difficulty": 3,
        },
    ],
    "software": [
        {
            "symptom": "My browser won't open any websites.",
            "detail": "Says 'page not found' for every site.",
            "bug_line": "dns_config = 'disabled'",
            "fix": "dns_config = 'auto'",
            "wrong_fixes": ["dns_config = 'manual'", "dns_config = None",
                            "dns_config = 'static'"],
            "difficulty": 1,
        },
        {
            "symptom": "All my files show as read-only!",
            "detail": "Can't edit or save anything.",
            "bug_line": "permissions = 0o444",
            "fix": "permissions = 0o644",
            "wrong_fixes": ["permissions = 0o000", "permissions = 0o111",
                            "permissions = 0o400"],
            "difficulty": 2,
        },
        {
            "symptom": "My printer only prints blank pages.",
            "detail": "Printer is connected but output is empty.",
            "bug_line": "output_stream = '/dev/null'",
            "fix": "output_stream = '/dev/lp0'",
            "wrong_fixes": ["output_stream = '/dev/zero'",
                            "output_stream = '/dev/random'",
                            "output_stream = None"],
            "difficulty": 2,
        },
        {
            "symptom": "Computer clock is always wrong!",
            "detail": "Time resets to 1970 on every boot.",
            "bug_line": "ntp_sync = False",
            "fix": "ntp_sync = True",
            "wrong_fixes": ["ntp_sync = 'manual'", "ntp_sync = 0",
                            "ntp_sync = None"],
            "difficulty": 1,
        },
        {
            "symptom": "Programs crash with 'out of memory' error.",
            "detail": "Even with plenty of RAM available.",
            "bug_line": "max_memory = 64  # MB",
            "fix": "max_memory = 4096  # MB",
            "wrong_fixes": ["max_memory = 0  # MB", "max_memory = 32  # MB",
                            "max_memory = -1  # MB"],
            "difficulty": 3,
        },
        {
            "symptom": "Screen rotation is upside down!",
            "detail": "Everything is flipped 180 degrees.",
            "bug_line": "display_rotation = 180",
            "fix": "display_rotation = 0",
            "wrong_fixes": ["display_rotation = 90",
                            "display_rotation = 270",
                            "display_rotation = 360"],
            "difficulty": 1,
        },
        {
            "symptom": "System boots to command line, no desktop!",
            "detail": "Only see a blinking cursor after login.",
            "bug_line": "default_target = 'multi-user'",
            "fix": "default_target = 'graphical'",
            "wrong_fixes": ["default_target = 'rescue'",
                            "default_target = 'emergency'",
                            "default_target = 'network'"],
            "difficulty": 3,
        },
        {
            "symptom": "All text appears as tiny unreadable font.",
            "detail": "System DPI settings seem wrong.",
            "bug_line": "display_scale = 0.25",
            "fix": "display_scale = 1.0",
            "wrong_fixes": ["display_scale = 0.1",
                            "display_scale = 5.0",
                            "display_scale = -1.0"],
            "difficulty": 2,
        },
        {
            "symptom": "Windows update broke my WiFi driver!",
            "detail": "Worked fine before last night's update.",
            "bug_line": "wifi_driver = 'disabled'",
            "fix": "wifi_driver = 'enabled'",
            "wrong_fixes": ["wifi_driver = 'blocked'",
                            "wifi_driver = None",
                            "wifi_driver = 'legacy'"],
            "difficulty": 3,
        },
        {
            "symptom": "Firewall is blocking everything!",
            "detail": "Can't open browser, email, or games.",
            "bug_line": "firewall_mode = 'block_all'",
            "fix": "firewall_mode = 'smart'",
            "wrong_fixes": ["firewall_mode = 'off'",
                            "firewall_mode = 'paranoid'",
                            "firewall_mode = 0"],
            "difficulty": 3,
        },
        {
            "symptom": "Bluetooth won't pair with anything.",
            "detail": "Devices show up then disappear.",
            "bug_line": "bluetooth_stack = 'legacy'",
            "fix": "bluetooth_stack = 'modern'",
            "wrong_fixes": ["bluetooth_stack = 'off'",
                            "bluetooth_stack = None",
                            "bluetooth_stack = 'debug'"],
            "difficulty": 2,
        },
        {
            "symptom": "Email stuck in outbox forever.",
            "detail": "Send button spins but nothing leaves.",
            "bug_line": "smtp_port = 0",
            "fix": "smtp_port = 587",
            "wrong_fixes": ["smtp_port = 1",
                            "smtp_port = -1",
                            "smtp_port = 99999"],
            "difficulty": 4,
        },
        {
            "symptom": "Auto-login keeps failing at startup.",
            "detail": "Password is correct but session won't start.",
            "bug_line": "session_type = 'none'",
            "fix": "session_type = 'desktop'",
            "wrong_fixes": ["session_type = 'headless'",
                            "session_type = 'locked'",
                            "session_type = 0"],
            "difficulty": 4,
        },
        {
            "symptom": "Microphone is always muted system-wide.",
            "detail": "Privacy settings look fine in the app.",
            "bug_line": "audio_input = 'muted'",
            "fix": "audio_input = 'active'",
            "wrong_fixes": ["audio_input = 'off'",
                            "audio_input = None",
                            "audio_input = 'silent'"],
            "difficulty": 2,
        },
        {
            "symptom": "Touchpad scrolling goes the wrong way.",
            "detail": "Two-finger scroll is inverted after update.",
            "bug_line": "natural_scroll = True",
            "fix": "natural_scroll = False",
            "wrong_fixes": ["natural_scroll = None",
                            "natural_scroll = 2",
                            "natural_scroll = 'auto'"],
            "difficulty": 1,
        },
        {
            "symptom": "App keeps opening on the wrong monitor.",
            "detail": "Always launches on the disconnected display.",
            "bug_line": "default_monitor = 2",
            "fix": "default_monitor = 1",
            "wrong_fixes": ["default_monitor = 0",
                            "default_monitor = -1",
                            "default_monitor = 99"],
            "difficulty": 2,
        },
        {
            "symptom": "Scheduled backups never run.",
            "detail": "Task shows enabled but log stays empty.",
            "bug_line": "backup_cron = '0 0 31 2 *'",
            "fix": "backup_cron = '0 2 * * *'",
            "wrong_fixes": ["backup_cron = 'never'",
                            "backup_cron = '* * * * 9'",
                            "backup_cron = None"],
            "difficulty": 4,
        },
        {
            "symptom": "HTTPS sites all show certificate errors.",
            "detail": "System trusts nothing after a tweak.",
            "bug_line": "verify_ssl = 'ignore'",
            "fix": "verify_ssl = 'strict'",
            "wrong_fixes": ["verify_ssl = 'off'",
                            "verify_ssl = None",
                            "verify_ssl = 0"],
            "difficulty": 3,
        },
        {
            "symptom": "Laptop never goes to sleep when idle.",
            "detail": "Battery drains overnight with lid closed.",
            "bug_line": "sleep_timeout = 0",
            "fix": "sleep_timeout = 300",
            "wrong_fixes": ["sleep_timeout = -1",
                            "sleep_timeout = 999999",
                            "sleep_timeout = None"],
            "difficulty": 3,
        },
        {
            "symptom": "Keyboard types the wrong symbols.",
            "detail": "Quotes and @ are swapped everywhere.",
            "bug_line": "keyboard_layout = 'uk'",
            "fix": "keyboard_layout = 'us'",
            "wrong_fixes": ["keyboard_layout = 'dvorak'",
                            "keyboard_layout = None",
                            "keyboard_layout = 'mac'"],
            "difficulty": 2,
        },
    ],
    "virus": [
        {
            "symptom": "Pop-ups appearing everywhere!",
            "detail": "Ads keep opening even when browser is closed.",
            "virus_name": "AdBlaster",
            "difficulty": 1,
        },
        {
            "symptom": "My files are all encrypted!",
            "detail": "Demanding payment to unlock them.",
            "virus_name": "CryptoLocker",
            "difficulty": 3,
        },
        {
            "symptom": "Computer is mining cryptocurrency by itself!",
            "detail": "CPU fan running full speed, very slow.",
            "virus_name": "CoinMiner",
            "difficulty": 2,
        },
        {
            "symptom": "Someone is controlling my mouse!",
            "detail": "Cursor moves on its own and clicks things.",
            "virus_name": "RemoteRat",
            "difficulty": 4,
        },
        {
            "symptom": "Desktop wallpaper keeps changing to skulls.",
            "detail": "And there's a creepy laughing sound.",
            "virus_name": "SkullFace",
            "difficulty": 2,
        },
        {
            "symptom": "All my passwords were changed!",
            "detail": "Can't log into any accounts.",
            "virus_name": "PassThief",
            "difficulty": 5,
        },
        {
            "symptom": "Computer sends emails by itself!",
            "detail": "My contacts say I'm spamming them.",
            "virus_name": "SpamBot",
            "difficulty": 3,
        },
        {
            "symptom": "Fake antivirus keeps asking for payment.",
            "detail": "Won't let me close the scary warning screen.",
            "virus_name": "ScareWare",
            "difficulty": 1,
        },
        {
            "symptom": "Browser homepage keeps changing!",
            "detail": "Resets to a sketchy search site every reboot.",
            "virus_name": "HijackSearch",
            "difficulty": 2,
        },
        {
            "symptom": "Antivirus was uninstalled by itself!",
            "detail": "Security icon vanished from the tray.",
            "virus_name": "DefenderKill",
            "difficulty": 4,
        },
        {
            "symptom": "Files keep duplicating with weird extensions.",
            "detail": ".locked copies appear on the desktop.",
            "virus_name": "DupWorm",
            "difficulty": 3,
        },
        {
            "symptom": "Webcam light is on when I'm not using it!",
            "detail": "Privacy slider is closed but LED stays lit.",
            "virus_name": "SpyCam",
            "difficulty": 4,
        },
        {
            "symptom": "Downloads folder full of unknown .exe files.",
            "detail": "Icons look like PDFs but are programs.",
            "virus_name": "TrojanDrop",
            "difficulty": 3,
        },
        {
            "symptom": "Network shares spreading junk files.",
            "detail": "Other PCs on LAN getting infected too.",
            "virus_name": "LanWorm",
            "difficulty": 5,
        },
        {
            "symptom": "Browser keeps redirecting my searches.",
            "detail": "Every click lands on a casino page.",
            "virus_name": "RedirBot",
            "difficulty": 2,
        },
        {
            "symptom": "A toolbar I never installed appeared.",
            "detail": "It re-installs itself after removal.",
            "virus_name": "ToolbarPest",
            "difficulty": 1,
        },
        {
            "symptom": "Keystrokes feel laggy and recorded.",
            "detail": "A hidden process logs everything I type.",
            "virus_name": "KeyLogger",
            "difficulty": 4,
        },
        {
            "symptom": "My PC is part of a botnet attack!",
            "detail": "Huge outbound traffic to random IPs.",
            "virus_name": "BotNet",
            "difficulty": 5,
        },
        {
            "symptom": "Boot is hijacked before Windows loads.",
            "detail": "A ransom screen shows at power-on.",
            "virus_name": "BootKit",
            "difficulty": 5,
        },
        {
            "symptom": "Calculator app spawns dozens of copies.",
            "detail": "They multiply until the PC is unusable.",
            "virus_name": "ForkBomb",
            "difficulty": 3,
        },
    ],
    "network": [
        {
            "symptom": "WiFi keeps disconnecting!",
            "detail": "Connected for a minute then drops.",
            "node_count": 4,
            "difficulty": 1,
        },
        {
            "symptom": "Can't connect to the office server.",
            "detail": "Other websites work fine though.",
            "node_count": 5,
            "difficulty": 2,
        },
        {
            "symptom": "Internet speed is incredibly slow!",
            "detail": "Speed test shows 0.5 Mbps on a 100 Mbps plan.",
            "node_count": 5,
            "difficulty": 2,
        },
        {
            "symptom": "VPN won't connect anymore.",
            "detail": "Was working fine yesterday.",
            "node_count": 6,
            "difficulty": 3,
        },
        {
            "symptom": "Can ping but can't browse websites.",
            "detail": "DNS resolution seems to be failing.",
            "node_count": 5,
            "difficulty": 3,
        },
        {
            "symptom": "Network drive won't map!",
            "detail": "Error: 'The network path was not found.'",
            "node_count": 7,
            "difficulty": 4,
        },
        {
            "symptom": "Getting 'IP conflict' error messages.",
            "detail": "Two devices fighting for the same address.",
            "node_count": 6,
            "difficulty": 4,
        },
        {
            "symptom": "Packets are being dropped on internal network.",
            "detail": "Intermittent connectivity between subnets.",
            "node_count": 8,
            "difficulty": 5,
        },
        {
            "symptom": "Guest WiFi can't reach the internet.",
            "detail": "Connects but pages never load.",
            "node_count": 4,
            "difficulty": 2,
        },
        {
            "symptom": "Port forwarding stopped working.",
            "detail": "Game server friends can't join anymore.",
            "node_count": 6,
            "difficulty": 4,
        },
        {
            "symptom": "DHCP isn't handing out IP addresses.",
            "detail": "Devices stuck on 169.254.x.x addresses.",
            "node_count": 5,
            "difficulty": 3,
        },
        {
            "symptom": "Ethernet works but WiFi is dead.",
            "detail": "Cable connection is fine on the same router.",
            "node_count": 5,
            "difficulty": 2,
        },
        {
            "symptom": "VPN connects but no traffic passes.",
            "detail": "Tunnel shows green but ping fails.",
            "node_count": 7,
            "difficulty": 4,
        },
        {
            "symptom": "Intermittent packet loss on fiber line.",
            "detail": "Video calls freeze every few minutes.",
            "node_count": 9,
            "difficulty": 5,
        },
        {
            "symptom": "Printer drops off the network randomly.",
            "detail": "Works after reboot, then vanishes again.",
            "node_count": 5,
            "difficulty": 2,
        },
        {
            "symptom": "Wi-Fi is fast up close but dead in back rooms.",
            "detail": "Signal collapses past one wall.",
            "node_count": 6,
            "difficulty": 3,
        },
        {
            "symptom": "Two offices can't see each other's files.",
            "detail": "The site-to-site link looks misrouted.",
            "node_count": 8,
            "difficulty": 5,
        },
        {
            "symptom": "Video calls lag despite fast download speed.",
            "detail": "Upload is saturated and jitter is high.",
            "node_count": 6,
            "difficulty": 3,
        },
        {
            "symptom": "New laptop won't get on the corporate VLAN.",
            "detail": "Switch port seems on the wrong VLAN.",
            "node_count": 7,
            "difficulty": 4,
        },
        {
            "symptom": "Smart devices keep losing connection.",
            "detail": "IoT subnet drops every evening at peak.",
            "node_count": 6,
            "difficulty": 3,
        },
    ],
}

CATEGORIES = ["hardware", "software", "virus", "network"]
CATEGORY_LABELS = {
    "hardware": "Hardware",
    "software": "Software",
    "virus": "Virus",
    "network": "Network",
}

CATEGORY_ICONS = {
    "hardware": "wrench",
    "software": "monitor",
    "virus": "virus",
    "network": "network",
}
CATEGORY_DESCRIPTIONS = {
    "hardware": "Physical component failure",
    "software": "Configuration or OS issue",
    "virus": "Malware infection",
    "network": "Connectivity problem",
}


class Problem:
    """Represents a customer's computer problem."""

    def __init__(self, category, data):
        self.category = category
        self.symptom = data["symptom"]
        self.detail = data.get("detail", "")
        self.difficulty = data.get("difficulty", 1)
        self.data = data  # full data dict for mini-game use

    def __repr__(self):
        return f"Problem({self.category}, d={self.difficulty}, '{self.symptom[:30]}...')"


class ProblemGenerator:
    """Generates problems appropriate for the current level."""

    def __init__(self):
        self.used_indices = {cat: [] for cat in CATEGORIES}
        self.level = 1

    def _pick_problem(self, level):
        """Pick one problem weighted toward higher difficulty."""
        min_diff, max_diff = get_difficulty_range(level)
        category = random.choice(CATEGORIES)
        pool = PROBLEMS[category]

        available = [
            (i, p) for i, p in enumerate(pool)
            if min_diff <= p["difficulty"] <= max_diff
            and i not in self.used_indices[category]
        ]
        if not available:
            self.used_indices[category].clear()
            available = [
                (i, p) for i, p in enumerate(pool)
                if min_diff <= p["difficulty"] <= max_diff
            ]
        if not available:
            available = list(enumerate(pool))

        weights = [p["difficulty"] ** 2 for _, p in available]
        idx, data = random.choices(available, weights=weights, k=1)[0]
        self.used_indices[category].append(idx)
        return Problem(category, data)

    def generate(self, level, count=1):
        """Generate problems scaled to café level difficulty."""
        self.level = level
        return [self._pick_problem(level) for _ in range(count)]

    def generate_single(self, level):
        """Generate a single problem for the given level."""
        self.level = level
        return self._pick_problem(level)

    def reset(self):
        """Reset used problem tracking."""
        self.used_indices = {cat: [] for cat in CATEGORIES}
