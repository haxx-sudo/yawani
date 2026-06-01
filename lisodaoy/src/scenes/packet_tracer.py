"""
Packet Tracer practice mode — trace routes and fix misconfigured devices.
Inspired by Cisco Packet Tracer topology troubleshooting.
"""
import pygame
import math
import random
from src.constants import *
from src.ui.button import Button
from src.ui.particles import ParticleSystem
from src.ui.icons import IconDrawer
from src.utils.mobile import touch_radius_scale


# Cisco PT–style palette
PT_BG = (12, 28, 48)
PT_GRID = (20, 40, 65)
PT_PC = (90, 95, 105)
PT_SWITCH = (0, 160, 200)
PT_ROUTER = (60, 140, 80)
PT_LINK = (0, 200, 120)
PT_LINK_BAD = (255, 80, 60)
PT_PANEL = (18, 32, 55)

# Per device-type icon + accent color used when drawing nodes
PT_DEVICE_STYLE = {
    "pc":       {"icon": "pt_pc",       "color": (150, 170, 200)},
    "switch":   {"icon": "pt_switch",   "color": PT_SWITCH},
    "router":   {"icon": "pt_router",   "color": PT_ROUTER},
    "server":   {"icon": "pt_server",   "color": (90, 110, 150)},
    "cloud":    {"icon": "pt_cloud",    "color": (120, 140, 180)},
    "firewall": {"icon": "pt_firewall", "color": (190, 70, 60)},
    "ap":       {"icon": "pt_ap",       "color": (0, 180, 160)},
}


