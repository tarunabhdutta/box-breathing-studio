"""
Box Breathing Studio  -  Immersive desktop breathwork
Developed by Tarunabh Dutta

A full-screen guided pranayama / breathwork experience built in pygame.
Higgsfield-generated ambient art per technique, smooth animated breathing
orb, particle effects, sine-wave audio cues, and a Smart Wizard that
picks the right routine for how you actually feel right now.

Techniques included
-------------------
  Box Breathing (Sama Vritti)        4-4-4-4
  4-7-8 (Weil)                       4-7-8-0
  Bhramari (Humming Bee)             4-0-8-0 with hum tone
  Nadi Shodhana (alt-nostril guide)  4-4-4-4 with left/right cues
  Extended Exhale                    4-0-6-0
  15-minute Daily Sequence           five blocks chained
  Smart Wizard                       3-question check-in
  Custom Builder                     any 4-phase ratio
"""

from __future__ import annotations

import math
import os
import random
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import numpy as np
import pygame

# =====================================================================
# CONSTANTS  /  IDENTITY
# =====================================================================

DEVELOPER  = "Tarunabh Dutta"
APP_NAME   = "Box Breathing Studio"
VERSION    = "2.0"
COPYRIGHT  = "© 2026 Tarunabh Dutta · TD Film Studio, Guwahati"

ROOT       = Path(__file__).parent
ASSETS     = ROOT / "assets"

# Colors (RGB)
BG            = (13, 27, 42)
PANEL         = (27, 38, 59)
PANEL_HOVER   = (42, 58, 85)
ACCENT        = (127, 219, 218)
ACCENT_BRIGHT = (166, 232, 231)
ACCENT_DIM    = (58, 138, 137)
TEXT          = (224, 230, 237)
TEXT_DIM      = (141, 153, 174)
INHALE_COL    = (127, 219, 218)   # cyan
HOLD_IN_COL   = (244, 211, 94)    # gold
EXHALE_COL    = (239, 131, 84)    # coral
HOLD_OUT_COL  = (157, 141, 241)   # lavender
WARN          = (239, 131, 84)
SUCCESS       = (158, 232, 154)

# Audio
SAMPLE_RATE = 44100

# =====================================================================
# AUDIO  -  generated sine cues via pygame mixer
# =====================================================================

PHASE_TONES = {
    "inhale":   (220.0, 0.40),
    "hold_in":  (330.0, 0.25),
    "exhale":   (165.0, 0.50),
    "hold_out": (110.0, 0.25),
    "complete": (440.0, 0.70),
    "click":    (660.0, 0.06),
}

class Audio:
    def __init__(self):
        self.volume = 0.8
        self.voice_volume = 1.0
        self.voice_on = True
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.voices: dict[str, pygame.mixer.Sound] = {}
        self._voice_channel: pygame.mixer.Channel | None = None
        self.hum: pygame.mixer.Sound | None = None
        self._build()
        self._load_voices()

    @staticmethod
    def _to_sound(pcm_mono: np.ndarray) -> pygame.mixer.Sound:
        """Wrap a mono int16 PCM buffer into a pygame Sound, matching the
        mixer's actual channel count (mono or stereo)."""
        channels = pygame.mixer.get_init()[2] if pygame.mixer.get_init() else 2
        if channels == 2:
            buf = np.column_stack([pcm_mono, pcm_mono])
        else:
            buf = pcm_mono
        buf = np.ascontiguousarray(buf)
        return pygame.sndarray.make_sound(buf)

    def _tone(self, freq: float, duration: float, gain: float = 0.30) -> pygame.mixer.Sound:
        n = int(SAMPLE_RATE * duration)
        t = np.linspace(0.0, duration, n, endpoint=False)
        wave = np.sin(2.0 * np.pi * freq * t)
        fade = max(64, int(SAMPLE_RATE * 0.04))
        env = np.ones(n)
        env[:fade] = np.linspace(0, 1, fade)
        env[-fade:] = np.linspace(1, 0, fade)
        pcm = (wave * env * gain * 32767).astype(np.int16)
        return self._to_sound(pcm)

    def _hum(self, duration: float, gain: float = 0.22) -> pygame.mixer.Sound:
        n = int(SAMPLE_RATE * duration)
        t = np.linspace(0.0, duration, n, endpoint=False)
        f = 130.0
        wave = (np.sin(2 * np.pi * f * t) * 0.6
                + np.sin(2 * np.pi * f * 2 * t) * 0.25
                + np.sin(2 * np.pi * f * 3 * t) * 0.10)
        fade = int(SAMPLE_RATE * 0.18)
        env = np.ones(n)
        env[:fade] = np.linspace(0, 1, fade)
        env[-fade:] = np.linspace(1, 0, fade)
        pcm = (wave * env * gain * 32767).astype(np.int16)
        return self._to_sound(pcm)

    def _build(self):
        for name, (f, d) in PHASE_TONES.items():
            self.sounds[name] = self._tone(f, d)

    def _load_voices(self):
        voice_dir = ROOT / "assets" / "voice"
        if not voice_dir.exists():
            return
        # Reserve a dedicated channel for voice so a new cue interrupts the
        # previous one (avoids overlapping narration).
        if pygame.mixer.get_init():
            try:
                pygame.mixer.set_num_channels(max(8, pygame.mixer.get_num_channels()))
                self._voice_channel = pygame.mixer.Channel(7)
            except Exception:
                self._voice_channel = None
        for p in voice_dir.glob("*.mp3"):
            try:
                self.voices[p.stem] = pygame.mixer.Sound(str(p))
            except pygame.error:
                pass

    def play(self, name: str):
        snd = self.sounds.get(name)
        if snd is None:
            return
        snd.set_volume(self.volume * 0.55)  # quieter so voice sits on top
        snd.play()

    def play_voice(self, key: str):
        if not self.voice_on or not key:
            return
        snd = self.voices.get(key)
        if snd is None:
            return
        snd.set_volume(self.voice_volume * self.volume)
        if self._voice_channel is not None:
            self._voice_channel.stop()
            self._voice_channel.play(snd)
        else:
            snd.play()

    def play_hum(self, duration: float):
        if duration <= 0.05:
            return
        s = self._hum(min(duration, 12.0))
        s.set_volume(self.volume * 0.9)
        s.play()

    def set_volume(self, v: float):
        self.volume = max(0.0, min(1.0, v))

    def toggle_voice(self):
        self.voice_on = not self.voice_on
        return self.voice_on


# =====================================================================
# ROUTINES
# =====================================================================

@dataclass
class Phase:
    name: str            # "inhale" | "hold_in" | "exhale" | "hold_out"
    seconds: int
    label: str
    hum: bool = False
    voice: str | None = None   # voice clip key in assets/voice/<key>.mp3

