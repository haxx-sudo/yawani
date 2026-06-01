"""
Game constants, colors, and configuration values.
"""

# =============================================================================
# Screen & Display
# =============================================================================
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
TITLE = "Tech Support Café"

# =============================================================================
# Color Palette — Warm café tones + neon tech accents
# =============================================================================

# Café backgrounds
COLOR_BG = (25, 18, 12)
COLOR_BG_LIGHT = (45, 32, 22)
COLOR_WALL = (65, 45, 30)
COLOR_WALL_LIGHT = (85, 60, 40)

# Wood tones
COLOR_WOOD_DARK = (75, 48, 28)
COLOR_WOOD = (120, 78, 42)
COLOR_WOOD_LIGHT = (165, 115, 65)
COLOR_WOOD_PALE = (200, 155, 100)

# Neutrals
COLOR_CREAM = (255, 242, 220)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GRAY = (120, 120, 120)
COLOR_GRAY_DARK = (60, 60, 60)
COLOR_GRAY_LIGHT = (180, 180, 180)

# Warm accents
COLOR_AMBER = (255, 185, 50)
COLOR_AMBER_DARK = (200, 135, 30)
COLOR_AMBER_GLOW = (255, 210, 100)
COLOR_ORANGE = (255, 140, 40)
COLOR_YELLOW = (255, 230, 50)

# Tech accents
COLOR_CYAN = (0, 220, 255)
COLOR_CYAN_DARK = (0, 140, 180)
COLOR_CYAN_GLOW = (100, 240, 255)
COLOR_MAGENTA = (255, 50, 200)
COLOR_GREEN = (0, 255, 100)
COLOR_GREEN_DARK = (0, 180, 70)
COLOR_GREEN_DIM = (0, 120, 50)
COLOR_RED = (255, 60, 60)
COLOR_RED_DARK = (180, 40, 40)
COLOR_BLUE = (60, 120, 255)
COLOR_PURPLE = (160, 80, 255)

# UI Panel colors
COLOR_PANEL = (40, 28, 20)
COLOR_PANEL_BORDER = (90, 65, 40)
COLOR_PANEL_LIGHT = (55, 40, 28)
COLOR_PANEL_HOVER = (70, 50, 35)
COLOR_TEXT = (255, 242, 220)
COLOR_TEXT_DIM = (160, 140, 120)
COLOR_TEXT_BRIGHT = (255, 255, 240)
COLOR_SHADOW = (15, 10, 5, 150)

# Category colors
CATEGORY_COLORS = {
    "hardware": COLOR_ORANGE,
    "software": COLOR_CYAN,
    "virus": COLOR_RED,
    "network": COLOR_GREEN,
}

# =============================================================================
# Customer appearance
# =============================================================================
CUSTOMER_BODY_COLORS = [
    (200, 85, 85),    # Muted red
    (85, 160, 200),   # Muted blue
    (85, 190, 110),   # Muted green
    (210, 170, 80),   # Muted yellow
    (160, 100, 200),  # Muted purple
    (200, 120, 160),  # Muted pink
    (100, 195, 180),  # Muted teal
    (210, 145, 85),   # Muted orange
]

SKIN_COLORS = [
    (255, 224, 189),
    (241, 194, 150),
    (224, 172, 125),
    (198, 143, 97),
    (162, 113, 76),
    (130, 90, 60),
]

HAIR_COLORS = [
    (40, 30, 20),     # Dark brown
    (80, 55, 30),     # Brown
    (180, 140, 60),   # Blonde
    (150, 50, 30),    # Auburn
    (20, 20, 20),     # Black
    (180, 180, 180),  # Gray
    (200, 80, 60),    # Red
]

# =============================================================================
# Game Balance
# =============================================================================
STARTING_MONEY = 0
STARTING_REPUTATION = 50
MAX_REPUTATION = 100
MIN_REPUTATION = 0
BASE_PATIENCE = 18.0           # seconds before customer leaves
PATIENCE_PER_LEVEL_REDUCE = 0.8  # seconds less per level
MIN_PATIENCE = 8.0
BASE_REWARD = 50               # base money per fix
BONUS_PER_DIFFICULTY = 20      # extra $ per difficulty level
REPUTATION_GAIN = 5            # rep for successful fix
REPUTATION_LOSS = 8            # rep loss for customer leaving angry
WRONG_DIAGNOSIS_PENALTY = 3.0  # seconds lost for wrong diagnosis
MAX_PROBLEM_DIFFICULTY = 5

# Customers per level (index = level - 1)
CUSTOMERS_PER_LEVEL = [
    3, 4, 4, 5, 5, 6, 6, 7, 8, 9,
    10, 11, 12, 13, 15,
]
# Spawn interval per level in seconds (lower = busier café)
SPAWN_INTERVALS = [
    6.0, 5.5, 5.0, 4.5, 4.0, 3.8, 3.5, 3.2, 3.0, 2.8,
    2.6, 2.4, 2.2, 2.0, 1.8,
]
MAX_LEVEL = 15