# Scenarios: trace = click hops in order; fix = pick broken device + correct IP
PT_SCENARIOS = [
    {
        "id": "lab1_trace",
        "title": "Lab 1 — Basic Trace",
        "type": "trace",
        "symptom": "PC-A cannot reach PC-B. Trace the path packets should take.",
        "goal": "Click devices in order: PC-A → SW → R1 → R2 → SW → PC-B",
        "devices": [
            {"type": "pc", "label": "PC-A", "ip": "192.168.1.10/24",
             "x": 90, "y": 400},
            {"type": "switch", "label": "SW-1", "ip": "",
             "x": 240, "y": 400},
            {"type": "router", "label": "R1", "ip": "10.0.0.1/30",
             "x": 400, "y": 400},
            {"type": "router", "label": "R2", "ip": "10.0.0.2/30",
             "x": 560, "y": 400},
            {"type": "switch", "label": "SW-2", "ip": "",
             "x": 720, "y": 400},
            {"type": "pc", "label": "PC-B", "ip": "192.168.2.10/24",
             "x": 870, "y": 400},
        ],
        "links": [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)],
        "difficulty": 1,
    },
    {
        "id": "lab2_fix_gw",
        "title": "Lab 2 — Wrong Default Gateway",
        "type": "fix",
        "symptom": "PC-Client has no internet. Other PCs on the LAN work fine.",
        "goal": "Find the misconfigured device and apply the correct IP.",
        "devices": [
            {"type": "pc", "label": "PC-Client", "ip": "192.168.1.50/24",
             "wrong_ip": "192.168.1.50/24", "x": 200, "y": 380,
             "broken": True},
            {"type": "switch", "label": "SW-1", "ip": "", "x": 400, "y": 380},
            {"type": "router", "label": "R-GW", "ip": "192.168.1.1/24",
             "x": 600, "y": 380},
            {"type": "cloud", "label": "Internet", "ip": "", "x": 800, "y": 380},
        ],
        "links": [(0, 1), (1, 2), (2, 3)],
        "fixes": [
            "192.168.1.50/24  gw 192.168.1.1",
            "192.168.1.50/24  gw 192.168.1.99",
            "10.0.0.50/24  gw 10.0.0.1",
            "192.168.1.50/24  gw 0.0.0.0",
        ],
        "correct_fix": "192.168.1.50/24  gw 192.168.1.1",
        "difficulty": 2,
    },
    {
        "id": "lab3_trace_vlan",
        "title": "Lab 3 — Campus Path",
        "type": "trace",
        "symptom": "Student PC cannot ping the Library server at 172.16.10.5",
        "goal": "Trace: PC → SW → R-Core → R-Edge → SW → Server",
        "devices": [
            {"type": "pc", "label": "PC-Student", "ip": "172.16.1.10/24",
             "x": 80, "y": 420},
            {"type": "switch", "label": "SW-A", "ip": "", "x": 220, "y": 420},
            {"type": "router", "label": "R-Core", "ip": "172.16.0.1/16",
             "x": 380, "y": 360},
            {"type": "router", "label": "R-Edge", "ip": "172.16.10.1/24",
             "x": 540, "y": 420},
            {"type": "switch", "label": "SW-B", "ip": "", "x": 700, "y": 420},
            {"type": "pc", "label": "Server", "ip": "172.16.10.5/24",
             "x": 860, "y": 420},
        ],
        "links": [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)],
        "difficulty": 3,
    },
    {
        "id": "lab4_fix_subnet",
        "title": "Lab 4 — Subnet Mask Error",
        "type": "fix",
        "symptom": "PC-2 cannot communicate with PC-1 on the same switch.",
        "goal": "Fix the device with the incorrect subnet mask.",
        "devices": [
            {"type": "pc", "label": "PC-1", "ip": "10.10.10.1/24",
             "x": 250, "y": 400},
            {"type": "pc", "label": "PC-2", "ip": "10.10.10.2/16",
             "wrong_ip": "10.10.10.2/16", "x": 450, "y": 400, "broken": True},
            {"type": "switch", "label": "SW-LAN", "ip": "", "x": 350, "y": 320},
            {"type": "router", "label": "R1", "ip": "10.10.10.254/24",
             "x": 650, "y": 400},
        ],
        "links": [(0, 2), (1, 2), (2, 3)],
        "fixes": [
            "10.10.10.2/24",
            "10.10.10.2/16",
            "10.10.10.2/8",
            "10.10.10.2/32",
        ],
        "correct_fix": "10.10.10.2/24",
        "difficulty": 3,
    },
    {
        "id": "lab5_trace_wan",
        "title": "Lab 5 — WAN Trace",
        "type": "trace",
        "symptom": "Branch office PC cannot reach HQ web server.",
        "goal": "Trace full WAN path through both routers.",
        "devices": [
            {"type": "pc", "label": "PC-Branch", "ip": "10.1.1.10/24",
             "x": 70, "y": 410},
            {"type": "switch", "label": "SW", "ip": "", "x": 200, "y": 410},
            {"type": "router", "label": "R-Branch", "ip": "10.1.1.1/24",
             "x": 340, "y": 410},
            {"type": "router", "label": "R-ISP", "ip": "203.0.113.1/30",
             "x": 500, "y": 350},
            {"type": "router", "label": "R-HQ", "ip": "10.2.2.1/24",
             "x": 660, "y": 410},
            {"type": "switch", "label": "SW-HQ", "ip": "", "x": 790, "y": 410},
            {"type": "pc", "label": "Web-Server", "ip": "10.2.2.50/24",
             "x": 920, "y": 410},
        ],
        "links": [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6)],
        "difficulty": 4,
    },
    {
        "id": "lab6_fix_dup",
        "title": "Lab 6 — Duplicate IP",
        "type": "fix",
        "symptom": "Intermittent ARP conflicts on VLAN 10 — one host has a duplicate.",
        "goal": "Select the PC using the duplicate address and fix it.",
        "devices": [
            {"type": "pc", "label": "PC-A", "ip": "10.0.10.5/24",
             "x": 200, "y": 380},
            {"type": "pc", "label": "PC-B", "ip": "10.0.10.5/24",
             "wrong_ip": "10.0.10.5/24", "x": 400, "y": 380, "broken": True},
            {"type": "switch", "label": "SW", "ip": "", "x": 300, "y": 300},
            {"type": "router", "label": "R-GW", "ip": "10.0.10.1/24",
             "x": 600, "y": 380},
        ],
        "links": [(0, 2), (1, 2), (2, 3)],
        "fixes": [
            "10.0.10.6/24",
            "10.0.10.5/24",
            "10.0.10.5/16",
            "10.0.10.255/24",
        ],
        "correct_fix": "10.0.10.6/24",
        "difficulty": 5,
    },
    {
        "id": "lab7_trace_dmz",
        "title": "Lab 7 — DMZ Web Access",
        "type": "trace",
        "symptom": "External users cannot reach the public web server in the DMZ.",
        "goal": "Trace: Internet → Firewall → R-Edge → SW → Web-Server",
        "devices": [
            {"type": "cloud", "label": "Internet", "ip": "", "x": 90, "y": 410},
            {"type": "firewall", "label": "FW-1", "ip": "203.0.113.2/30",
             "x": 260, "y": 410},
            {"type": "router", "label": "R-Edge", "ip": "10.5.0.1/24",
             "x": 430, "y": 410},
            {"type": "switch", "label": "SW-DMZ", "ip": "", "x": 600, "y": 410},
            {"type": "server", "label": "Web-Server", "ip": "10.5.0.80/24",
             "x": 770, "y": 410},
        ],
        "links": [(0, 1), (1, 2), (2, 3), (3, 4)],
        "difficulty": 4,
    },
    {
        "id": "lab8_fix_dns",
        "title": "Lab 8 — Wrong DNS Server",
        "type": "fix",
        "symptom": "PCs can ping by IP but cannot resolve any hostnames.",
        "goal": "Fix the host pointing at the wrong DNS address.",
        "devices": [
            {"type": "pc", "label": "PC-1", "ip": "192.168.5.10/24",
             "wrong_ip": "dns 8.8.4.0", "x": 200, "y": 380, "broken": True},
            {"type": "switch", "label": "SW", "ip": "", "x": 380, "y": 380},
            {"type": "router", "label": "R-GW", "ip": "192.168.5.1/24",
             "x": 560, "y": 380},
            {"type": "server", "label": "DNS", "ip": "192.168.5.53/24",
             "x": 740, "y": 380},
        ],
        "links": [(0, 1), (1, 2), (2, 3)],
        "fixes": [
            "dns 192.168.5.53",
            "dns 8.8.4.0",
            "dns 192.168.5.1",
            "dns 255.255.255.0",
        ],
        "correct_fix": "dns 192.168.5.53",
        "difficulty": 4,
    },
    {
        "id": "lab9_trace_wifi",
        "title": "Lab 9 — Wireless Client",
        "type": "trace",
        "symptom": "Laptop on Wi-Fi cannot reach the file server.",
        "goal": "Trace: Laptop → AP → SW → R-Core → Server",
        "devices": [
            {"type": "pc", "label": "Laptop", "ip": "192.168.20.40/24",
             "x": 80, "y": 420},
            {"type": "ap", "label": "AP-1", "ip": "192.168.20.2/24",
             "x": 240, "y": 420},
            {"type": "switch", "label": "SW", "ip": "", "x": 410, "y": 420},
            {"type": "router", "label": "R-Core", "ip": "192.168.20.1/24",
             "x": 580, "y": 360},
            {"type": "server", "label": "File-Srv", "ip": "192.168.20.50/24",
             "x": 760, "y": 420},
        ],
        "links": [(0, 1), (1, 2), (2, 3), (3, 4)],
        "difficulty": 5,
    },
    {
        "id": "lab10_fix_wan_link",
        "title": "Lab 10 — WAN Link Subnet",
        "type": "fix",
        "symptom": "The point-to-point WAN link between R1 and R2 stays down.",
        "goal": "Correct the WAN interface that is on the wrong subnet.",
        "devices": [
            {"type": "router", "label": "R1", "ip": "10.0.0.1/30",
             "x": 250, "y": 380},
            {"type": "router", "label": "R2", "ip": "10.0.1.2/30",
             "wrong_ip": "10.0.1.2/30", "x": 550, "y": 380, "broken": True},
            {"type": "cloud", "label": "WAN", "ip": "", "x": 400, "y": 300},
        ],
        "links": [(0, 2), (1, 2)],
        "fixes": [
            "10.0.0.2/30",
            "10.0.1.2/30",
            "10.0.0.2/24",
            "10.0.0.5/30",
        ],
        "correct_fix": "10.0.0.2/30",
        "difficulty": 5,
    },
    {
        "id": "lab11_trace_redundant",
        "title": "Lab 11 — Redundant Core",
        "type": "trace",
        "symptom": "Failover path: branch must reach datacenter via the backup core.",
        "goal": "Trace: PC → SW → R-Acc → R-Core → FW → Server",
        "devices": [
            {"type": "pc", "label": "PC", "ip": "172.20.1.10/24",
             "x": 70, "y": 430},
            {"type": "switch", "label": "SW", "ip": "", "x": 200, "y": 430},
            {"type": "router", "label": "R-Acc", "ip": "172.20.1.1/24",
             "x": 350, "y": 430},
            {"type": "router", "label": "R-Core", "ip": "172.20.0.1/16",
             "x": 510, "y": 360},
            {"type": "firewall", "label": "FW", "ip": "172.20.0.2/16",
             "x": 670, "y": 430},
            {"type": "server", "label": "DC-Srv", "ip": "172.20.99.5/24",
             "x": 840, "y": 430},
        ],
        "links": [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)],
        "difficulty": 5,
    },
    {
        "id": "lab12_fix_gw_subnet",
        "title": "Lab 12 — Gateway Out of Subnet",
        "type": "fix",
        "symptom": "PC has an IP but its gateway is unreachable — wrong subnet.",
        "goal": "Set a gateway that lives inside the PC's own subnet.",
        "devices": [
            {"type": "pc", "label": "PC-X", "ip": "192.168.8.20/24",
             "wrong_ip": "gw 192.168.9.1", "x": 220, "y": 380,
             "broken": True},
            {"type": "switch", "label": "SW", "ip": "", "x": 420, "y": 380},
            {"type": "router", "label": "R-GW", "ip": "192.168.8.1/24",
             "x": 620, "y": 380},
            {"type": "cloud", "label": "Internet", "ip": "", "x": 810, "y": 380},
        ],
        "links": [(0, 1), (1, 2), (2, 3)],
        "fixes": [
            "gw 192.168.8.1",
            "gw 192.168.9.1",
            "gw 192.168.8.255",
            "gw 10.0.0.1",
        ],
        "correct_fix": "gw 192.168.8.1",
        "difficulty": 5,
    },
    {
        "id": "lab13_trace_voip",
        "title": "Lab 13 — VoIP Call Path",
        "type": "trace",
        "symptom": "An IP phone can register but calls to HQ have no audio.",
        "goal": "Trace: Phone → SW → R-Branch → R-HQ → SW → Call-Server",
        "devices": [
            {"type": "pc", "label": "IP-Phone", "ip": "10.3.1.20/24",
             "x": 70, "y": 420},
            {"type": "switch", "label": "SW-V", "ip": "", "x": 200, "y": 420},
            {"type": "router", "label": "R-Branch", "ip": "10.3.1.1/24",
             "x": 350, "y": 420},
            {"type": "router", "label": "R-HQ", "ip": "10.9.0.1/24",
             "x": 520, "y": 360},
            {"type": "switch", "label": "SW-HQ", "ip": "", "x": 690, "y": 420},
            {"type": "server", "label": "Call-Srv", "ip": "10.9.0.40/24",
             "x": 860, "y": 420},
        ],
        "links": [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)],
        "difficulty": 5,
    },
    {
        "id": "lab14_fix_vlan",
        "title": "Lab 14 — Wrong VLAN Address",
        "type": "fix",
        "symptom": "A PC moved to VLAN 30 still has a VLAN 20 address.",
        "goal": "Re-address the host into the VLAN 30 subnet.",
        "devices": [
            {"type": "pc", "label": "PC-30", "ip": "192.168.20.15/24",
             "wrong_ip": "192.168.20.15/24", "x": 220, "y": 380,
             "broken": True},
            {"type": "switch", "label": "SW", "ip": "", "x": 420, "y": 380},
            {"type": "router", "label": "R-L3", "ip": "192.168.30.1/24",
             "x": 620, "y": 380},
            {"type": "server", "label": "App", "ip": "192.168.30.90/24",
             "x": 800, "y": 380},
        ],
        "links": [(0, 1), (1, 2), (2, 3)],
        "fixes": [
            "192.168.30.15/24",
            "192.168.20.15/24",
            "192.168.30.15/16",
            "192.168.130.15/24",
        ],
        "correct_fix": "192.168.30.15/24",
        "difficulty": 5,
    },
    {
        "id": "lab15_trace_double_nat",
        "title": "Lab 15 — Double NAT Path",
        "type": "trace",
        "symptom": "Home lab behind two routers can't reach a cloud API.",
        "goal": "Trace: PC → SW → R-Home → R-ISP → Firewall → Internet",
        "devices": [
            {"type": "pc", "label": "PC", "ip": "192.168.0.10/24",
             "x": 70, "y": 430},
            {"type": "switch", "label": "SW", "ip": "", "x": 200, "y": 430},
            {"type": "router", "label": "R-Home", "ip": "192.168.0.1/24",
             "x": 350, "y": 430},
            {"type": "router", "label": "R-ISP", "ip": "100.64.0.1/24",
             "x": 510, "y": 360},
            {"type": "firewall", "label": "FW", "ip": "203.0.113.1/30",
             "x": 680, "y": 430},
            {"type": "cloud", "label": "Internet", "ip": "", "x": 860, "y": 430},
        ],
        "links": [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)],
        "difficulty": 5,
    },
    {
        "id": "lab16_fix_loopback",
        "title": "Lab 16 — Router ID Clash",
        "type": "fix",
        "symptom": "OSPF won't form an adjacency — two routers share a Router-ID.",
        "goal": "Give the broken router a unique loopback address.",
        "devices": [
            {"type": "router", "label": "R1", "ip": "1.1.1.1/32",
             "x": 250, "y": 380},
            {"type": "router", "label": "R2", "ip": "1.1.1.1/32",
             "wrong_ip": "1.1.1.1/32", "x": 550, "y": 380, "broken": True},
            {"type": "cloud", "label": "Area 0", "ip": "", "x": 400, "y": 300},
        ],
        "links": [(0, 2), (1, 2)],
        "fixes": [
            "2.2.2.2/32",
            "1.1.1.1/32",
            "1.1.1.2/24",
            "255.255.255.255/32",
        ],
        "correct_fix": "2.2.2.2/32",
        "difficulty": 5,
    },
]