@dataclass
class Block:
    title: str
    subtitle: str
    cycles: int
    phases: list[Phase]
    note: str = ""
    bg_key: str = "bg_box"   # asset background to use for this block

@dataclass
class Routine:
    title: str
    description: str
    blocks: list[Block] = field(default_factory=list)
    bg_key: str = "bg_home"

def _phases(ratio, cues=None, hum=False, voice_keys=None):
    """Build a 4-phase block. ``voice_keys`` overrides the default voice clip
    per phase (e.g. {'inhale': 'inhale_left', 'exhale': 'exhale_right'})."""
    inh, hin, exh, hout = ratio
    cues = cues or {}
    vk = voice_keys or {}
    out = []
    if inh > 0:
        out.append(Phase("inhale", inh, cues.get("inhale", "Inhale"),
                         voice=vk.get("inhale", "inhale")))
    if hin > 0:
        out.append(Phase("hold_in", hin, cues.get("hold_in", "Hold"),
                         voice=vk.get("hold_in", "hold")))
    if exh > 0:
        out.append(Phase("exhale", exh, cues.get("exhale", "Exhale"),
                         hum=hum,
                         voice=vk.get("exhale", "hum" if hum else "exhale")))
    if hout > 0:
        out.append(Phase("hold_out", hout, cues.get("hold_out", "Hold empty"),
                         voice=vk.get("hold_out", "hold_empty")))
    return out

def routine_box(level: str = "intermediate") -> Routine:
    n = {"beginner": 3, "intermediate": 4, "advanced": 6}[level]
    return Routine(
        title=f"Box Breathing — {level.title()}",
        description=f"Sama Vritti  ·  {n}-{n}-{n}-{n}  ·  equal four-sided breath",
        bg_key="bg_box",
        blocks=[Block("Box Breathing", "Sama Vritti", 10, _phases((n, n, n, n)),
                      note="Sit upright. Chin mudra. Nasal breath only.",
                      bg_key="bg_box")],
    )

def routine_478() -> Routine:
    return Routine(
        title="4-7-8 Breathing",
        description="Dr Weil's calming breath  ·  long exhale = vagal brake",
        bg_key="bg_478",
        blocks=[Block("4-7-8", "Sleep & panic-reset", 8, _phases((4, 7, 8, 0)),
                      note="Exhale through pursed lips with a soft 'whoosh'.",
                      bg_key="bg_478")],
    )

def routine_bhramari() -> Routine:
    return Routine(
        title="Bhramari Pranayama",
        description="Humming Bee Breath  ·  vibration soothes the brain",
        bg_key="bg_bhramari",
        blocks=[Block("Bhramari", "Hum on every exhale", 7, _phases((4, 0, 8, 0), hum=True),
                      note="Close ears with index fingers. Hum 'mmm' through full exhale.",
                      bg_key="bg_bhramari")],
    )

def routine_nadi() -> Routine:
    left  = {"inhale": "Inhale LEFT", "hold_in": "Hold",
             "exhale": "Exhale RIGHT", "hold_out": "Hold"}
    right = {"inhale": "Inhale RIGHT", "hold_in": "Hold",
             "exhale": "Exhale LEFT", "hold_out": "Hold"}
    vleft = {"inhale": "inhale_left", "hold_in": "hold",
             "exhale": "exhale_right", "hold_out": "hold_empty"}
    vright = {"inhale": "inhale_right", "hold_in": "hold",
              "exhale": "exhale_left", "hold_out": "hold_empty"}
    return Routine(
        title="Nadi Shodhana",
        description="Alternate-nostril breathing  ·  Vishnu Mudra",
        bg_key="bg_nadi",
        blocks=[
            Block("Left → Right", "Round A", 5,
                  _phases((4, 4, 4, 4), cues=left, voice_keys=vleft),
                  note="Right thumb closes right nostril. Inhale left, exhale right.",
                  bg_key="bg_nadi"),
            Block("Right → Left", "Round B", 5,
                  _phases((4, 4, 4, 4), cues=right, voice_keys=vright),
                  note="Ring + pinky close left nostril. Inhale right, exhale left.",
                  bg_key="bg_nadi"),
        ],
    )


def routine_nadi_box() -> Routine:
    """Classical Nadi Shodhana, box-style.  One full cycle alternates sides:
    inhale LEFT (4) - hold (4) - exhale RIGHT (4) - hold (4)
                    - inhale RIGHT (4) - hold (4) - exhale LEFT (4) - hold (4)
    32 seconds per cycle, repeated 7 times = ~3:45 minutes."""
    phases = [
        Phase("inhale",   4, "Inhale LEFT",  voice="inhale_left"),
        Phase("hold_in",  4, "Hold",         voice="hold"),
        Phase("exhale",   4, "Exhale RIGHT", voice="exhale_right"),
        Phase("hold_out", 4, "Hold empty",   voice="hold_empty"),
        Phase("inhale",   4, "Inhale RIGHT", voice="inhale_right"),
        Phase("hold_in",  4, "Hold",         voice="hold"),
        Phase("exhale",   4, "Exhale LEFT",  voice="exhale_left"),
        Phase("hold_out", 4, "Hold empty",   voice="hold_empty"),
    ]
    return Routine(
        title="Nadi Shodhana Box",
        description="Classical alternation  ·  4-4-4-4 holds on every side",
        bg_key="bg_nadi",
        blocks=[Block("Full alternation", "8-phase cycle", 7, phases,
                      note="Vishnu Mudra. Switch nostrils on every breath. "
                           "One cycle takes both sides through inhale and exhale.",
                      bg_key="bg_nadi")],
    )

def routine_extended_exhale() -> Routine:
    return Routine(
        title="Extended Exhale 4:6",
        description="Inhale 4, exhale 6  ·  pure parasympathetic",
        bg_key="bg_extended",
        blocks=[Block("Extended Exhale", "4 in / 6 out", 12, _phases((4, 0, 6, 0)),
                      note="No retention. Long smooth exhale through the nose.",
                      bg_key="bg_extended")],
    )

def routine_daily_15() -> Routine:
    return Routine(
        title="15-Minute Daily Sequence",
        description="Warm-up → Box → Nadi Shodhana → Bhramari → Integration",
        bg_key="bg_home",
        blocks=[
            Block("Warm-up", "Diaphragmatic breathing", 8, _phases((4, 0, 4, 0)),
                  note="Lying or seated. One hand on belly.",
                  bg_key="bg_extended"),
            Block("Box Breathing", "Sama Vritti core", 10, _phases((4, 4, 4, 4)),
                  note="Spine long. Chin mudra.",
                  bg_key="bg_box"),
            Block("Nadi Shodhana", "Alt-nostril (left start)", 5,
                  _phases((4, 4, 4, 4),
                          cues={"inhale": "Inhale LEFT", "hold_in": "Hold",
                                "exhale": "Exhale RIGHT", "hold_out": "Hold"}),
                  note="Inhale left, exhale right.",
                  bg_key="bg_nadi"),
            Block("Bhramari", "Humming Bee Breath", 5,
                  _phases((4, 0, 8, 0), hum=True),
                  note="Hum on every exhale.",
                  bg_key="bg_bhramari"),
            Block("Integration", "Natural breath awareness", 6, _phases((4, 0, 6, 0)),
                  note="Eyes closed. Let the breath find its own rhythm.",
                  bg_key="bg_extended"),
        ],
    )

