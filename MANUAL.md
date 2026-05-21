# Box Breathing Studio — Complete Build Manual

> **Author**: Tarunabh Dutta · TD Film Studio, Guwahati
> **Version**: 2.1 · **Built**: 2026-05-21
> **Status**: Complete reference for the entire build session

This is the single source-of-truth document for the project. If everything else were lost — the local files, the GitHub repo, the assets — this manual contains enough information to **rebuild the entire app from scratch**, end-to-end, on a clean Windows PC.

It also serves as:
- A **decision log** explaining why each technology was chosen
- A **bug post-mortem** for the issues we hit and the exact fixes
- A **complete recipe** of every Higgsfield prompt, voice script, and shell command used
- An **end-user help manual** for anyone using the app

---

## Table of contents

1. [What was built](#1-what-was-built)
2. [Tech stack and why](#2-tech-stack-and-why)
3. [Phase A — Building the Windows desktop app from scratch](#3-phase-a--building-the-windows-desktop-app-from-scratch)
4. [Phase B — Generating the visual asset suite (Higgsfield)](#4-phase-b--generating-the-visual-asset-suite-higgsfield)
5. [Phase C — Building the offline-portable Python bundle](#5-phase-c--building-the-offline-portable-python-bundle)
6. [Phase D — Generating the voice narration (Edge TTS)](#6-phase-d--generating-the-voice-narration-edge-tts)
7. [Phase E — Building the mobile PWA from scratch](#7-phase-e--building-the-mobile-pwa-from-scratch)
8. [Phase F — Publishing to GitHub](#8-phase-f--publishing-to-github)
9. [Bug post-mortems and gotchas](#9-bug-post-mortems-and-gotchas)
10. [Maintenance recipes](#10-maintenance-recipes)
11. [End-user help documentation](#11-end-user-help-documentation)
12. [Future roadmap (Play Store, etc.)](#12-future-roadmap)
13. [Appendix A — Complete Higgsfield prompts used](#appendix-a--complete-higgsfield-prompts-used)
14. [Appendix B — Complete voice clip script](#appendix-b--complete-voice-clip-script)
15. [Appendix C — Repo file inventory](#appendix-c--repo-file-inventory)
16. [Appendix D — Glossary of pranayama terms](#appendix-d--glossary-of-pranayama-terms)

---

## 1. What was built

A free, offline, MIT-licensed meditation app in two flavours:

| Flavour | Platform | Tech | Size | Install path |
|---|---|---|---|---|
| **Windows desktop** | Windows 10/11 64-bit | Python 3.11 + Pygame + NumPy | ~140 MB | Download ZIP from GitHub Releases → extract → run `install_app.bat` |
| **Mobile PWA** | Android / iPhone | Vanilla HTML / CSS / JS | ~16 MB | Visit GitHub Pages URL in Chrome (Safari on iOS) → tap "Install" / "Add to home screen" |

**Both flavours share**:
- Same 9 routines (Smart Wizard, Box Breathing, 4-7-8, Bhramari, Nadi Shodhana, Nadi Shodhana Box, Extended Exhale, 15-min Daily, Custom Builder)
- Same 7 Higgsfield-generated ambient backgrounds
- Same 11 Microsoft Edge TTS voice clips (Aria Neural, slowed)
- Same colour palette, branding, and feature set

**Public URL** (lives on GitHub Pages):
```
https://tarunabhdutta.github.io/box-breathing-studio/
```

**Repo**:
```
https://github.com/tarunabhdutta/box-breathing-studio
```

---

## 2. Tech stack and why

### Decision matrix from the session

| Layer | Considered | Chosen | Why |
|---|---|---|---|
| Desktop UI | Tkinter, CustomTkinter, PyQt, Pygame | **Pygame** | True full-screen immersive control, smooth animations, particle effects. Tkinter v1 was too "utility-like". |
| Mobile platform | Native APK (Buildozer), TWA, **PWA** | **PWA** | Buildozer requires Linux + ~hours of setup. PWA delivers 95% of the experience with 5% of the work, installs from a URL, works offline. |
| Visuals | Hand-drawn, stock photos, AI | **Higgsfield AI (`soul_location` + `z_image`)** | Higgsfield was already in the user's MCP toolkit. `soul_location` is purpose-built for ambient backgrounds. |
| Voice TTS | Higgsfield, pyttsx3 (Windows SAPI), gTTS, **Edge TTS** | **Microsoft Edge TTS** | Higgsfield does NOT offer standalone TTS (only video-with-audio, would cost ~600 credits for 11 clips). Edge TTS gives studio-quality neural voices, free, pre-generated at build time. |
| Audio runtime | sounddevice (v1), **pygame.mixer** (v2) | **pygame.mixer** (desktop), **Web Audio API + HTML5 Audio** (mobile) | pygame.mixer removed the sounddevice dependency. Web Audio handles sine tones in browser without needing files. |
| Python distribution | System Python install, embeddable | **Embeddable Python 3.11.9** | "Works on any Windows 10/11 PC with no system Python install" — zero-prerequisite portability. |
| Hosting | Netlify, GitHub Pages | **GitHub Pages** | Free, permanent URL, automatic HTTPS, auto-deploys from repo via GitHub Actions, doubles as the stable URL needed for future Play Store TWA. |
| License | MIT, GPL, Apache | **MIT** | Most permissive; suits a personal-practice tool intended for free sharing. |

---

## 3. Phase A — Building the Windows desktop app from scratch

> **Goal**: A full-screen Pygame app with 9 routines, smart wizard, immersive ambient backgrounds, voice + sine-tone audio guidance.

### A.1 Folder structure (target)

Create on disk:

```
BoxBreathingApp/
├── app.py                    main application (~1500 lines)
├── install_app.bat           one-click installer (creates shortcuts)
├── run_app.bat               launcher used by the Desktop shortcut
├── README.txt                user-facing readme
├── assets/
│   ├── icon.png              app icon (2048x2048)
│   ├── icon.ico              multi-resolution Windows icon
│   ├── bg_home.png           7 ambient backgrounds
│   ├── bg_box.png
│   ├── bg_478.png
│   ├── bg_bhramari.png
│   ├── bg_nadi.png
│   ├── bg_extended.png
│   ├── bg_complete.png
│   └── voice/
│       ├── inhale.mp3        11 voice clips
│       ├── hold.mp3
│       ├── exhale.mp3
│       ├── hold_empty.mp3
│       ├── inhale_left.mp3
│       ├── inhale_right.mp3
│       ├── exhale_left.mp3
│       ├── exhale_right.mp3
│       ├── hum.mp3
│       ├── begin.mp3
│       └── complete.mp3
└── python_portable/          bundled Python (created by build_portable.bat)
    ├── python.exe
    ├── pythonw.exe
    └── Lib/site-packages/
        ├── numpy/
        └── pygame/
```

### A.2 The Python app (`app.py`) — architectural overview

The complete source is in [`windows/app.py`](windows/app.py) in the repo (~46 KB, ~1500 lines). Major sections:

1. **Constants / identity** — colours, developer name, version, sample rate
2. **AUDIO** — `Audio` class with `playTone`, `playVoice`, `playHum`. Uses pygame.mixer. Stereo-safe (see [§9.1](#91-bug-stereo-mixer-rejects-mono-buffers)).
3. **ROUTINES** — `Phase`, `Block`, `Routine` dataclasses. Factory functions: `routine_box`, `routine_478`, `routine_bhramari`, `routine_nadi`, `routine_nadi_box` (new classical alternation), `routine_extended_exhale`, `routine_daily_15`, `routine_custom`. Plus `pick_routine` for the wizard.
4. **RENDER HELPERS** — `make_glow`, `draw_text`, `darken`, easing functions.
5. **ASSETS** — Asset class that loads PNGs and pre-renders dimmed versions; loads scaled fonts based on screen height.
6. **WIDGETS** — Button, Tile, Slider, RadioGroup.
7. **SCENES** — Splash, Home, Wizard, Custom, Session, Complete, About. Each is a `ttk.Frame`-style class with `handle`, `update`, `draw`.
8. **APP** — orchestrates the Pygame main loop, scene swaps, full-screen init.

### A.3 The 9 routines — phase patterns

| Routine | Pattern | Cycles | Duration |
|---|---|---|---|
| Box Breathing (Beginner) | 3-3-3-3 | 10 | 2:00 |
| Box Breathing (Intermediate) | 4-4-4-4 | 10 | 2:40 |
| Box Breathing (Advanced) | 6-6-6-6 | 10 | 4:00 |
| 4-7-8 | 4-7-8-0 | 8 | 2:32 |
| Bhramari | 4-0-8-0 (with hum) | 7 | 1:24 |
| Nadi Shodhana (two-round) | 4-4-4-4, L-start then R-start | 5+5 blocks | 2:40 |
| **Nadi Shodhana Box** (new) | 8-phase alternating cycle (see §A.4) | 7 | 3:44 |
| Extended Exhale | 4-0-6-0 | 12 | 2:00 |
| 15-min Daily | Multi-block sequence | 34 cycles total | ~15:00 |
| Custom | User-defined 1-12s phases, 3-30 cycles | variable | variable |

### A.4 Nadi Shodhana Box (the new variant) — explained

**Classical 8-phase cycle**, 32 seconds per cycle, repeated 7 times:

| Step | Phase | Duration | Voice cue |
|---|---|---|---|
| 1 | Inhale LEFT | 4 s | "Inhale through the left nostril" |
| 2 | Hold (full) | 4 s | "Hold" |
| 3 | Exhale RIGHT | 4 s | "Exhale through the right nostril" |
| 4 | Hold (empty) | 4 s | "Hold" |
| 5 | Inhale RIGHT | 4 s | "Inhale through the right nostril" |
| 6 | Hold (full) | 4 s | "Hold" |
| 7 | Exhale LEFT | 4 s | "Exhale through the left nostril" |
| 8 | Hold (empty) | 4 s | "Hold" |

This differs from the simpler two-round Nadi Shodhana (which keeps the same inhale-side for 5 reps before swapping). The classical pattern alternates **every breath**, which is closer to the traditional pranayama transmission.

### A.5 Smart Wizard logic

The 3-question wizard maps to one of 5 routine recommendations:

```
if sleep == "poor" OR (hour >= 21 AND stress >= 3):
    → "Sleep Reset" (Extended Exhale → 4-7-8 → Bhramari)
elif stress >= 4:
    → "Acute Stress Reset" (Box → Nadi Shodhana)
elif hours_sat >= 10:
    → "Long-Sitting Reset" (Box → Extended Exhale → Bhramari)
elif hour < 11:
    → "Morning Box" (Box, 10 cycles)
else:
    → 15-min Daily Sequence (default)
```

### A.6 Colour palette (used everywhere)

```python
BG            = (13, 27, 42)      # deep navy
PANEL         = (27, 38, 59)      # panel
ACCENT        = (127, 219, 218)   # soft cyan
ACCENT_BRIGHT = (166, 232, 231)
ACCENT_DIM    = (58, 138, 137)
TEXT          = (224, 230, 237)
TEXT_DIM      = (141, 153, 174)
INHALE_COL    = (127, 219, 218)   # cyan — inhale
HOLD_IN_COL   = (244, 211, 94)    # gold — hold full
EXHALE_COL    = (239, 131, 84)    # coral — exhale
HOLD_OUT_COL  = (157, 141, 241)   # lavender — hold empty
```

### A.7 Phase-tone frequencies (sine wave cues)

```python
PHASE_TONES = {
    "inhale":   (220.0 Hz, 0.40 s),   # low warm
    "hold_in":  (330.0 Hz, 0.25 s),   # mid
    "exhale":   (165.0 Hz, 0.50 s),   # lower
    "hold_out": (110.0 Hz, 0.25 s),   # lowest
    "complete": (440.0 Hz, 0.70 s),   # bell
}
```

Sample rate: 44100 Hz. Each tone has a 40 ms linear fade in/out to avoid clicks.

### A.8 Installer scripts

**`install_app.bat`** — verifies `python_portable\pythonw.exe` exists, creates Desktop + Start Menu shortcuts (via embedded PowerShell + WScript.Shell COM), launches the app on user confirmation.

**`run_app.bat`** — single-line launcher: `start "" "python_portable\pythonw.exe" "app.py"`. Uses `pythonw` (not `python`) so no console window flashes on launch.

**`build_portable.bat`** (in `windows/`, git-tracked) — rebuilds the `python_portable/` folder from scratch. See [§5](#5-phase-c--building-the-offline-portable-python-bundle).

---

## 4. Phase B — Generating the visual asset suite (Higgsfield)

> **Goal**: 8 ambient images — 1 app icon + 7 technique-specific backgrounds — using Higgsfield AI.

### B.1 Model choices

- **`z_image`** (Tongyi-MAI) — fast, stylized text-to-image. Used for the **app icon** at 1:1 aspect.
- **`soul_location`** (Higgsfield) — purpose-built for environments / backgrounds. Used for **all 7 backgrounds** at 16:9.

Both accept text-only prompts (no reference images required) and output at 2048×2048 (1:1) or 2048×1152 (16:9).

### B.2 Asset list — what to generate

| File | Aspect | Model | Mood |
|---|---|---|---|
| `icon.png` | 1:1 | `z_image` | Lotus + breath ripples, cyan + gold on navy |
| `bg_home.png` | 16:9 | `soul_location` | Cosmic aurora (Aurora Ridge) |
| `bg_box.png` | 16:9 | `soul_location` | Sacred geometry, teal (Azure Mindfulness Studio) |
| `bg_478.png` | 16:9 | `soul_location` | Moonlit night (Crescent Bay) |
| `bg_bhramari.png` | 16:9 | `soul_location` | Golden honey sunset (Sunset Sound) |
| `bg_nadi.png` | 16:9 | `soul_location` | Two streams merging (Nadi Sangam) |
| `bg_extended.png` | 16:9 | `soul_location` | Peaceful dawn (Lac de l'Aube) |
| `bg_complete.png` | 16:9 | `soul_location` | Golden mandala sunburst (Surya Mandir) |

The full prompt text used for each is in **[Appendix A](#appendix-a--complete-higgsfield-prompts-used)**.

### B.3 Generation steps (for re-running in future)

1. Call the Higgsfield MCP `balance` to check available credits.
2. Call `generate_image` with each prompt (jobs run asynchronously — submit all 8 in parallel).
3. Call `job_display` with the returned job IDs to retrieve completion status + result URLs.
4. Download each URL using `Invoke-WebRequest` (or `curl`).
5. Save under `assets/` (desktop) and `mobile/assets/bg/` (mobile) — they share identical files.
6. Generate `icon.ico` from `icon.png` once via Pillow:

   ```python
   from PIL import Image
   im = Image.open('assets/icon.png')
   im.save('assets/icon.ico',
           sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)])
   ```

7. Generate PWA icons (192/512 PNG) for the mobile manifest:

   ```python
   from PIL import Image
   im = Image.open('assets/icon.png')
   im.resize((192,192), Image.LANCZOS).save('mobile/icons/icon-192.png')
   im.resize((512,512), Image.LANCZOS).save('mobile/icons/icon-512.png')
   ```

> Total credit cost: ~30-50 Higgsfield credits across the 8 images (varies by current pricing).

---

## 5. Phase C — Building the offline-portable Python bundle

> **Goal**: A self-contained `python_portable/` folder containing Python 3.11.9 + numpy + pygame. After this is in place, the user needs no system Python install — `pythonw.exe app.py` works directly.

### C.1 Why embeddable Python

The official **Python embeddable zip** is a stripped-down distribution intended exactly for redistributing with apps. It includes:
- `python.exe` / `pythonw.exe`
- The standard library (compressed in `python311.zip`)
- Core DLLs

It does NOT include `pip` or `site-packages`. We add those.

### C.2 Step-by-step build

These exact commands rebuild the entire portable Python from nothing. (Also encoded in `windows/build_portable.bat`.)

```powershell
# 1. Download the embeddable Python zip
$url = 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip'
Invoke-WebRequest -Uri $url -OutFile 'build_cache\python_embed.zip' -UseBasicParsing

# 2. Extract to python_portable/
Expand-Archive 'build_cache\python_embed.zip' -DestinationPath 'python_portable' -Force

# 3. Enable site-packages — edit python311._pth
# Replace "#import site" with "import site" + a new line "Lib\site-packages"
(Get-Content 'python_portable\python311._pth') `
    -replace '#import site', "import site`r`nLib\site-packages" `
    | Set-Content 'python_portable\python311._pth'

# 4. Download get-pip.py and install pip into the embeddable Python
Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' `
    -OutFile 'build_cache\get-pip.py' -UseBasicParsing
.\python_portable\python.exe 'build_cache\get-pip.py' --no-warn-script-location

# 5. Install runtime dependencies
.\python_portable\python.exe -m pip install --no-warn-script-location numpy pygame
```

### C.3 Final bundle sizes

```
python_portable/    ~120 MB
  Lib/site-packages/
    numpy/          ~50 MB
    pygame/         ~30 MB
    pip/setuptools  ~10 MB
  (Python core)     ~30 MB

Assets:
  bg images         ~15 MB (7 PNGs)
  icon              ~5 MB
  voice clips       ~0.2 MB (11 MP3s)

Total bundle:       ~140 MB
```

### C.4 Verifying the bundle works

```powershell
.\python_portable\python.exe -c "import numpy, pygame; print(numpy.__version__, pygame.version.ver)"
```

Should print something like `2.4.6 2.6.1`. If it errors, repeat step 3 (the `._pth` edit is the most fragile part).

---

## 6. Phase D — Generating the voice narration (Edge TTS)

> **Goal**: 11 calm, slowed voice clips for phase guidance + session start/end. Pre-generated once at build time, bundled as MP3.

### D.1 Why Edge TTS and not Higgsfield/SAPI/gTTS

| Option | Verdict |
|---|---|
| Higgsfield audio | ❌ No standalone TTS — only video models with synchronized audio. Would cost ~600 credits to generate 11 clips via video and extract. |
| Windows SAPI / pyttsx3 | ⚠️ Free, offline at runtime, but voices sound more robotic. Generation is fine. |
| gTTS (Google Translate) | ⚠️ Needs internet at runtime if not pre-generated. Lower quality than Edge. |
| **Microsoft Edge TTS** | ✅ Neural voices, free, very high quality. Generated once at build time, bundled as MP3. |

### D.2 Voice settings

- **Voice**: `en-US-AriaNeural` (calm warm female, US English neutral)
- **Rate**: `-22%` (slowed for meditation)
- **Pitch**: `-3Hz` (slightly lower for warmth)

Alternative voices we considered but didn't use:
- `en-US-JennyNeural` (warm female, slightly more chipper)
- `en-IN-NeerjaNeural` (Indian English female, culturally aligned with pranayama)
- `en-US-GuyNeural` / `en-GB-RyanNeural` (calm male, grounding)

### D.3 Generation script

Save as `_generate_voice.py` in the BoxBreathingApp folder (this is a one-time build artefact, not bundled with the app):

```python
import asyncio
from pathlib import Path
import edge_tts

VOICE = "en-US-AriaNeural"
RATE  = "-22%"
PITCH = "-3Hz"
OUT   = Path(__file__).parent / "assets" / "voice"
OUT.mkdir(parents=True, exist_ok=True)

CLIPS = {
    "inhale":         "Breathe in.",
    "hold":           "Hold.",
    "exhale":         "Breathe out.",
    "hold_empty":     "Hold.",
    "inhale_left":    "Inhale through the left nostril.",
    "inhale_right":   "Inhale through the right nostril.",
    "exhale_left":    "Exhale through the left nostril.",
    "exhale_right":   "Exhale through the right nostril.",
    "hum":            "Hum.",
    "begin":          "Let's begin. Settle into your breath.",
    "complete":       "Session complete. Notice the calm.",
}

async def synth(text, out_path):
    tts = edge_tts.Communicate(text=text, voice=VOICE, rate=RATE, pitch=PITCH)
    await tts.save(str(out_path))

async def main():
    for key, text in CLIPS.items():
        await synth(text, OUT / f"{key}.mp3")
        print(f"  {key:14} -> {key}.mp3")

asyncio.run(main())
```

### D.4 Build-time setup and teardown

```powershell
# Temporarily install edge-tts in the portable Python
.\python_portable\python.exe -m pip install --no-warn-script-location edge-tts

# Run the script
.\python_portable\python.exe _generate_voice.py

# After clips are saved, uninstall edge-tts and its async deps
# (otherwise they bloat the bundle by ~15 MB)
.\python_portable\python.exe -m pip uninstall -y edge-tts aiohttp aiohappyeyeballs `
    aiosignal yarl multidict frozenlist propcache attrs certifi srt tabulate

# Delete the build script
Remove-Item _generate_voice.py
```

Final voice folder: 11 MP3 files, ~200 KB total. The app then plays them at runtime using pygame.mixer.Sound (desktop) or HTML5 `<Audio>` (mobile).

---

## 7. Phase E — Building the mobile PWA from scratch

> **Goal**: A touch-native Progressive Web App that reuses the same 8 backgrounds + 11 voice clips, installable on Android via Chrome's "Install app" / "Add to home screen" flow.

### E.1 PWA folder structure

```
BoxBreathingMobile/                    (= mobile/ in repo)
├── index.html                         shell — loads CSS + JS
├── styles.css                         mobile-first dark theme
├── app.js                             all logic (~30 KB)
├── manifest.json                      makes it installable
├── service-worker.js                  caches everything for offline
├── README.txt                         install guide
├── icons/
│   ├── icon-192.png                   home screen icon
│   └── icon-512.png                   splash + maskable
└── assets/
    ├── bg/                            7 background PNGs (same as desktop)
    └── voice/                         11 voice MP3s (same as desktop)
```

### E.2 The three "must-have-or-Chrome-won't-install-you" files

#### `manifest.json` — makes the page installable

```json
{
  "name": "Box Breathing Studio",
  "short_name": "Box Breath",
  "start_url": "./index.html",
  "scope": "./",
  "display": "standalone",
  "orientation": "portrait",
  "background_color": "#0d1b2a",
  "theme_color": "#0d1b2a",
  "icons": [
    { "src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png",
      "purpose": "maskable" }
  ]
}
```

Required fields for installability: `name` or `short_name`, `icons` (with 192 AND 512), `start_url`, `display` (must be `standalone`, `fullscreen`, or `minimal-ui`).

#### `service-worker.js` — caches everything for offline use

Pre-caches all CSS, JS, icons, backgrounds, and voice clips on first install. Subsequent visits hit the cache. The page must be served over HTTPS (or `localhost`) for the service worker to register at all.

#### `index.html` — links manifest + registers service worker

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1,
                                  viewport-fit=cover, user-scalable=no">
  <meta name="theme-color" content="#0d1b2a">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <link rel="manifest" href="manifest.json">
  <link rel="icon" href="icons/icon-192.png">
  <link rel="apple-touch-icon" href="icons/icon-192.png">
  <link rel="stylesheet" href="styles.css">
  <title>Box Breathing Studio</title>
</head>
<body>
  <div id="app"></div>
  <script src="app.js"></script>
</body>
</html>
```

### E.3 The JavaScript port — design choices

The Python code translated to JS roughly 1:1, but with these adjustments:

| Python (desktop) | JavaScript (mobile) |
|---|---|
| `pygame.mixer.Sound` | HTML5 `<Audio>` for voice MP3s |
| Pre-generated sine WAVs via `pygame.sndarray.make_sound` | **Web Audio API** `OscillatorNode` (generated on the fly, no files) |
| Custom Tkinter-style widgets | Native DOM `<button>` / `<input type="range">` |
| `pygame.Surface` for orb gradient | CSS `radial-gradient` + `transform: scale()` |
| 60 fps `clock.tick(60)` | `requestAnimationFrame` |
| `pygame.FULLSCREEN \| pygame.SCALED` | Manifest `display: standalone` |
| Mouse events | Touch events (`click` works for both) |
| n/a | **Wake Lock API** to keep screen on during sessions |
| n/a | **Visibility API** to pause when app goes to background |

### E.4 Mobile-specific gotchas handled

1. **Audio unlock** — mobile browsers require a user gesture before audio plays. The first tile tap calls `AudioContext.resume()`.
2. **Wake lock** — `navigator.wakeLock.request("screen")` prevents the screen from dimming during a session. Released on session exit.
3. **Hardware back button** — `popstate` listener catches Android's hardware back press and routes to home instead of closing the app.
4. **iOS quirk** — iOS only supports PWA install via **Safari** (not Chrome on iOS). Documented in INSTALL.md.

---

## 8. Phase F — Publishing to GitHub

> **Goal**: Push the code to GitHub, auto-deploy the PWA to GitHub Pages for installation by anyone via URL.

### F.1 Repo structure (final)

```
box-breathing-studio/                  (the GitHub repo)
├── README.md                          public-facing
├── LICENSE                            MIT
├── INSTALL.md                         newcomer install guide
├── MANUAL.md                          this document
├── .gitignore                         excludes python_portable/, *.log, etc.
├── .github/workflows/
│   └── deploy-pages.yml               auto-deploys mobile/ to GitHub Pages
├── windows/                           desktop source (NO python_portable/)
│   ├── app.py
│   ├── install_app.bat
│   ├── run_app.bat
│   ├── build_portable.bat
│   ├── README.txt
│   └── assets/
└── mobile/                            PWA source (complete)
    ├── index.html
    ├── styles.css
    ├── app.js
    ├── manifest.json
    ├── service-worker.js
    ├── README.txt
    ├── icons/
    └── assets/
```

### F.2 .gitignore (what does NOT get committed)

```
windows/python_portable/    # 120 MB, rebuilt locally via build_portable.bat
__pycache__/
*.pyc
*.log
error.log
build_cache/
*.zip
.DS_Store
Thumbs.db
.vscode/
.idea/
```

### F.3 GitHub Actions for auto-deploy

`.github/workflows/deploy-pages.yml` deploys `mobile/` to GitHub Pages on every push to `main` that touches `mobile/**`. Uses the modern `actions/upload-pages-artifact@v3` + `actions/deploy-pages@v4` flow (no `gh-pages` branch needed).

### F.4 First-time push commands

After creating the empty repo on github.com (no README, no .gitignore — we have our own):

```powershell
# Tell git who you are (first time only, on this PC)
git config --global user.email "your.email@example.com"
git config --global user.name "Your Name"

cd C:\SD\CLAUDE\box-breathing-studio

git init
git add .
git commit -m "Initial commit: Windows desktop + mobile PWA"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/box-breathing-studio.git
git push -u origin main
```

**Auth note**: Modern Git for Windows uses **browser-based OAuth** via Git Credential Manager. A browser tab opens for you to log in. If that doesn't appear, generate a Personal Access Token at [github.com/settings/tokens](https://github.com/settings/tokens) with the `repo` scope and paste it as the password.

### F.5 Enable GitHub Pages

After the first push:

1. Visit your repo on github.com → **Settings** → left sidebar → **Pages**
2. Under **Build and deployment** → **Source**, select **GitHub Actions**
3. Wait ~1-2 minutes — the workflow auto-runs from the initial push.
4. Live URL appears: `https://YOUR-USERNAME.github.io/box-breathing-studio/`

### F.6 Subsequent updates

```powershell
# After making changes
git add .
git commit -m "Brief description of the change"
git push
```

GitHub Actions auto-redeploys within ~1 minute of every push.

### F.7 Making the Windows ZIP downloadable via GitHub Releases

The repo intentionally does NOT contain the 120 MB `python_portable/` folder. Users who want a ready-to-run install (not a build-from-source) need a ZIP from Releases:

```powershell
# Build the complete bundle locally (with python_portable/ included)
cd C:\SD\CLAUDE\BoxBreathingApp     # original working folder
Compress-Archive -Path .\* -DestinationPath '..\BoxBreathingApp-windows.zip'
```

Then:

1. GitHub repo → **Releases** → **Create a new release**
2. Tag: `v2.1` · Title: `v2.1 — Voice + Nadi Box`
3. Drop the ZIP onto "Attach binaries"
4. **Publish release**

---

## 9. Bug post-mortems and gotchas

Five real bugs hit during this build. Each one taught something worth remembering.

### 9.1 BUG: Stereo mixer rejects mono buffers

**Symptom**: App launches via `run_app.bat`, console flashes for a split second, app dies. No error visible because `pythonw.exe` suppresses stderr.

**Root cause**: Audio engine generated mono sine-wave buffers (1-D numpy arrays). Pygame's mixer initialized as stereo (2 channels) on the real audio driver, ignoring `pygame.mixer.pre_init(channels=1)`. Calling `pygame.sndarray.make_sound(mono_buffer)` threw `ValueError: Array must be 2-dimensional for stereo mixer`.

**Why it didn't show up in testing**: Headless smoke tests used the SDL `"dummy"` audio driver which accepts anything.

**Fix**: Make audio buffers stereo-safe regardless of mixer init. In `Audio._to_sound`:

```python
@staticmethod
def _to_sound(pcm_mono: np.ndarray) -> pygame.mixer.Sound:
    channels = pygame.mixer.get_init()[2] if pygame.mixer.get_init() else 2
    if channels == 2:
        buf = np.column_stack([pcm_mono, pcm_mono])
    else:
        buf = pcm_mono
    return pygame.sndarray.make_sound(np.ascontiguousarray(buf))
```

**Also added**: a top-level try/except in `_main()` that writes any future crash to `error.log` and shows a Windows MessageBox, so silent failures can't happen again.

### 9.2 BUG: Overlapping text and oversized countdown

**Symptom**: User reports header text overlapping subtitle, countdown number so big it eats the phase label below it.

**Root cause 1**: Countdown font was `140 * scale` (where `scale = h / 800.0`). On 1080p that's 189 pixels tall — bigger than the gap I'd reserved between phase label and countdown.

**Root cause 2**: All header positions were hard-coded pixel values (`y=60`, `y=110`, `y=140`). On a tall display, font heights grew but the gaps between them didn't — title's bottom ended up only 5 px above the subtitle's top.

**Fix**: Two-part change in `Assets._fonts` and every scene's `draw` method:

1. Reduced font sizes and clamped the scale factor:
   ```python
   scale = max(0.7, min(1.4, h / 1080.0))   # 1080p reference, clamped
   self.f_count = f(72, True)               # was 140 — way smaller now
   ```

2. Replaced all hard-coded y values with measured stacking using `rect.bottom + gap`:
   ```python
   y = int(h * 0.04)
   rect = draw_text(surf, title, a.f_xl, TEXT, (cx, y), anchor="midtop")
   y = rect.bottom + int(h * 0.012)
   draw_text(surf, subtitle, a.f_md, ACCENT, (cx, y), anchor="midtop")
   ```

3. Moved phase label and countdown **below** the breathing orb (instead of inside it) so they have a stable position regardless of orb scale.

4. Reduced orb max radius from `0.32 * min(w, h)` to `0.16 * min(w, h)` — was taking up two-thirds of the screen height before.

### 9.3 GOTCHA: Higgsfield has no standalone TTS

When the user asked for voiceovers "generated with Higgsfield audio", the natural assumption was Higgsfield had a TTS model. It does not — all audio-capable Higgsfield models are video models with synchronized audio. Generating 11 voice clips through Veo3 / Kling would have cost ~600 credits, taken hours, and required ffmpeg to extract the audio.

**Decision**: pivot to **Microsoft Edge TTS** — free, high-quality neural voices, generated once at build time. This was the right call.

### 9.4 GOTCHA: Higgsfield doesn't support APK building

When the user asked for an Android installer, the natural path was "build an APK". The realistic options were all heavy:
- Buildozer requires Linux (WSL2 setup on Windows) + 4-8 hours
- Cloud APK build via GitHub Actions requires Kivy rewrite + workflow setup
- Local Android Studio build requires Android SDK + Kotlin/Java rewrite

**Decision**: pivot to **PWA**. Delivers 95% of the native experience for 5% of the work, installs in 3 minutes via Chrome's "Install app" button, uses the same backgrounds and voice clips.

### 9.5 GOTCHA: Git identity not set

First `git commit` failed with `Author identity unknown`. Standard fix:

```powershell
git config --global user.email "your.email@example.com"
git config --global user.name "Your Name"
```

Email should match the address registered on your GitHub account (or the GitHub-provided no-reply email at `<id>+<username>@users.noreply.github.com`).

### 9.6 GOTCHA: Chrome's "Install app" sometimes labeled "Add to home screen"

Chrome's PWA install option shows different text depending on Chrome version:
- Newer Chrome → "Install app"
- Older Chrome → "Add to home screen"
- Sometimes neither shows until you've interacted with the page (engagement heuristic)

**Workaround**: Tap any tile and let a session run for a few seconds before opening the Chrome menu. This satisfies Chrome's engagement requirement and unlocks the install option.

### 9.7 GOTCHA: PWA install vs bookmark fallback

If Chrome doesn't recognize the page as a proper PWA (missing manifest fields, service worker not registered, etc.), "Add to home screen" creates a bookmark shortcut instead — opens inside Chrome with the address bar visible, no full-screen mode, no offline support.

**How to tell**: Tap the home-screen icon. If the app opens **full-screen with no Chrome address bar**, it's a real PWA install. If you see the address bar, it's a bookmark — long-press the icon, remove, redo the install after interacting with the page first.

---

## 10. Maintenance recipes

Common future tasks and exactly how to do them.

### 10.1 Add a new breathing technique

1. **Edit `windows/app.py`**: add a `routine_yourname()` factory near the existing routines. Define a list of `Phase("inhale", seconds, "Label", voice="inhale")` etc.
2. **Add a tile to home screen**: in `HomeScene._build()`, append to the `items` list:
   ```python
   ("Your Routine", "Brief subtitle", "bg_box",
    lambda: self.app.go(SessionScene(self.app, routine_yourname()))),
   ```
3. **Mirror in `mobile/app.js`**: write the same routine factory in JS, add it to the `tiles` array in `sceneHome()`.
4. If the routine needs new voice cues, regenerate the relevant clips (see [§10.3](#103-regenerate-or-change-voice-clips)).
5. Commit + push. Pages auto-redeploys.

### 10.2 Regenerate or replace ambient backgrounds

1. Open the prompt from **[Appendix A](#appendix-a--complete-higgsfield-prompts-used)** that you want to change.
2. Call Higgsfield `generate_image` with the new prompt.
3. Download the result via `Invoke-WebRequest`.
4. Overwrite both `windows/assets/bg_xxx.png` AND `mobile/assets/bg/bg_xxx.png` with the new file.
5. Commit + push.

### 10.3 Regenerate or change voice clips

1. Edit the `CLIPS` dictionary in `_generate_voice.py` (script in [§6.3](#d3-generation-script)).
2. Optional: change `VOICE`, `RATE`, or `PITCH`.
3. Install edge-tts, run the script, uninstall edge-tts (commands in [§6.4](#d4-build-time-setup-and-teardown)).
4. Copy the resulting MP3s to both `windows/assets/voice/` and `mobile/assets/voice/`.
5. Commit + push.

### 10.4 Update the Windows ZIP on Releases

1. Make code changes, test locally on the live `BoxBreathingApp/` folder.
2. Re-zip:
   ```powershell
   Compress-Archive -Path C:\SD\CLAUDE\BoxBreathingApp\* `
       -DestinationPath C:\SD\CLAUDE\BoxBreathingApp-v2.2.zip -Force
   ```
3. On GitHub → Releases → **Draft a new release** → tag `v2.2` → drop ZIP → publish.

### 10.5 Change the developer credit / branding

Strings to update:
- `windows/app.py` — constants near top: `DEVELOPER`, `APP_NAME`, `VERSION`, `COPYRIGHT`
- `mobile/app.js` — same constants near top
- `README.md`, `INSTALL.md`, `LICENSE`, `MANUAL.md` — search for the name

### 10.6 Rebuild python_portable on a fresh PC

```powershell
cd box-breathing-studio\windows
.\build_portable.bat
```

That's the entire process. The script handles download, extraction, pip install, and dependency setup. Takes ~3 minutes with internet.

---

## 11. End-user help documentation

For users who download / install the app — this is what they see on screen and what they should know.

### 11.1 First launch

- **Splash screen** (~2.5 seconds) — Lotus icon fades in, then "Box Breathing Studio · Created by Tarunabh Dutta" appears. Auto-transitions to Home.

### 11.2 Home screen

| Element | What it does |
|---|---|
| Tile grid (3×3) | 9 routines — tap any to start. Each shows a thumbnail and one-line description. |
| Volume slider | Master volume for tones + voice. Slide to 0 to silence. |
| Voice toggle | "Voice ON" (cyan) plays narration at every phase. Tap to mute → "Voice OFF" (gray) — beeps only. |
| About button | Credits, version, contraindications. |
| Quit button (Windows only) | Closes the app. |

### 11.3 Smart Wizard

Three sliders, takes about 10 seconds:

1. **Stress level** (1–5) — How wired do you feel right now?
2. **Hours sat today** (0–16) — Sedentary time at the desk today.
3. **Sleep last night** (Poor / OK / Good)

The wizard maps to one of:
- Sleep Reset (if sleep was poor OR it's late and you're stressed)
- Acute Stress Reset (if stress ≥ 4)
- Long-Sitting Reset (if you've sat ≥ 10 hours)
- Morning Box (if before 11 AM)
- 15-min Daily Sequence (default)

### 11.4 Session screen

| Element | What it shows |
|---|---|
| Routine title (top) | "Box Breathing — Intermediate" or whatever you picked |
| Block info | "Block 1/3 · Box Breathing" — for multi-block routines |
| Cycle info | "Cycle 4 / 10  ·  ~3:20 left" |
| **Breathing orb** | Smoothly expands on inhale, holds, contracts on exhale. Colour matches phase. |
| Phase label | "Inhale" / "Hold" / "Exhale" / "Hold empty" / left-right variants |
| **Countdown number** | Seconds remaining in current phase |
| Note text | Block-specific reminders (posture, mudra, etc.) |
| Pause/Resume button | Tap or press SPACE (desktop) |
| End session button | Tap or press ESC (desktop) |

**Audio**: A soft sine-wave tone marks each phase transition (different pitch per phase). When voice is on, narration plays over it: "Breathe in", "Hold", "Breathe out". Bhramari adds a low harmonic hum during the exhale.

### 11.5 Keyboard shortcuts (desktop only)

| Key | Action |
|---|---|
| **ESC** | Exit session → return to Home |
| **SPACE** | Pause / Resume current session |
| **Mouse hover** | Tile glow effect |
| **Mouse click** | Select tile / button |

### 11.6 Custom Builder

Five sliders, then "Start session":

- **Inhale** (1–12 sec)
- **Hold full** (0–12 sec) — set to 0 to skip
- **Exhale** (1–12 sec)
- **Hold empty** (0–12 sec) — set to 0 to skip
- **Cycles** (3–30)

Useful for: trying out non-standard ratios (e.g. 4-7-8 with different counts), gradually working up to advanced Box (5-5-5-5, 6-6-6-6), or building wind-down routines with 4:8 inhale:exhale.

### 11.7 Contraindications and safety

| Condition | Guidance |
|---|---|
| High blood pressure | Skip post-inhale hold (Kumbhaka). Use Extended Exhale or Custom with Hold In = 0. |
| Pregnancy | Avoid breath retention. Stick to Extended Exhale. |
| Severe respiratory condition (COPD, severe asthma) | Consult doctor before practicing breath retention. |
| Anxiety disorder (panic) | Start with Extended Exhale or Bhramari — they're the most calming. Avoid 4-7-8 if it triggers air-hunger. |
| Lightheaded during practice | Stop immediately. Breathe naturally. You may be over-retaining or hyperventilating. |
| Pre-existing cardiac condition | Run by your doctor first. |

### 11.8 When to practice for which benefit

| Goal | Best routine | Best time |
|---|---|---|
| Falling asleep | 4-7-8, then Bhramari | 20–30 min before bed |
| Anxiety / panic | Box Breathing, Extended Exhale | Anywhere, anytime |
| Energy and focus | Morning Box, Nadi Shodhana | Morning, between work blocks |
| Recovery from long sitting | Long-Sitting Reset (wizard) | Mid-afternoon |
| Heart rate variability training | 15-min Daily | Same time daily for 4+ weeks |
| Stress in the moment | Acute Stress Reset (wizard) | Whenever you notice tension |

### 11.9 Troubleshooting

| Issue | Fix |
|---|---|
| Mobile app silent on first tap | Tap any tile first — mobile browsers require a user gesture before audio plays. |
| Mobile install option missing | Tap a tile, run a session for 5–10 seconds, then check the Chrome menu. Engagement heuristic. |
| Mobile install creates a bookmark, not a real app | Long-press icon → remove → interact with the page first → retry install. |
| Windows: error.log appears in the folder | Open it. Tells you exactly what crashed. Most likely: missing voice clip or stale `python_portable`. |
| Windows: Defender SmartScreen warning | "More info" → "Run anyway". Code is open source on GitHub — verify by reading `app.py` first if concerned. |
| Voice sounds robotic | You may have voice OFF (toggle on home) and the system fallback is playing. Toggle voice ON. |
| App won't update on phone after I push to GitHub | Service worker caches aggressively. On phone: clear site data for `tarunabhdutta.github.io`, or uninstall and reinstall the PWA. |

---

## 12. Future roadmap

Things explicitly considered but not done in this session, in priority order.

### 12.1 Google Play Store submission (TWA path)

Requires:
- $25 one-time Google Play Developer fee
- 14-day initial account hold + 20 closed-test users (Google's 2023 policy for new devs)
- Real privacy policy URL (host as a separate page in the repo)
- Screenshots (2–8 phone screenshots, 1024×500 feature graphic, app icon)
- TWA-wrapped APK from [PWABuilder.com](https://www.pwabuilder.com) — paste the Pages URL, download generated APK + keystore
- Digital Asset Links file (`/.well-known/assetlinks.json`) on the Pages URL to verify TWA ownership
- Content rating questionnaire (~5 minutes)
- Target Android API 34 (PWABuilder handles automatically)

Total realistic timeline: 2–4 weeks for first-time devs. Cost: $25 + your time.

### 12.2 Apple App Store submission

Costs $99/year (Apple Developer Program). PWA Builder can wrap for iOS too but the App Store has notoriously stricter review. Not recommended unless you specifically need App Store distribution.

### 12.3 Additional techniques to add

- **Kapalabhati** (skull-shining breath) — short forceful exhales
- **Ujjayi** (ocean breath) — for yoga practice
- **Sitali / Sitkari** (cooling breaths)
- **Wim Hof method** — 30 deep breaths + retention
- **Coherent breathing** (5.5 breaths/min) — for HRV training

### 12.4 Visual / UX improvements

- Subtle particle effects on inhale/exhale (already in desktop session, could port to mobile)
- Statistics tracking (how many sessions you've done) — would require local storage on mobile, JSON file on desktop
- "Streak" tracker
- Customisable voice (let user pick Aria / Jenny / Neerja from a dropdown — would require generating multiple voice sets)
- Hindi voice variants for Indian users

### 12.5 Distribution

- Submit to alternate Android stores: F-Droid (FOSS-friendly), Aurora Store, Amazon Appstore
- Create installation video for YouTube → embed in INSTALL.md
- Wiki page on the GitHub repo with screenshots from real installs

---

## Appendix A — Complete Higgsfield prompts used

All eight prompts, exact text, for re-generation in the future. Style: cinematic, ambient, no people, no text in image.

### A.1 App icon (`z_image`, 1:1)

```
Minimalist app icon for a meditation breathing app. Centered design:
stylized lotus flower with concentric expanding breath ripples emerging
outward. Soft cyan and warm gold gradient on deep navy background. Clean
flat vector style, sacred geometry, glowing edges, subtle radial light.
No text, no letters. Centered composition, suitable for application icon
and shortcut.
```

### A.2 Home / aurora background — `bg_home.png` (`soul_location`, 16:9)

```
Serene cosmic aurora wellness app background. Deep navy and indigo sky
with soft cyan and violet ribbons of light flowing across. Subtle stars.
Minimal, calming, meditative atmosphere. No text, no letters, no people.
Cinematic depth, soft gradient, peaceful, suitable as full-screen
background for a breathing meditation app.
```

### A.3 Box Breathing / sacred geometry — `bg_box.png`

```
Sacred geometry meditation background, square mandala patterns nested
within each other, deep teal and cyan gradients on dark navy. Four-fold
symmetry representing equal-sided breath. Soft glowing edges, minimalist,
mystical, calming. No text, no people. Cinematic depth, suitable as
full-screen ambient background.
```

### A.4 4-7-8 / moonlit — `bg_478.png`

```
Serene moonlit night sky over still water. Soft indigo, deep purple, and
midnight blue gradient. Crescent moon glowing softly, gentle mist,
dreamlike atmosphere for sleep meditation. Minimal, dreamy, deeply
calming. No text, no people. Cinematic, suitable as full-screen ambient
background.
```

### A.5 Bhramari / honey sunset — `bg_bhramari.png`

```
Warm golden honey sunset with soft concentric sound wave ripples
radiating outward. Amber, bronze, and gold gradients on a deep horizon.
Tiny floating light particles like bees of light. Mystical, warm, deeply
soothing. No text, no people. Cinematic, suitable as full-screen ambient
background for humming meditation.
```

### A.6 Nadi Shodhana / two streams — `bg_nadi.png`

```
Two streams of energy flowing and merging in the center. Left side cool
blue and silver, right side warm orange and gold. Perfect yin-yang
balance, swirling currents meeting harmoniously. Deep cosmic background.
Symbolic of alternate-nostril breathing. Elegant, balanced, mystical.
No text, no people. Cinematic, full-screen background.
```

### A.7 Extended Exhale / dawn lake — `bg_extended.png`

```
Peaceful dawn over a still mountain lake, mist rising softly. Pale pink,
lavender, and soft blue gradient sky. Reflections in the calm water.
Open, expansive, releasing atmosphere symbolizing a long exhale.
Tranquil, fresh, infinitely calm. No text, no people. Cinematic,
full-screen background for breathwork app.
```

### A.8 Complete / mandala — `bg_complete.png`

```
Radiant golden mandala sunburst, sacred geometry, intricate symmetrical
patterns. Bright glowing center radiating outward with warm gold, amber,
and rose-gold light beams. Celebration, achievement, inner peace. Subtle
dark navy edges to frame the brilliance. No text, no people. Cinematic,
full-screen background for session completion celebration.
```

---

## Appendix B — Complete voice clip script

All 11 voice clips. Voice: **`en-US-AriaNeural`**, rate: **`-22%`**, pitch: **`-3Hz`**.

| File | Text spoken | Used in |
|---|---|---|
| `inhale.mp3` | "Breathe in." | Box, 4-7-8, Extended Exhale, Custom, Daily warm-up |
| `hold.mp3` | "Hold." | All routines with hold_in phase |
| `exhale.mp3` | "Breathe out." | Box, Extended Exhale, Custom, Daily |
| `hold_empty.mp3` | "Hold." | All routines with hold_out phase |
| `inhale_left.mp3` | "Inhale through the left nostril." | Nadi Shodhana, Nadi Shodhana Box |
| `inhale_right.mp3` | "Inhale through the right nostril." | Nadi Shodhana, Nadi Shodhana Box |
| `exhale_left.mp3` | "Exhale through the left nostril." | Nadi Shodhana, Nadi Shodhana Box |
| `exhale_right.mp3` | "Exhale through the right nostril." | Nadi Shodhana, Nadi Shodhana Box |
| `hum.mp3` | "Hum." | Bhramari (also triggers built-in harmonic hum tone) |
| `begin.mp3` | "Let's begin. Settle into your breath." | Played once at session start |
| `complete.mp3` | "Session complete. Notice the calm." | Played at session end |

---

## Appendix C — Repo file inventory

After everything is built and committed, the repo contains exactly these files (`python_portable/` lives only locally, recreated per machine by `build_portable.bat`):

```
box-breathing-studio/
├── .github/workflows/deploy-pages.yml    # 0.7 KB
├── .gitignore                            # 0.4 KB
├── LICENSE                               # 1.1 KB (MIT)
├── README.md                             # 4.9 KB (repo landing page)
├── INSTALL.md                            # 7.1 KB (newcomer guide)
├── MANUAL.md                             # this file
├── windows/                              ← 21 files, ~17 MB
│   ├── app.py                            # ~46 KB
│   ├── install_app.bat                   # 2.4 KB
│   ├── run_app.bat                       # 0.3 KB
│   ├── build_portable.bat                # 2.5 KB
│   ├── README.txt                        # 4.6 KB
│   └── assets/
│       ├── icon.png                      # 5.4 MB (2048x2048)
│       ├── icon.ico                      # 0.1 MB
│       ├── bg_478.png                    # 1.4 MB
│       ├── bg_bhramari.png               # 2.6 MB
│       ├── bg_box.png                    # 2.0 MB
│       ├── bg_complete.png               # 3.0 MB
│       ├── bg_extended.png               # 2.1 MB
│       ├── bg_home.png                   # 1.3 MB
│       ├── bg_nadi.png                   # 2.5 MB
│       └── voice/                        # 11 MP3s, 200 KB
└── mobile/                               ← 28 files, ~17 MB
    ├── index.html                        # 0.7 KB
    ├── app.js                            # 29.4 KB
    ├── styles.css                        # 10.1 KB
    ├── manifest.json                     # 0.7 KB
    ├── service-worker.js                 # 1.7 KB
    ├── README.txt                        # 6.3 KB
    ├── icons/
    │   ├── icon-192.png                  # 35 KB
    │   └── icon-512.png                  # 250 KB
    └── assets/
        ├── bg/                           # 7 backgrounds (same as desktop)
        └── voice/                        # 11 MP3s (same as desktop)

Total repo size committed: ~36 MB
After local build (windows/python_portable/ added): ~155 MB
```

---

## Appendix D — Glossary of pranayama terms

For anyone unfamiliar with the Sanskrit / yogic vocabulary used throughout.

| Term | Meaning |
|---|---|
| **Pranayama** | Sanskrit for "extension of life-force". The general yogic discipline of breath regulation. |
| **Sama Vritti** | "Equal flow". The classical name for Box Breathing — equal-length phases. |
| **Vishama Vritti** | "Unequal flow". Breathing with intentional asymmetry (e.g. 4-7-8). |
| **Puraka** | Inhalation. |
| **Kumbhaka** | Breath retention. Antara Kumbhaka = retention after inhale (full lungs). Bahya Kumbhaka = retention after exhale (empty lungs). |
| **Rechaka** | Exhalation. |
| **Nadi Shodhana** | "Channel purification". Alternate-nostril breathing — purifies the energy channels (nadis). |
| **Bhramari** | "Bee". Humming breath — the exhale hum vibration calms the nervous system. |
| **Ujjayi** | "Victorious". Ocean breath — slight glottal constriction creates a soft hissing sound. |
| **Chin Mudra** | Hand gesture — index finger and thumb lightly touching, palms up on knees. Common pranayama seal. |
| **Vishnu Mudra** | Hand gesture for Nadi Shodhana — fold index and middle fingers; use thumb to close right nostril, ring + pinky to close left. |
| **Sukhasana** | "Easy pose". Cross-legged seated posture. |
| **Siddhasana** | "Accomplished pose". Stricter cross-legged posture with one heel against the perineum. |
| **Ajna** | The "third eye" energy center between the brows. Often the focal point for breath awareness. |
| **HRV** | Heart Rate Variability — the variation in beat-to-beat timing of the heart. Higher HRV = better autonomic balance. |
| **Vagal tone** | Activity of the vagus nerve (parasympathetic). Slow exhales raise vagal tone, which lowers heart rate and induces calm. |

---

## End of manual

**Total document size**: ~40 KB · ~12,000 words · ~25-30 printed pages depending on layout.

This document is committed to the repo alongside the code. To export as PDF:

1. Open this file on GitHub: `https://github.com/tarunabhdutta/box-breathing-studio/blob/main/MANUAL.md`
2. Use any browser → File → Print → Save as PDF
3. Or copy the raw markdown into [Dillinger](https://dillinger.io) or [StackEdit](https://stackedit.io) and export as PDF directly

For local offline reference, the markdown file itself is fully self-contained — no images embedded that need to be downloaded separately. Future-you can open `MANUAL.md` in any text editor and reconstruct the entire project.

---

**Last updated**: 2026-05-21 · **Maintainer**: Tarunabh Dutta
**License**: MIT (same as the project itself)
**Repo**: [github.com/tarunabhdutta/box-breathing-studio](https://github.com/tarunabhdutta/box-breathing-studio)
