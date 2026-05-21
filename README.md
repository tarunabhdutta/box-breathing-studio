# Box Breathing Studio

> Guided pranayama and breathwork for sleep, stress, anxiety, elevated heart rate, and the wear-and-tear of long sedentary work days.

A free, fully offline meditation app shipped in two flavours:

- **🪟 Windows desktop** — full-screen immersive Pygame app
- **📱 Mobile PWA** — installable on Android (and iOS) via Chrome

Developed by **Tarunabh Dutta** · TD Film Studio, Guwahati 🇮🇳

---

## Features

Nine guided routines, all with calm voice narration:

| Routine | What it does | Best for |
|---|---|---|
| **Smart Wizard** | 3-question check-in → picks the right routine for right now | Don't know what you need |
| **Box Breathing** | Sama Vritti, 4-4-4-4 — three difficulty levels | Focus, daily practice |
| **4-7-8** | Dr Weil's calming breath | Sleep, panic-reset |
| **Bhramari** | Humming Bee Breath with built-in hum tone | Anxiety, mental noise |
| **Nadi Shodhana** | Two-round alternate-nostril breathing | Nervous-system balance |
| **Nadi Shodhana Box** | Classical 8-phase alternation with 4-4-4-4 holds | Deep practice |
| **Extended Exhale** | 4 in / 6 out — pure parasympathetic | Wind-down |
| **15-min Daily** | Full integrated five-block sequence | Daily ritual |
| **Custom Builder** | Roll your own ratio (1–12s per phase) | Personalised practice |

Every phase is guided by a calm female voice (*Microsoft Aria Neural*, slowed −22 % for meditation) and a soft sine-wave tone. The ambient backgrounds were generated with **Higgsfield AI** — each technique gets its own mood (Aurora Ridge, Azure Mindfulness Studio, Crescent Bay, Sunset Sound, Nadi Sangam, Lac de l'Aube, Surya Mandir).

---

## 📱 Mobile (PWA) — install on your phone

The mobile version is hosted by GitHub Pages. **No app store needed.**

1. On your phone, open Chrome.
2. Visit: **`https://tarunabhdutta.github.io/box-breathing-studio/`**
3. Chrome menu (⋮) → **Install app** (or "Add to home screen")
4. The lotus icon appears on your home screen — tap to launch full-screen.

Works fully offline after the first install. The app is ~16 MB and caches itself onto your phone the first time you open it.

[👉 Full mobile install guide and troubleshooting](mobile/README.txt)

---

## 🪟 Windows desktop — install on your PC

The desktop version is more immersive — uses your whole screen, smoother animations, the same voice and visuals.

### Quick install (3 steps)

1. Download the **`BoxBreathingApp-windows.zip`** from the [Releases page](../../releases/latest).
2. Unzip anywhere — the folder is fully self-contained (no system Python required).
3. Double-click **`install_app.bat`** — creates a Desktop shortcut.

### Or build it yourself from source

If you cloned the repo, the bundled Python runtime is not included (it's 130 MB and gitignored). To rebuild it:

```cmd
cd windows
build_portable.bat       :: downloads Python 3.11.9 + numpy + pygame (~3 min)
install_app.bat          :: creates Desktop + Start Menu shortcuts
```

Requires: Windows 10/11 (64-bit), ~250 MB disk, internet on first run only.

[👉 Full Windows install guide](windows/README.txt)

---

## 🧘 Contraindications

- **High blood pressure** — skip the post-inhale hold. Use Extended Exhale or Custom Builder with Hold In = 0.
- **Pregnancy** — avoid breath retention.
- **Dizziness** during practice — stop and breathe normally. You may be over-retaining.

---

## Repo layout

```
box-breathing-studio/
├── README.md                  ← you are here
├── LICENSE                    MIT
├── .gitignore
├── .github/workflows/
│   └── deploy-pages.yml       auto-deploys mobile/ to GitHub Pages
├── windows/                   Windows desktop app (Python + Pygame)
│   ├── app.py
│   ├── install_app.bat
│   ├── run_app.bat
│   ├── build_portable.bat     rebuilds python_portable/ from scratch
│   ├── README.txt
│   └── assets/                backgrounds, icon, voice clips
└── mobile/                    Installable PWA (HTML + CSS + JS)
    ├── index.html
    ├── app.js
    ├── styles.css
    ├── manifest.json
    ├── service-worker.js
    ├── README.txt
    ├── icons/
    └── assets/                same backgrounds + voice clips
```

---

## Credits

- **Visuals**: Higgsfield AI (`soul_location` for backgrounds, `z_image` for the lotus icon)
- **Voice**: Microsoft Edge TTS (`en-US-AriaNeural`, slowed for meditation)
- **Built with**: Python · Pygame · NumPy (desktop) — Vanilla JS · Web Audio API (mobile)

---

## License

MIT — see [LICENSE](LICENSE).

© 2026 Tarunabh Dutta