def routine_custom(inh, hin, exh, hout, cycles) -> Routine:
    return Routine(
        title=f"Custom — {inh}-{hin}-{exh}-{hout}",
        description=f"Your own ratio  ·  {cycles} cycles",
        bg_key="bg_home",
        blocks=[Block("Custom Breath", "Your ratio", cycles,
                      _phases((inh, hin, exh, hout)),
                      bg_key="bg_box")],
    )

def pick_routine(stress: int, hours_sat: int, sleep: str, hour: int) -> Routine:
    if sleep == "poor" or (hour >= 21 and stress >= 3):
        r = Routine(title="Sleep Reset",
                    description="Wind down: Extended Exhale → 4-7-8 → Bhramari",
                    bg_key="bg_478",
                    blocks=(routine_extended_exhale().blocks
                          + routine_478().blocks
                          + routine_bhramari().blocks))
        return r
    if stress >= 4:
        return Routine(title="Acute Stress Reset",
                       description="Box + Nadi Shodhana for nervous-system reset",
                       bg_key="bg_nadi",
                       blocks=routine_box("intermediate").blocks + routine_nadi().blocks)
    if hours_sat >= 10:
        return Routine(title="Long-Sitting Reset",
                       description="For 10h+ at the desk: Box → Extended Exhale → Bhramari",
                       bg_key="bg_box",
                       blocks=(routine_box("intermediate").blocks
                             + routine_extended_exhale().blocks
                             + routine_bhramari().blocks))
    if hour < 11:
        return Routine(title="Morning Box",
                       description="Energising start: Box, 10 cycles",
                       bg_key="bg_box",
                       blocks=routine_box("intermediate").blocks)
    return routine_daily_15()


# =====================================================================
# RENDER HELPERS
# =====================================================================

def lerp(a, b, t):  return a + (b - a) * t
def ease_in_out(t): return 0.5 - 0.5 * math.cos(math.pi * t)
def ease_out(t):    return 1 - (1 - t) ** 3

def make_glow(radius: int, color, inner_alpha: int = 200) -> pygame.Surface:
    """A soft circular glow as an alpha-channel surface."""
    size = radius * 2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    steps = max(40, radius)
    for i in range(steps, 0, -1):
        r = int(radius * (i / steps))
        a = int(inner_alpha * (1 - i / steps) ** 2)
        pygame.draw.circle(surf, (*color, a), (radius, radius), r)
    return surf

def darken(surf: pygame.Surface, amount: int) -> pygame.Surface:
    """Returns surf with a dark overlay for legibility."""
    out = surf.copy()
    veil = pygame.Surface(out.get_size(), pygame.SRCALPHA)
    veil.fill((0, 0, 0, amount))
    out.blit(veil, (0, 0))
    return out

def draw_text(surf, text, font, color, pos, anchor="center", shadow=True):
    img = font.render(text, True, color)
    rect = img.get_rect(**{anchor: pos})
    if shadow:
        sh = font.render(text, True, (0, 0, 0))
        sh.set_alpha(140)
        surf.blit(sh, rect.move(2, 2))
    surf.blit(img, rect)
    return rect

def draw_panel(surf, rect, fill=PANEL, border=ACCENT_DIM, radius=18, border_w=1, alpha=210):
    s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(s, (*fill, alpha), s.get_rect(), border_radius=radius)
    if border_w:
        pygame.draw.rect(s, (*border, 255), s.get_rect(), border_w, border_radius=radius)
    surf.blit(s, rect.topleft)


# =====================================================================
# ASSETS
# =====================================================================

class Assets:
    def __init__(self, screen_size):
        self.bgs: dict[str, pygame.Surface] = {}
        self.bg_dim: dict[str, pygame.Surface] = {}
        self.icon: pygame.Surface | None = None
        self._load(screen_size)
        self._fonts(screen_size)

    def _load(self, size):
        keys = ["bg_home", "bg_box", "bg_478", "bg_bhramari", "bg_nadi",
                "bg_extended", "bg_complete"]
        for k in keys:
            p = ASSETS / f"{k}.png"
            if p.exists():
                img = pygame.image.load(str(p)).convert()
                img = pygame.transform.smoothscale(img, size)
                self.bgs[k] = img
                self.bg_dim[k] = darken(img, 110)
        p = ASSETS / "icon.png"
        if p.exists():
            self.icon = pygame.image.load(str(p)).convert_alpha()

    def _fonts(self, size):
        w, h = size
        # 1080p is the reference; clamp so very small or very large displays
        # don't get unreadable extremes.
        scale = max(0.7, min(1.4, h / 1080.0))
        def f(sz, bold=False):
            return pygame.font.SysFont("Segoe UI,Arial", max(10, int(sz * scale)), bold=bold)
        self.f_huge   = f(56, True)
        self.f_xl     = f(40, True)
        self.f_lg     = f(28, True)
        self.f_md     = f(20)
        self.f_md_b   = f(20, True)
        self.f_sm     = f(15)
        self.f_sm_b   = f(15, True)
        self.f_count  = f(72, True)
        self.f_phase  = f(26, True)
        self.f_xs     = f(12)


# =====================================================================
# WIDGETS
# =====================================================================

class Button:
    def __init__(self, rect, label, on_click, *, font=None, primary=False, icon=None):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.on_click = on_click
        self.font = font
        self.primary = primary
        self.icon = icon
        self.hover = False

    def handle(self, e):
        if e.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(e.pos)
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.rect.collidepoint(e.pos):
                self.on_click()
                return True
        return False

    def draw(self, surf, audio: Audio | None = None):
        if self.primary:
            base = ACCENT_BRIGHT if self.hover else ACCENT
            fg = BG
            border = ACCENT_BRIGHT
        else:
            base = PANEL_HOVER if self.hover else PANEL
            fg = TEXT
            border = ACCENT_DIM if not self.hover else ACCENT
        s = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(s, (*base, 235), s.get_rect(), border_radius=14)
        pygame.draw.rect(s, (*border, 255), s.get_rect(), 2, border_radius=14)
        surf.blit(s, self.rect.topleft)
        font = self.font
        img = font.render(self.label, True, fg)
        surf.blit(img, img.get_rect(center=self.rect.center))