# Level time limit in seconds (None = no limit). Rush from level 6+.
LEVEL_TIME_LIMITS = [
    None, None, None, None, None,
    200, 185, 170, 160, 150,
    140, 130, 120, 110, 100,
]

# Extra seconds removed from mini-games per café level
MINIGAME_LEVEL_TIME_PENALTY = 0.35

LEVEL_NAMES = {
    1: "Opening Shift",
    2: "Morning Rush",
    3: "Coffee & Cables",
    4: "Ticket Queue",
    5: "Power Users",
    6: "Lunch Rush",
    7: "Patch Tuesday",
    8: "Malware Monday",
    9: "Network Nightmare",
    10: "VIP Support",
    11: "Server Room",
    12: "Zero-Day Panic",
    13: "Datacenter Drama",
    14: "CEO's Laptop",
    15: "Grand Finale",
}


def get_level_customers(level):
    idx = min(max(1, level) - 1, len(CUSTOMERS_PER_LEVEL) - 1)
    return CUSTOMERS_PER_LEVEL[idx]


def get_level_spawn_interval(level):
    idx = min(max(1, level) - 1, len(SPAWN_INTERVALS) - 1)
    return SPAWN_INTERVALS[idx]


def get_level_time_limit(level):
    idx = min(max(1, level) - 1, len(LEVEL_TIME_LIMITS) - 1)
    return LEVEL_TIME_LIMITS[idx]


def get_difficulty_range(level):
    """Min/max problem difficulty (1–5) for this café level."""
    level = max(1, level)
    max_diff = min(MAX_PROBLEM_DIFFICULTY, 1 + (level + 1) // 2)
    min_diff = 1
    if level >= 5:
        min_diff = 2
    if level >= 9:
        min_diff = 3
    if level >= 13:
        min_diff = 4
    min_diff = min(min_diff, max_diff)
    return min_diff, max_diff


def get_level_display_name(level):
    return LEVEL_NAMES.get(level, f"Level {level}")

# =============================================================================
# Workstation Layout
# =============================================================================
MAX_WORKSTATIONS = 5
DEFAULT_WORKSTATIONS = 3
WORKSTATION_Y = 420
WORKSTATION_SPACING = 200
WORKSTATION_WIDTH = 160
WORKSTATION_HEIGHT = 120

# =============================================================================
# Mini-game Settings
# =============================================================================
MINIGAME_BASE_TIME = 12.0      # seconds for mini-game at difficulty 1
MINIGAME_TIME_PER_DIFF = 1.5   # less time per difficulty level

# Hardware mini-game
HARDWARE_COMPONENTS = [
    {"name": "RAM Stick", "color": COLOR_GREEN},
    {"name": "Graphics Card", "color": COLOR_RED},
    {"name": "CPU Chip", "color": COLOR_CYAN},
    {"name": "SSD Drive", "color": COLOR_BLUE},
    {"name": "Power Supply", "color": COLOR_YELLOW},
    {"name": "Cooling Fan", "color": COLOR_GRAY_LIGHT},
]

# Software mini-game options per problem
SOFTWARE_FIX_COUNT = 4  # number of options shown

# Virus mini-game
VIRUS_SPAWN_RATE = 1.2  # seconds between spawns (base)
VIRUS_TARGET_KILLS = 8  # viruses to kill at difficulty 1
VIRUS_EXTRA_PER_DIFF = 3
VIRUS_EXTRA_PER_LEVEL = 1  # more kills required at higher café levels

# Network mini-game
NETWORK_BASE_NODES = 4
NETWORK_EXTRA_PER_DIFF = 1

# =============================================================================
# Upgrade Definitions
# =============================================================================
UPGRADES = {
    "workstation": {
        "name": "Extra Workstation",
        "description": "Add another repair station",
        "icon": "workstation",
        "costs": [200, 400],  # cost for 4th, 5th station
        "max_level": 2,
    },
    "tools": {
        "name": "Better Tools",
        "description": "+3s mini-game time",
        "icon": "wrench",
        "costs": [100, 200, 350],
        "max_level": 3,
    },
    "coffee": {
        "name": "Coffee Machine",
        "description": "+3s customer patience",
        "icon": "coffee",
        "costs": [150, 300, 500],
        "max_level": 3,
    },
    "diagnostic": {
        "name": "Diagnostic Scanner",
        "description": "Highlights correct diagnosis",
        "icon": "scanner",
        "costs": [250],
        "max_level": 1,
    },
    "reputation": {
        "name": "Yelp Boost",
        "description": "+10 reputation",
        "icon": "star",
        "costs": [100, 150, 200, 300],
        "max_level": 4,
    },
}

# =============================================================================
# Scene Names
# =============================================================================
SCENE_MENU = "menu"
SCENE_CAFE = "cafe"
SCENE_REPAIR = "repair"
SCENE_UPGRADE = "upgrade"
SCENE_GAMEOVER = "gameover"
SCENE_PACKET_TRACER = "packet_tracer"