class PacketTracerScene:
    """Standalone Packet Tracer training mode."""

    def __init__(self, game):
        self.game = game
        self.particles = ParticleSystem()
        self.scenario_idx = 0
        self.score = 0
        self.completed = False
        self.success = False
        self.result_timer = 0
        self.time_remaining = 0
        self.max_time = 0

        self._state = {}
        self._fix_buttons = []
        self._back_button = None
        self._packets = []
        self._vignette = None

        # Session stats (persist across labs until a fresh run)
        self.attempts = 0
        self.correct = 0
        self.labs_completed = 0
        self.session_over = False
        self.session_failed = False
        self._summary_buttons = []

    def enter(self, scenario_idx=0, **kwargs):
        self.scenario_idx = scenario_idx % len(PT_SCENARIOS)
        self.completed = False
        self.success = False
        self.result_timer = 0
        self._fix_buttons = []
        self._packets = []
        self.particles.clear()

        # Start of a brand-new practice run → reset cumulative stats
        if self.scenario_idx == 0:
            self.score = 0
            self.attempts = 0
            self.correct = 0
            self.labs_completed = 0
            self.session_over = False
            self.session_failed = False
            self._summary_buttons = []

        self._load_scenario()

        self._back_button = Button(
            12, SCREEN_HEIGHT - 56, 120, 44, "MENU",
            font_name="small", accent_color=COLOR_CYAN,
            callback=self._exit_to_menu,
        )

    def _exit_to_menu(self):
        self.game.change_scene(SCENE_MENU)

    def _load_scenario(self):
        sc = PT_SCENARIOS[self.scenario_idx]
        diff = sc.get("difficulty", 1)
        self.max_time = max(25.0, 55.0 - diff * 4)
        self.time_remaining = self.max_time

        devices = []
        for i, d in enumerate(sc["devices"]):
            devices.append({
                **d,
                "idx": i,
                "active": False,
                "highlighted": False,
                "selected": False,
            })

        self._state = {
            "scenario": sc,
            "devices": devices,
            "links": list(sc.get("links", [])),
            "current_idx": 0,
            "connections": [],
            "wrong_flash": 0,
            "phase": "play",
            "selected_device": None,
            "show_fix_panel": False,
        }

        if sc["type"] == "fix":
            self._build_fix_buttons(sc)

    def _build_fix_buttons(self, sc):
        self._fix_buttons = []
        fixes = list(sc["fixes"])
        random.shuffle(fixes)
        btn_w = 420
        btn_h = 40
        start_y = 200
        for i, fix in enumerate(fixes):
            btn = Button(
                SCREEN_WIDTH // 2 - btn_w // 2,
                start_y + i * (btn_h + 8),
                btn_w, btn_h,
                fix,
                font_name="terminal",
                accent_color=COLOR_CYAN,
            )
            btn._fix_value = fix
            self._fix_buttons.append(btn)

    def _device_at(self, pos):
        hit_r = 42 * touch_radius_scale()
        for dev in self._state["devices"]:
            dx = pos[0] - dev["x"]
            dy = pos[1] - dev["y"]
            if dx * dx + dy * dy <= hit_r * hit_r:
                return dev
        return None

    def _emit_packet(self, x1, y1, x2, y2):
        self._packets.append({
            "x": float(x1), "y": float(y1),
            "tx": float(x2), "ty": float(y2),
            "t": 0.0,
            "duration": 0.45,
        })

    def _handle_trace_click(self, dev):
        st = self._state
        self.attempts += 1
        if dev["idx"] == st["current_idx"]:
            self.correct += 1
            dev["active"] = True
            if st["current_idx"] > 0:
                prev = st["devices"][st["current_idx"] - 1]
                st["connections"].append((st["current_idx"] - 1, st["current_idx"]))
                self._emit_packet(prev["x"], prev["y"], dev["x"], dev["y"])
            st["current_idx"] += 1
            self.game.sounds.play("click")
            self.particles.emit_sparkles(dev["x"], dev["y"], PT_LINK, 12)
            if st["current_idx"] >= len(st["devices"]):
                self._scenario_complete()
        else:
            st["wrong_flash"] = 0.4
            self.time_remaining -= 2.0
            self.game.sounds.play("error")

    def _handle_fix_click(self, dev):
        st = self._state
        sc = st["scenario"]
        for d in st["devices"]:
            d["selected"] = False
        dev["selected"] = True
        st["selected_device"] = dev

        self.attempts += 1
        if dev.get("broken"):
            self.correct += 1
            st["show_fix_panel"] = True
            self.game.sounds.play("click")
        else:
            st["wrong_flash"] = 0.35
            self.time_remaining -= 1.5
            self.game.sounds.play("error")

    def _apply_fix(self, fix_value):
        sc = self._state["scenario"]
        self.attempts += 1
        if fix_value == sc["correct_fix"]:
            self.correct += 1
            dev = self._state["selected_device"]
            if dev:
                first = sc["correct_fix"].split()[0]
                # Replace the shown address only when the fix is itself an IP/subnet;
                # config fixes (dns/gw ...) keep the device's existing address.
                if first[:1].isdigit():
                    dev["ip"] = first
                dev["active"] = True
                dev["broken"] = False
            self._state["show_fix_panel"] = False
            self.game.sounds.play("click")
            self._scenario_complete()
        else:
            self._state["wrong_flash"] = 0.4
            self.time_remaining -= 2.5
            self.game.sounds.play("error")

    def _scenario_complete(self):
        self.success = True
        self.completed = True
        self.result_timer = 2.0
        diff = self._state["scenario"].get("difficulty", 1)
        self.score += 100 + diff * 50
        self.labs_completed += 1
        self.particles.emit_sparkles(SCREEN_WIDTH // 2, 300, COLOR_GREEN, 25)
        self.game.sounds.play_success()

    def _scenario_fail(self):
        self.success = False
        self.completed = True
        self.result_timer = 2.0
        self.game.sounds.play("error")

    def accuracy(self):
        if self.attempts <= 0:
            return 100.0
        return 100.0 * self.correct / self.attempts

    def _begin_session_over(self, failed):
        """Show the end-of-run summary with score + accuracy."""
        self.session_over = True
        self.session_failed = failed
        self.completed = False
        if self.score > self.game.high_score:
            self.game.high_score = self.score
        self._build_summary_buttons()

    def _build_summary_buttons(self):
        cx = SCREEN_WIDTH // 2
        y = SCREEN_HEIGHT // 2 + 120
        self._summary_buttons = [
            Button(cx - 230, y, 210, 56, "TRY AGAIN",
                   font_name="heading", accent_color=COLOR_GREEN,
                   icon_type="play", icon_size=16,
                   callback=lambda: self.enter(scenario_idx=0)),
            Button(cx + 20, y, 210, 56, "MENU",
                   font_name="heading", accent_color=COLOR_CYAN,
                   icon_type="home", icon_size=16,
                   callback=self._exit_to_menu),
        ]

    def handle_event(self, event):
        if self.session_over:
            for btn in self._summary_buttons:
                btn.handle_event(event)
            return

        if self._back_button:
            self._back_button.handle_event(event)

        if self.completed:
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self._advance_or_exit()
            return

        st = self._state
        if st.get("show_fix_panel"):
            for btn in self._fix_buttons:
                if btn.handle_event(event):
                    self._apply_fix(btn._fix_value)
                    return
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            dev = self._device_at(event.pos)
            if dev:
                sc = st["scenario"]
                if sc["type"] == "trace":
                    self._handle_trace_click(dev)
                else:
                    self._handle_fix_click(dev)

    def _advance_or_exit(self):
        if self.success and self.scenario_idx < len(PT_SCENARIOS) - 1:
            self.enter(scenario_idx=self.scenario_idx + 1)
        else:
            # Final lab cleared, or ran out of time → end-of-run summary
            self._begin_session_over(failed=not self.success)

    def update(self, dt):
        self.particles.update(dt)

        if self.session_over:
            for btn in self._summary_buttons:
                btn.update(dt)
            return

        if self._back_button:
            self._back_button.update(dt)

        for btn in self._fix_buttons:
            btn.update(dt)

        if self.completed:
            self.result_timer -= dt
            return

        self.time_remaining -= dt
        if self.time_remaining <= 0:
            self._scenario_fail()
            return

        st = self._state
        if st["wrong_flash"] > 0:
            st["wrong_flash"] -= dt

        sc = st["scenario"]
        if sc["type"] == "trace":
            for i, dev in enumerate(st["devices"]):
                dev["highlighted"] = (i == st["current_idx"])

        # Animate packets along links
        alive = []
        for pkt in self._packets:
            pkt["t"] += dt
            if pkt["t"] < pkt["duration"]:
                alive.append(pkt)
        self._packets = alive

    # -------------------------------------------------------------------------
    # Drawing
    # -------------------------------------------------------------------------
    def _draw_grid(self, screen):
        screen.fill(PT_BG)
        # Brighter minor grid + accented major grid lines
        for gx in range(0, SCREEN_WIDTH, 40):
            col = (28, 52, 80) if gx % 160 == 0 else PT_GRID
            pygame.draw.line(screen, col, (gx, 0), (gx, SCREEN_HEIGHT))
        for gy in range(0, SCREEN_HEIGHT, 40):
            col = (28, 52, 80) if gy % 160 == 0 else PT_GRID
            pygame.draw.line(screen, col, (0, gy), (SCREEN_WIDTH, gy))
        screen.blit(self._bg_vignette(), (0, 0))

    def _bg_vignette(self):
        if self._vignette is None:
            v = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            steps = 50
            for i in range(steps):
                a = int(90 * (i / steps) ** 2)
                inset = int((steps - i) * 9)
                pygame.draw.rect(v, (0, 0, 0, a),
                                 (inset, inset,
                                  SCREEN_WIDTH - inset * 2,
                                  SCREEN_HEIGHT - inset * 2),
                                 border_radius=140, width=10)
            self._vignette = v
        return self._vignette

    def _draw_device(self, screen, assets, dev):
        dtype = dev["type"]
        x, y = dev["x"], dev["y"]
        w, h = 78, 70
        timer = pygame.time.get_ticks() / 1000.0

        style = PT_DEVICE_STYLE.get(dtype, PT_DEVICE_STYLE["pc"])
        icon_color = style["color"]

        rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
        active = dev.get("active")
        flagged = dev.get("highlighted") or dev.get("selected")
        border = PT_LINK if active else (
            COLOR_AMBER if flagged else (50, 70, 95))
        if dev.get("broken") and dev.get("selected"):
            border = PT_LINK_BAD

        # Selection / active glow halo
        if active or flagged:
            halo = pygame.Surface((w + 24, h + 24), pygame.SRCALPHA)
            glow = (*border[:3], 60)
            pygame.draw.rect(halo, glow, halo.get_rect(), border_radius=12)
            screen.blit(halo, (rect.x - 12, rect.y - 12))

        # Node card
        pygame.draw.rect(screen, PT_PANEL, rect, border_radius=8)
        pygame.draw.rect(screen, border, rect, border_radius=8, width=2)

        # Icon
        IconDrawer.draw(screen, style["icon"], x, y - 12, 17, icon_color,
                        timer=timer)

        # Status LED (top-right of card)
        led = PT_LINK if active else (
            PT_LINK_BAD if dev.get("broken") and not active else (70, 90, 115))
        pygame.draw.circle(screen, led, (rect.right - 8, rect.top + 8), 3)

        font = assets.get_font("tiny")
        name = font.render(dev["label"], True,
                           COLOR_WHITE if not flagged else COLOR_AMBER_GLOW)
        screen.blit(name, name.get_rect(center=(x, y + 12)))
        if dev.get("ip"):
            broken_now = dev.get("broken") and not active
            ip_text = dev.get("wrong_ip", dev["ip"]) if broken_now else dev["ip"]
            ip_color = PT_LINK_BAD if broken_now else COLOR_CYAN_GLOW
            ip_surf = font.render(ip_text, True, ip_color)
            screen.blit(ip_surf, ip_surf.get_rect(center=(x, y + 26)))

        if dev.get("highlighted"):
            pulse = int(4 + 3 * math.sin(pygame.time.get_ticks() / 200))
            pygame.draw.rect(screen, COLOR_AMBER,
                             rect.inflate(pulse, pulse), border_radius=10, width=2)

    def _draw_summary(self, screen, assets):
        """End-of-run game-over panel with score & accuracy."""
        total = len(PT_SCENARIOS)
        acc = self.accuracy()
        all_clear = self.labs_completed >= total

        # Dim backdrop
        dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim.fill((4, 12, 22, 220))
        screen.blit(dim, (0, 0))

        # Panel
        pw, ph = 560, 420
        panel = pygame.Rect(SCREEN_WIDTH // 2 - pw // 2,
                            SCREEN_HEIGHT // 2 - ph // 2 - 10, pw, ph)
        assets.draw_panel(screen, panel, color=PT_PANEL,
                          border_color=PT_SWITCH, alpha=245)

        cx = panel.centerx
        if all_clear:
            heading, hcolor = "ALL LABS COMPLETE!", COLOR_GREEN
        elif self.session_failed:
            heading, hcolor = "SESSION OVER", COLOR_RED
        else:
            heading, hcolor = "PRACTICE COMPLETE", COLOR_CYAN
        assets.draw_text_shadow(screen, heading, "title",
                                cx, panel.y + 50, hcolor, center=True)

        # Accuracy grade
        if acc >= 90:
            grade, gcolor = "A", COLOR_GREEN
        elif acc >= 75:
            grade, gcolor = "B", COLOR_CYAN
        elif acc >= 60:
            grade, gcolor = "C", COLOR_AMBER
        else:
            grade, gcolor = "D", COLOR_RED
        assets.draw_text_shadow(screen, f"Grade  {grade}", "heading",
                                cx, panel.y + 108, gcolor, center=True)

        # Stat rows
        rows = [
            ("Score", f"{self.score}", COLOR_AMBER),
            ("Labs Cleared", f"{self.labs_completed} / {total}", COLOR_CREAM),
            ("Accuracy", f"{acc:.0f}%  ({self.correct}/{self.attempts})",
             gcolor),
            ("Best Score", f"{self.game.high_score}", COLOR_AMBER_GLOW),
        ]
        ry = panel.y + 158
        for label, value, vcolor in rows:
            row = pygame.Rect(panel.x + 40, ry, pw - 80, 40)
            pygame.draw.rect(screen, (12, 26, 44), row, border_radius=6)
            pygame.draw.rect(screen, (30, 60, 90), row, border_radius=6, width=1)
            assets.draw_text_shadow(screen, label, "small",
                                    row.x + 16, row.centery - 9,
                                    COLOR_TEXT_DIM, center=False)
            vs = assets.get_font("hud").render(value, True, vcolor)
            screen.blit(vs, vs.get_rect(midright=(row.right - 16,
                                                  row.centery)))
            ry += 48

        for btn in self._summary_buttons:
            btn.draw(screen, assets)

    def draw(self, screen):
        self._draw_grid(screen)
        assets = self.game.assets

        if self.session_over:
            self._draw_summary(screen, assets)
            return

        st = self._state
        sc = st["scenario"]

        # Top toolbar (PT-style)
        toolbar = pygame.Rect(0, 0, SCREEN_WIDTH, 52)
        pygame.draw.rect(screen, (8, 18, 32), toolbar)
        pygame.draw.line(screen, PT_SWITCH, (0, 51), (SCREEN_WIDTH, 51), 2)
        assets.draw_text_shadow(screen, "Cisco Packet Tracer — Practice Mode",
                                "body", 16, 18, COLOR_CYAN, center=False)
        lab_s = assets.get_font("small").render(
            f"Lab {self.scenario_idx + 1}/{len(PT_SCENARIOS)}", True, COLOR_TEXT_DIM)
        screen.blit(lab_s, (SCREEN_WIDTH - lab_s.get_width() - 12, 14))
        score_s = assets.get_font("small").render(
            f"Score: {self.score}", True, COLOR_AMBER)
        screen.blit(score_s, (SCREEN_WIDTH - score_s.get_width() - 12, 32))

        # Timer bar
        progress = max(0, self.time_remaining / max(0.01, self.max_time))
        assets.draw_progress_bar(screen, SCREEN_WIDTH // 2 - 100, 58,
                                 200, 8, progress,
                                 COLOR_GREEN if progress > 0.3 else COLOR_RED)

        # Scenario panel
        panel = pygame.Rect(16, 72, SCREEN_WIDTH - 32, 88)
        pygame.draw.rect(screen, PT_PANEL, panel, border_radius=8)
        pygame.draw.rect(screen, PT_SWITCH, panel, border_radius=8, width=1)
        assets.draw_text_shadow(screen, sc["title"], "body",
                                panel.x + 12, panel.y + 10, COLOR_AMBER)
        assets.draw_text_shadow(screen, sc["symptom"], "small",
                                panel.x + 12, panel.y + 36, COLOR_CREAM)
        assets.draw_text_shadow(screen, sc["goal"], "tiny",
                                panel.x + 12, panel.y + 58, COLOR_TEXT_DIM)

        # Inactive links (dashed-ish faint cabling)
        for a, b in st["links"]:
            n1, n2 = st["devices"][a], st["devices"][b]
            done = (a, b) in st["connections"] or (b, a) in st["connections"]
            if not done:
                pygame.draw.line(screen, (40, 60, 85),
                                 (n1["x"], n1["y"]), (n2["x"], n2["y"]), 2)

        # Active links with neon glow
        glow_layer = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT),
                                    pygame.SRCALPHA)
        for a, b in st["connections"]:
            n1, n2 = st["devices"][a], st["devices"][b]
            p1, p2 = (n1["x"], n1["y"]), (n2["x"], n2["y"])
            pygame.draw.line(glow_layer, (*PT_LINK, 60), p1, p2, 12)
            pygame.draw.line(glow_layer, (*PT_LINK, 110), p1, p2, 6)
        screen.blit(glow_layer, (0, 0))
        for a, b in st["connections"]:
            n1, n2 = st["devices"][a], st["devices"][b]
            pygame.draw.line(screen, PT_LINK, (n1["x"], n1["y"]),
                             (n2["x"], n2["y"]), 3)
            pygame.draw.line(screen, (210, 255, 235), (n1["x"], n1["y"]),
                             (n2["x"], n2["y"]), 1)

        # Animated packets with comet trail
        for pkt in self._packets:
            t = min(1.0, pkt["t"] / pkt["duration"])
            px = pkt["x"] + (pkt["tx"] - pkt["x"]) * t
            py = pkt["y"] + (pkt["ty"] - pkt["y"]) * t
            for tr in range(5):
                tt = max(0.0, t - tr * 0.05)
                trx = pkt["x"] + (pkt["tx"] - pkt["x"]) * tt
                try_ = pkt["y"] + (pkt["ty"] - pkt["y"]) * tt
                a = int(120 * (1 - tr / 5))
                trail = pygame.Surface((16, 16), pygame.SRCALPHA)
                pygame.draw.circle(trail, (*COLOR_AMBER, a), (8, 8),
                                   6 - tr)
                screen.blit(trail, (int(trx) - 8, int(try_) - 8))
            pygame.draw.circle(screen, COLOR_AMBER, (int(px), int(py)), 6)
            pygame.draw.circle(screen, COLOR_WHITE, (int(px), int(py)), 3)

        # Devices
        for dev in st["devices"]:
            self._draw_device(screen, assets, dev)

        # Fix panel overlay
        if st.get("show_fix_panel"):
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            assets.draw_text_shadow(screen, "Select correct configuration:",
                                    "heading", SCREEN_WIDTH // 2, 155,
                                    COLOR_CYAN, center=True)
            for btn in self._fix_buttons:
                btn.draw(screen, assets)

        # Trace progress
        if sc["type"] == "trace" and not self.completed:
            total = len(st["devices"])
            done = st["current_idx"]
            assets.draw_text_shadow(
                screen, f"Hop {done}/{total} — click next device in path",
                "small", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 72,
                COLOR_TEXT_DIM, center=True)

        if st["wrong_flash"] > 0:
            flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            flash.fill((255, 0, 0, int(50 * st["wrong_flash"] / 0.4)))
            screen.blit(flash, (0, 0))

        self.particles.draw(screen, assets)
        self._back_button.draw(screen, assets)

        if self.completed:
            dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 180))
            screen.blit(dim, (0, 0))
            msg = "LAB COMPLETE!" if self.success else "TIME'S UP!"
            color = COLOR_GREEN if self.success else COLOR_RED
            assets.draw_text_shadow(screen, msg, "title",
                                    SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30,
                                    color, center=True)
            if self.success and self.scenario_idx < len(PT_SCENARIOS) - 1:
                hint = "Click for next lab..."
            else:
                hint = "Click for results..."
            assets.draw_text_shadow(screen, hint, "body",
                                    SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30,
                                    COLOR_TEXT_DIM, center=True)