class Tile:
    """Big home-screen tile with title + subtitle. Optional background image."""
    def __init__(self, rect, title, subtitle, on_click, bg_image=None, accent=ACCENT):
        self.rect = pygame.Rect(rect)
        self.title = title
        self.subtitle = subtitle
        self.on_click = on_click
        self.bg = bg_image
        self.accent = accent
        self.hover = False
        self._hover_t = 0.0

    def handle(self, e):
        if e.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(e.pos)
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.rect.collidepoint(e.pos):
                self.on_click()
                return True
        return False

    def update(self, dt):
        target = 1.0 if self.hover else 0.0
        self._hover_t = lerp(self._hover_t, target, min(1, dt * 8))

    def draw(self, surf, assets: Assets):
        s = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        if self.bg is not None:
            scaled = pygame.transform.smoothscale(self.bg, self.rect.size)
            s.blit(scaled, (0, 0))
            veil = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            veil.fill((BG[0], BG[1], BG[2], int(180 - 60 * self._hover_t)))
            s.blit(veil, (0, 0))
        else:
            pygame.draw.rect(s, (*PANEL, 235), s.get_rect(), border_radius=18)
        # rounded clip
        mask = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=18)
        s.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        # border
        glow_c = (*self.accent, int(120 + 120 * self._hover_t))
        pygame.draw.rect(s, glow_c, s.get_rect(), int(2 + 2 * self._hover_t), border_radius=18)
        surf.blit(s, self.rect.topleft)
        # text
        x = self.rect.x + 24
        y = self.rect.y + self.rect.h - 78
        title_img = assets.f_md_b.render(self.title, True, TEXT)
        surf.blit(title_img, (x, y))
        sub_img = assets.f_sm.render(self.subtitle, True, TEXT_DIM)
        surf.blit(sub_img, (x, y + 34))


class Slider:
    def __init__(self, rect, vmin, vmax, value, on_change, *, step=1, label_fn=None):
        self.rect = pygame.Rect(rect)
        self.vmin = vmin
        self.vmax = vmax
        self.value = value
        self.on_change = on_change
        self.step = step
        self.label_fn = label_fn or str
        self.dragging = False

    def _val_from_x(self, x):
        t = (x - self.rect.x) / max(1, self.rect.w)
        t = max(0.0, min(1.0, t))
        raw = self.vmin + t * (self.vmax - self.vmin)
        if self.step >= 1:
            return int(round(raw / self.step) * self.step)
        return raw

    def handle(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.rect.collidepoint(e.pos):
                self.dragging = True
                self.value = self._val_from_x(e.pos[0])
                self.on_change(self.value)
                return True
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            self.dragging = False
        elif e.type == pygame.MOUSEMOTION and self.dragging:
            self.value = self._val_from_x(e.pos[0])
            self.on_change(self.value)
            return True
        return False

    def draw(self, surf, font):
        track = pygame.Rect(self.rect.x, self.rect.y + self.rect.h // 2 - 3,
                            self.rect.w, 6)
        pygame.draw.rect(surf, PANEL, track, border_radius=3)
        t = (self.value - self.vmin) / max(0.001, (self.vmax - self.vmin))
        fill = track.copy(); fill.w = int(track.w * t)
        pygame.draw.rect(surf, ACCENT, fill, border_radius=3)
        cx = self.rect.x + int(self.rect.w * t)
        cy = self.rect.y + self.rect.h // 2
        pygame.draw.circle(surf, ACCENT_BRIGHT, (cx, cy), 11)
        pygame.draw.circle(surf, BG, (cx, cy), 11, 2)
        lbl = font.render(self.label_fn(self.value), True, ACCENT)
        surf.blit(lbl, lbl.get_rect(midbottom=(self.rect.centerx, self.rect.y - 4)))


class RadioGroup:
    def __init__(self, rect, options, value, on_change, font):
        self.rect = pygame.Rect(rect)
        self.options = options    # list of (value, label)
        self.value = value
        self.on_change = on_change
        self.font = font
        self._make_rects()

    def _make_rects(self):
        n = len(self.options)
        gap = 12
        w = (self.rect.w - gap * (n - 1)) // n
        self._rects = []
        for i in range(n):
            r = pygame.Rect(self.rect.x + i * (w + gap), self.rect.y, w, self.rect.h)
            self._rects.append(r)

    def handle(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for r, (val, _) in zip(self._rects, self.options):
                if r.collidepoint(e.pos):
                    self.value = val
                    self.on_change(val)
                    return True
        return False

    def draw(self, surf):
        for r, (val, label) in zip(self._rects, self.options):
            sel = (val == self.value)
            s = pygame.Surface(r.size, pygame.SRCALPHA)
            fill = ACCENT if sel else PANEL
            fg = BG if sel else TEXT
            pygame.draw.rect(s, (*fill, 235), s.get_rect(), border_radius=10)
            pygame.draw.rect(s, (*ACCENT, 255), s.get_rect(), 2, border_radius=10)
            surf.blit(s, r.topleft)
            img = self.font.render(label, True, fg)
            surf.blit(img, img.get_rect(center=r.center))


# =====================================================================
# SCENES
# =====================================================================

class Scene:
    def __init__(self, app: "App"):
        self.app = app

    def handle(self, e): pass
    def update(self, dt): pass
    def draw(self, surf): pass


# ---------- splash ----------

class SplashScene(Scene):
    def __init__(self, app, duration=2.6):
        super().__init__(app)
        self.t = 0.0
        self.duration = duration

    def update(self, dt):
        self.t += dt
        if self.t >= self.duration:
            self.app.go(HomeScene(self.app))

    def draw(self, surf):
        a = self.app.assets
        w, h = surf.get_size()
        bg = a.bgs.get("bg_home")
        if bg: surf.blit(a.bg_dim["bg_home"], (0, 0))
        else:  surf.fill(BG)

        # icon centered
        if a.icon is not None:
            sz = int(min(w, h) * 0.32)
            ic = pygame.transform.smoothscale(a.icon, (sz, sz))
            alpha = int(255 * min(1.0, self.t / 0.8))
            ic.set_alpha(alpha)
            surf.blit(ic, ic.get_rect(center=(w // 2, h // 2 - 60)))

        # title
        title_a = int(255 * max(0.0, min(1.0, (self.t - 0.5) / 0.8)))
        if title_a > 0:
            img = a.f_huge.render(APP_NAME, True, TEXT)
            img.set_alpha(title_a)
            surf.blit(img, img.get_rect(center=(w // 2, h // 2 + 200)))

        # developer credit
        cred_a = int(255 * max(0.0, min(1.0, (self.t - 1.3) / 0.8)))
        if cred_a > 0:
            img = a.f_md.render(f"Created by  {DEVELOPER}", True, ACCENT)
            img.set_alpha(cred_a)
            surf.blit(img, img.get_rect(center=(w // 2, h // 2 + 260)))


# ---------- home ----------

class HomeScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.tiles: list[Tile] = []
        self.buttons: list[Button] = []
        self.vol_slider: Slider | None = None
        self.drift = 0.0
        self._build()

    def _build(self):
        a = self.app.assets
        w, h = self.app.screen.get_size()
        # 3x3 grid for tiles (9 routines)
        margin_x = int(w * 0.06)
        margin_top = int(h * 0.20)
        margin_bot = int(h * 0.14)
        gap = 18
        cols, rows = 3, 3
        gw = w - margin_x * 2
        gh = h - margin_top - margin_bot
        tw = (gw - gap * (cols - 1)) // cols
        th = (gh - gap * (rows - 1)) // rows

        items = [
            ("Smart Wizard", "3 questions → best routine right now",
             "bg_home", lambda: self.app.go(WizardScene(self.app))),
            ("Box Breathing", "Sama Vritti  ·  4-4-4-4",
             "bg_box", lambda: self.app.go(SessionScene(self.app, routine_box("intermediate")))),
            ("4-7-8", "Sleep & panic-reset",
             "bg_478", lambda: self.app.go(SessionScene(self.app, routine_478()))),
            ("Bhramari", "Humming Bee Breath",
             "bg_bhramari", lambda: self.app.go(SessionScene(self.app, routine_bhramari()))),
            ("Nadi Shodhana", "Alternate-nostril  ·  two-round",
             "bg_nadi", lambda: self.app.go(SessionScene(self.app, routine_nadi()))),
            ("Nadi Shodhana Box", "Classical alternation  ·  4-4-4-4 holds",
             "bg_nadi", lambda: self.app.go(SessionScene(self.app, routine_nadi_box()))),
            ("Extended Exhale", "4 in / 6 out  ·  parasympathetic",
             "bg_extended", lambda: self.app.go(SessionScene(self.app, routine_extended_exhale()))),
            ("15-min Daily", "Full integrated sequence",
             "bg_complete", lambda: self.app.go(SessionScene(self.app, routine_daily_15()))),
            ("Custom Builder", "Roll your own ratio",
             "bg_box", lambda: self.app.go(CustomScene(self.app))),
        ]
        for i, (title, sub, bg_key, cb) in enumerate(items):
            r, c = divmod(i, cols)
            x = margin_x + c * (tw + gap)
            y = margin_top + r * (th + gap)
            self.tiles.append(Tile((x, y, tw, th), title, sub, cb,
                                   bg_image=a.bgs.get(bg_key)))

        # bottom bar
        bar_y = h - margin_bot + 12
        # volume slider — right side
        slider_w = 200
        self.vol_slider = Slider((w - slider_w - 30, bar_y, slider_w, 30),
                                 0, 100, int(self.app.audio.volume * 100),
                                 lambda v: self.app.audio.set_volume(v / 100.0),
                                 step=1, label_fn=lambda v: f"Vol  {int(v)}")
        # voice toggle — to the left of the volume slider
        voice_btn_x = w - slider_w - 30 - 160 - 20
        def _toggle_voice():
            on = self.app.audio.toggle_voice()
            self.btn_voice.label = "Voice  ON" if on else "Voice  OFF"
            self.btn_voice.primary = on
        self.btn_voice = Button(
            (voice_btn_x, bar_y - 6, 160, 42),
            "Voice  ON" if self.app.audio.voice_on else "Voice  OFF",
            _toggle_voice, font=a.f_md, primary=self.app.audio.voice_on)
        self.buttons.append(self.btn_voice)
        # about
        self.buttons.append(Button((30, bar_y - 6, 130, 42), "About",
                                   lambda: self.app.go(AboutScene(self.app)),
                                   font=a.f_md))
        # quit
        self.buttons.append(Button((170, bar_y - 6, 110, 42), "Quit",
                                   self.app.quit, font=a.f_md))

    def handle(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            self.app.quit()
            return
        for t in self.tiles:
            t.handle(e)
        for b in self.buttons:
            b.handle(e)
        if self.vol_slider:
            self.vol_slider.handle(e)

    def update(self, dt):
        self.drift += dt * 0.05
        for t in self.tiles:
            t.update(dt)

    def draw(self, surf):
        a = self.app.assets
        w, h = surf.get_size()
        bg = a.bgs.get("bg_home")
        if bg is not None:
            # subtle horizontal drift
            offset = int(20 * math.sin(self.drift))
            scaled = pygame.transform.smoothscale(bg, (w + 40, h + 40))
            surf.blit(scaled, (-20 + offset, -20))
            veil = pygame.Surface((w, h), pygame.SRCALPHA)
            veil.fill((BG[0], BG[1], BG[2], 140))
            surf.blit(veil, (0, 0))
        else:
            surf.fill(BG)

        # header — measured from font heights so nothing overlaps
        cx = w // 2
        y = int(h * 0.045)
        rect = draw_text(surf, APP_NAME, a.f_xl, TEXT, (cx, y), anchor="midtop")
        y = rect.bottom + int(h * 0.018)
        draw_text(surf, "Sama Vritti  ·  4-7-8  ·  Bhramari  ·  Nadi Shodhana  ·  Extended Exhale",
                  a.f_md, ACCENT, (cx, y), anchor="midtop")

        for t in self.tiles:
            t.draw(surf, a)

        # bottom bar credit + buttons
        draw_text(surf, f"Created by {DEVELOPER}", a.f_sm, TEXT_DIM,
                  (cx, h - int(h * 0.02)))

        for b in self.buttons:
            b.draw(surf)
        if self.vol_slider:
            self.vol_slider.draw(surf, a.f_sm_b)


# ---------- wizard ----------

class WizardScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        a = self.app.assets
        w, h = self.app.screen.get_size()
        self.stress = 3
        self.hours = 8
        self.sleep = "ok"
        cx = w // 2
        panel_w = int(w * 0.62)
        panel_x = (w - panel_w) // 2
        y = int(h * 0.28)

        self.r_stress = RadioGroup((panel_x, y, panel_w, 56),
                                   [(1, "1 calm"), (2, "2"), (3, "3 ok"), (4, "4"), (5, "5 wired")],
                                   3, self._set_stress, a.f_md)
        y += 130
        self.s_hours = Slider((panel_x, y + 30, panel_w, 30),
                              0, 16, 8, self._set_hours, step=1,
                              label_fn=lambda v: f"{int(v)} hours at the desk today")
        y += 130
        self.r_sleep = RadioGroup((panel_x, y, panel_w, 56),
                                  [("poor", "Poor"), ("ok", "OK"), ("good", "Good")],
                                  "ok", self._set_sleep, a.f_md)

        # buttons
        by = h - 140
        self.btn_go   = Button((cx - 200, by, 180, 56), "Pick my routine",
                               self._go, font=a.f_md_b, primary=True)
        self.btn_back = Button((cx + 20,  by, 180, 56), "Back", self._back, font=a.f_md)

    def _set_stress(self, v): self.stress = v
    def _set_hours(self, v):  self.hours = v
    def _set_sleep(self, v):  self.sleep = v

    def _go(self):
        hour = time.localtime().tm_hour
        r = pick_routine(self.stress, self.hours, self.sleep, hour)
        self.app.go(SessionScene(self.app, r))

    def _back(self):
        self.app.go(HomeScene(self.app))

    def handle(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            self._back(); return
        self.r_stress.handle(e)
        self.s_hours.handle(e)
        self.r_sleep.handle(e)
        self.btn_go.handle(e)
        self.btn_back.handle(e)

    def draw(self, surf):
        a = self.app.assets
        w, h = surf.get_size()
        bg = a.bgs.get("bg_home")
        if bg: surf.blit(a.bg_dim["bg_home"], (0, 0))
        else:  surf.fill(BG)

        cx = w // 2
        rect = draw_text(surf, "Smart Wizard", a.f_xl, TEXT,
                         (cx, int(h * 0.045)), anchor="midtop")
        draw_text(surf, "Three quick questions — I'll pick the right routine.",
                  a.f_md, ACCENT, (cx, rect.bottom + int(h * 0.018)), anchor="midtop")

        # question labels
        panel_w = int(w * 0.62)
        panel_x = (w - panel_w) // 2
        y = int(h * 0.28)
        draw_text(surf, "1.  How stressed are you right now?", a.f_md_b, TEXT,
                  (panel_x, y - 36), anchor="topleft")
        self.r_stress.draw(surf)

        y += 130
        draw_text(surf, "2.  Hours sat at the desk today", a.f_md_b, TEXT,
                  (panel_x, y - 36), anchor="topleft")
        self.s_hours.draw(surf, a.f_sm_b)

        y += 130
        draw_text(surf, "3.  Sleep last night", a.f_md_b, TEXT,
                  (panel_x, y - 36), anchor="topleft")
        self.r_sleep.draw(surf)

        self.btn_go.draw(surf)
        self.btn_back.draw(surf)


# ---------- custom builder ----------

class CustomScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        a = self.app.assets
        w, h = self.app.screen.get_size()
        cx = w // 2
        self.vals = {"inh": 4, "hin": 4, "exh": 4, "hout": 4, "cyc": 10}
        panel_w = int(w * 0.62)
        panel_x = (w - panel_w) // 2
        y = int(h * 0.26)
        gap = 90
        self.sliders = []
        labels = [
            ("inh",  "Inhale (sec)",   1, 12),
            ("hin",  "Hold full (sec)", 0, 12),
            ("exh",  "Exhale (sec)",   1, 12),
            ("hout", "Hold empty (sec)", 0, 12),
            ("cyc",  "Cycles",          3, 30),
        ]
        self.label_positions = []
        for i, (key, lab, lo, hi) in enumerate(labels):
            ry = y + i * gap
            self.label_positions.append((lab, panel_x, ry))
            s = Slider((panel_x, ry + 26, panel_w, 30), lo, hi, self.vals[key],
                       lambda v, k=key: self._set(k, v), step=1,
                       label_fn=lambda v: f"{int(v)}")
            self.sliders.append(s)

        by = h - 140
        self.btn_go = Button((cx - 200, by, 180, 56), "Start session",
                             self._go, font=a.f_md_b, primary=True)
        self.btn_back = Button((cx + 20, by, 180, 56), "Back",
                               lambda: self.app.go(HomeScene(self.app)),
                               font=a.f_md)

    def _set(self, k, v): self.vals[k] = v

    def _go(self):
        v = self.vals
        r = routine_custom(v["inh"], v["hin"], v["exh"], v["hout"], v["cyc"])
        self.app.go(SessionScene(self.app, r))

    def handle(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            self.app.go(HomeScene(self.app)); return
        for s in self.sliders: s.handle(e)
        self.btn_go.handle(e)
        self.btn_back.handle(e)

    def draw(self, surf):
        a = self.app.assets
        w, h = surf.get_size()
        bg = a.bgs.get("bg_box")
        if bg: surf.blit(a.bg_dim["bg_box"], (0, 0))
        else:  surf.fill(BG)
        cx = w // 2
        rect = draw_text(surf, "Custom Builder", a.f_xl, TEXT,
                         (cx, int(h * 0.045)), anchor="midtop")
        draw_text(surf, "Roll your own ratio. Holds can be zero.",
                  a.f_md, ACCENT, (cx, rect.bottom + int(h * 0.018)), anchor="midtop")
        for (lab, x, y), s in zip(self.label_positions, self.sliders):
            draw_text(surf, lab, a.f_md_b, TEXT, (x, y), anchor="topleft")
            s.draw(surf, a.f_sm_b)
        self.btn_go.draw(surf)
        self.btn_back.draw(surf)


# ---------- session ----------

@dataclass
class _Particle:
    x: float; y: float
    vx: float; vy: float
    life: float; max_life: float
    size: float
    color: tuple

class SessionScene(Scene):
    def __init__(self, app, routine: Routine):
        super().__init__(app)
        self.routine = routine
        self.block_idx = 0
        self.cycle_idx = 0
        self.phase_idx = 0
        self.t_in_phase = 0.0
        self.running = False
        self.particles: list[_Particle] = []
        self._cue_played = False
        self._hum_played = False
        a = self.app.assets
        w, h = self.app.screen.get_size()

        cx = w // 2
        by = h - int(h * 0.07)
        bw = int(w * 0.14)
        gap = int(w * 0.02)
        self.btn_toggle = Button((cx - bw - gap // 2, by, bw, int(h * 0.045)),
                                 "Start", self.toggle, font=a.f_md_b, primary=True)
        self.btn_back   = Button((cx + gap // 2, by, bw, int(h * 0.045)),
                                 "End session", self._exit, font=a.f_md)
        # pre-render breathing glow — orb sized so it fits between the header
        # and the phase/count text + buttons below.
        self.max_r = int(min(w, h) * 0.16)
        self.min_r = int(min(w, h) * 0.05)
        self._glow_cache: dict[tuple, pygame.Surface] = {}

    @property
    def block(self) -> Block: return self.routine.blocks[self.block_idx]
    @property
    def phase(self) -> Phase: return self.block.phases[self.phase_idx]

    def toggle(self):
        was_running = self.running
        self.running = not self.running
        self.btn_toggle.label = "Pause" if self.running else "Resume"
        if self.running and not was_running:
            # First time we hit Start in this session: play the welcome.
            if (self.block_idx == 0 and self.cycle_idx == 0
                    and self.phase_idx == 0 and self.t_in_phase == 0.0):
                self.app.audio.play_voice("begin")
            if self.t_in_phase == 0.0:
                self._enter_phase()

    def _enter_phase(self):
        self._cue_played = False
        self._hum_played = False

    def _exit(self):
        pygame.mixer.stop()
        self.app.go(HomeScene(self.app))

    def handle(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                self._exit(); return
            if e.key == pygame.K_SPACE:
                self.toggle(); return
        self.btn_toggle.handle(e)
        self.btn_back.handle(e)

    def update(self, dt):
        if not self.running:
            return
        if not self._cue_played:
            self.app.audio.play(self.phase.name)
            self.app.audio.play_voice(self.phase.voice)
            self._cue_played = True
        if (self.phase.name == "exhale" and self.phase.hum
                and not self._hum_played):
            self.app.audio.play_hum(self.phase.seconds)
            self._hum_played = True

        self.t_in_phase += dt
        if self.t_in_phase >= self.phase.seconds:
            self.t_in_phase = 0.0
            self.phase_idx += 1
            if self.phase_idx >= len(self.block.phases):
                self.phase_idx = 0
                self.cycle_idx += 1
                if self.cycle_idx >= self.block.cycles:
                    self.cycle_idx = 0
                    self.block_idx += 1
                    if self.block_idx >= len(self.routine.blocks):
                        self._finish()
                        return
            self._enter_phase()

        # spawn particles
        if random.random() < dt * 8:
            w, h = self.app.screen.get_size()
            cx, cy = w // 2, h // 2 + 20
            r = self._current_radius()
            ang = random.uniform(0, math.tau)
            x = cx + math.cos(ang) * r
            y = cy + math.sin(ang) * r
            if self.phase.name == "inhale":
                vx, vy = (cx - x) * 0.5, (cy - y) * 0.5  # drift inward
                color = INHALE_COL
            elif self.phase.name == "exhale":
                vx, vy = (x - cx) * 0.6, (y - cy) * 0.6  # drift outward
                color = EXHALE_COL
            else:
                vx = random.uniform(-10, 10); vy = random.uniform(-10, 10)
                color = HOLD_IN_COL if self.phase.name == "hold_in" else HOLD_OUT_COL
            life = random.uniform(1.0, 2.4)
            self.particles.append(_Particle(x, y, vx, vy, life, life,
                                            random.uniform(2.5, 5.5), color))
        new = []
        for p in self.particles:
            p.life -= dt
            if p.life > 0:
                p.x += p.vx * dt
                p.y += p.vy * dt
                new.append(p)
        self.particles = new

    def _finish(self):
        self.running = False
        self.app.audio.play("complete")
        self.app.audio.play_voice("complete")
        self.app.go(CompleteScene(self.app, self.routine))

    def _current_radius(self) -> float:
        ph = self.phase
        t = self.t_in_phase / max(0.0001, ph.seconds)
        t = max(0.0, min(1.0, t))
        if ph.name == "inhale":
            return lerp(self.min_r, self.max_r, ease_in_out(t))
        if ph.name == "exhale":
            return lerp(self.max_r, self.min_r, ease_in_out(t))
        if ph.name == "hold_in":
            return self.max_r + 3 * math.sin(t * math.pi * 4)
        return self.min_r + 2 * math.sin(t * math.pi * 4)

    def _phase_color(self):
        return {"inhale": INHALE_COL, "hold_in": HOLD_IN_COL,
                "exhale": EXHALE_COL, "hold_out": HOLD_OUT_COL}[self.phase.name]

    def _get_glow(self, radius: int, color) -> pygame.Surface:
        key = (radius, color)
        if key not in self._glow_cache:
            self._glow_cache[key] = make_glow(radius, color, inner_alpha=180)
        return self._glow_cache[key]

    def _remaining_total(self) -> int:
        total = 0
        per_cycle_now = sum(p.seconds for p in self.block.phases)
        # remainder of current cycle
        if self.running:
            elapsed_cycle = sum(p.seconds for p in self.block.phases[:self.phase_idx])
            elapsed_cycle += self.t_in_phase
            total += per_cycle_now - elapsed_cycle
        else:
            total += per_cycle_now
        total += per_cycle_now * (self.block.cycles - self.cycle_idx - 1)
        for b in self.routine.blocks[self.block_idx + 1:]:
            total += sum(p.seconds for p in b.phases) * b.cycles
        return int(total)

    def draw(self, surf):
        a = self.app.assets
        w, h = surf.get_size()
        cx = w // 2
        bg = a.bgs.get(self.block.bg_key, a.bgs.get("bg_home"))
        if bg: surf.blit(a.bg_dim[self.block.bg_key], (0, 0))
        else:  surf.fill(BG)

        # ---- HEADER (top stack, measured) ----
        y = int(h * 0.04)
        rect = draw_text(surf, self.routine.title, a.f_xl, TEXT, (cx, y), anchor="midtop")
        y = rect.bottom + int(h * 0.012)
        rect = draw_text(surf, self.routine.description, a.f_md, ACCENT, (cx, y), anchor="midtop")
        y = rect.bottom + int(h * 0.020)
        block_label = f"Block {self.block_idx + 1}/{len(self.routine.blocks)}  ·  {self.block.title}"
        rect = draw_text(surf, block_label, a.f_md_b, ACCENT_BRIGHT, (cx, y), anchor="midtop")
        y = rect.bottom + 6
        line = f"Cycle {self.cycle_idx + 1} / {self.block.cycles}"
        if self.running:
            rem = self._remaining_total()
            m, s = divmod(rem, 60)
            line += f"     ·     ~{m}:{s:02d} left"
        draw_text(surf, line, a.f_sm, TEXT_DIM, (cx, y), anchor="midtop")

        # ---- ORB (centered, smaller than before) ----
        # Reserved vertical band for the orb so it never collides with header
        # above or the text+buttons below.
        orb_cy = int(h * 0.50)

        # particles (behind orb)
        for p in self.particles:
            alpha = int(220 * (p.life / p.max_life))
            s = pygame.Surface((int(p.size * 4), int(p.size * 4)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*p.color, alpha),
                               (s.get_width() // 2, s.get_height() // 2), int(p.size))
            surf.blit(s, s.get_rect(center=(int(p.x), int(p.y))))

        if self.running or self.t_in_phase > 0:
            r = self._current_radius()
        else:
            r = self.min_r
        color = self._phase_color()
        qr = max(20, int(r) // 2 * 2)
        glow = self._get_glow(int(qr * 1.6), color)
        surf.blit(glow, glow.get_rect(center=(cx, orb_cy)))
        pygame.draw.circle(surf, color, (cx, orb_cy), int(r * 0.65))
        pygame.draw.circle(surf, ACCENT_BRIGHT, (cx, orb_cy), int(r * 0.65), 2)

        # ---- TEXT BELOW ORB (always below the orb's MAX extent, so nothing
        #      shifts as the orb breathes) ----
        below_y = orb_cy + self.max_r + int(h * 0.015)
        ph_label = self.phase.label if self.running or self.t_in_phase > 0 else "Ready"
        rect = draw_text(surf, ph_label, a.f_phase, TEXT, (cx, below_y), anchor="midtop")
        below_y = rect.bottom + int(h * 0.010)
        if self.running:
            remaining = max(0, self.phase.seconds - int(self.t_in_phase))
            draw_text(surf, str(remaining + 1), a.f_count, color, (cx, below_y), anchor="midtop")
        else:
            draw_text(surf, "▶", a.f_count, ACCENT, (cx, below_y), anchor="midtop")

        # note above buttons (just above the button row)
        if self.block.note:
            draw_text(surf, self.block.note, a.f_sm, TEXT_DIM,
                      (cx, self.btn_toggle.rect.top - int(h * 0.025)))

        self.btn_toggle.draw(surf)
        self.btn_back.draw(surf)


# ---------- complete ----------

class CompleteScene(Scene):
    def __init__(self, app, routine: Routine):
        super().__init__(app)
        self.routine = routine
        self.t = 0.0
        a = self.app.assets
        w, h = self.app.screen.get_size()
        cx = w // 2
        self.btn_home   = Button((cx - 200, h - 140, 180, 54), "Home",
                                 lambda: self.app.go(HomeScene(self.app)),
                                 font=a.f_md_b, primary=True)
        self.btn_again  = Button((cx + 20, h - 140, 200, 54), "Repeat session",
                                 lambda: self.app.go(SessionScene(self.app, routine)),
                                 font=a.f_md)

    def handle(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            self.app.go(HomeScene(self.app)); return
        self.btn_home.handle(e)
        self.btn_again.handle(e)

    def update(self, dt): self.t += dt

    def draw(self, surf):
        a = self.app.assets
        w, h = surf.get_size()
        bg = a.bgs.get("bg_complete")
        if bg: surf.blit(a.bg_dim["bg_complete"], (0, 0))
        else:  surf.fill(BG)

        cx = w // 2
        y = int(h * 0.36)
        rect = draw_text(surf, "Session complete", a.f_huge, TEXT,
                         (cx, y), anchor="midtop")
        y = rect.bottom + int(h * 0.025)
        rect = draw_text(surf, self.routine.title, a.f_lg, ACCENT,
                         (cx, y), anchor="midtop")
        y = rect.bottom + int(h * 0.020)
        draw_text(surf, "Sit a moment. Notice the calm.", a.f_md, TEXT_DIM,
                  (cx, y), anchor="midtop")
        draw_text(surf, f"Created by {DEVELOPER}", a.f_sm, TEXT_DIM,
                  (cx, h - int(h * 0.025)))
        self.btn_home.draw(surf)
        self.btn_again.draw(surf)


# ---------- about ----------

class AboutScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        a = self.app.assets
        w, h = self.app.screen.get_size()
        self.btn_back = Button((w // 2 - 90, h - 140, 180, 54), "Back",
                               lambda: self.app.go(HomeScene(self.app)),
                               font=a.f_md_b, primary=True)

    def handle(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            self.app.go(HomeScene(self.app)); return
        self.btn_back.handle(e)

    def draw(self, surf):
        a = self.app.assets
        w, h = surf.get_size()
        bg = a.bgs.get("bg_home")
        if bg: surf.blit(a.bg_dim["bg_home"], (0, 0))
        else:  surf.fill(BG)

        cx = w // 2
        y = int(h * 0.08)
        if a.icon is not None:
            sz = int(min(w, h) * 0.13)
            ic = pygame.transform.smoothscale(a.icon, (sz, sz))
            ic_rect = ic.get_rect(midtop=(cx, y))
            surf.blit(ic, ic_rect)
            y = ic_rect.bottom + int(h * 0.025)

        rect = draw_text(surf, APP_NAME, a.f_xl, TEXT, (cx, y), anchor="midtop")
        y = rect.bottom + int(h * 0.015)
        rect = draw_text(surf, f"Version {VERSION}", a.f_md, ACCENT, (cx, y), anchor="midtop")
        y = rect.bottom + int(h * 0.030)

        lines = [
            f"Developed by {DEVELOPER}",
            "TD Film Studio  ·  Guwahati, India",
            "",
            "Guided pranayama for sleep, stress, anxiety,",
            "elevated heart rate, and the wear-and-tear of",
            "long sedentary work days.",
            "",
            "Built with pygame, numpy.",
            "Ambient backgrounds generated with Higgsfield AI.",
            "",
            COPYRIGHT,
        ]
        line_h = a.f_md.get_linesize()
        for line in lines:
            if line:
                draw_text(surf, line, a.f_md, TEXT, (cx, y), shadow=False, anchor="midtop")
            y += line_h

        self.btn_back.draw(surf)


# =====================================================================
# APP
# =====================================================================

class App:
    def __init__(self):
        pygame.mixer.pre_init(SAMPLE_RATE, -16, 1, 256)
        pygame.init()
        info = pygame.display.Info()
        # Borderless full-screen at desktop res
        self.size = (info.current_w, info.current_h)
        flags = pygame.FULLSCREEN | pygame.SCALED
        try:
            self.screen = pygame.display.set_mode(self.size, flags)
        except pygame.error:
            self.screen = pygame.display.set_mode((1280, 800))
        pygame.display.set_caption(APP_NAME)
        icon_path = ASSETS / "icon.png"
        if icon_path.exists():
            try:
                pygame.display.set_icon(pygame.image.load(str(icon_path)))
            except Exception:
                pass
        self.assets = Assets(self.screen.get_size())
        self.audio = Audio()
        self.clock = pygame.time.Clock()
        self.running = True
        self.scene: Scene = SplashScene(self)

    def go(self, scene: Scene):
        self.scene = scene

    def quit(self):
        self.running = False

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                    continue
                self.scene.handle(e)
            self.scene.update(dt)
            self.scene.draw(self.screen)
            pygame.display.flip()
        pygame.quit()


def _main():
    try:
        App().run()
    except Exception:
        import traceback
        log = ROOT / "error.log"
        with log.open("w", encoding="utf-8") as f:
            f.write(f"{APP_NAME} v{VERSION} crashed at {time.ctime()}\n\n")
            traceback.print_exc(file=f)
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                0,
                f"{APP_NAME} hit an error and could not start.\n\n"
                f"Details written to:\n{log}\n\n"
                f"Please share that file with the developer.",
                f"{APP_NAME}", 0x10)
        except Exception:
            pass
        raise


if __name__ == "__main__":
    _main()
