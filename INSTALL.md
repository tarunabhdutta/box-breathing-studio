# How to install Box Breathing Studio

> A simple meditation app for sleep, stress, anxiety, and long workdays.
> **Free. No ads. No signup. Works offline.**

Pick your device below. Both versions are the same app — same voice, same visuals, same nine guided routines.

📱 **[I have an Android phone](#-android--3-taps-to-install)**
🍎 **[I have an iPhone](#-iphone--3-taps-to-install)**
🪟 **[I have a Windows PC](#-windows-pc--5-minute-setup)**

---

## 📱 Android — 3 taps to install

You don't need the Play Store. The app installs directly from your browser in less than a minute.

### Step 1 — Open the link in Chrome

On your phone, open **Chrome** and visit:

> ### 👉 [tarunabhdutta.github.io/box-breathing-studio](https://tarunabhdutta.github.io/box-breathing-studio/)

You'll see a deep navy welcome screen with a lotus icon and the text "Box Breathing Studio · Created by Tarunabh Dutta".

### Step 2 — Wait 5 seconds, then tap any tile

Tap any breathing technique (e.g. "Box Breathing") and let it run for 5 seconds. Then tap **End session** to go back. *(This step "wakes up" Chrome's Install option — it only appears once Chrome sees you've actually interacted with the page.)*

### Step 3 — Tap "Install" or "Add to home screen"

1. Tap the **three dots** (⋮) in the top-right of Chrome.
2. Scroll the menu until you find **"Install app"** OR **"Add to home screen"**. *(Both mean the same thing — the wording depends on your Chrome version.)*
3. Tap it. A small dialog appears — tap **"Install"** or **"Add"**.

✅ **Done.** A lotus icon labelled "Box Breath" now sits on your home screen. Tap it to launch — the app opens full-screen with no browser bars, like any other app you've downloaded.

### How to know it installed correctly

- ✅ Tapping the home-screen icon opens it **full-screen** with no Chrome address bar at the top.
- ❌ If you see Chrome's address bar at the top, it installed as a bookmark by mistake. Long-press the icon → remove from home screen → redo Step 2 (interacting with a tile is what triggers the *real* install instead of the bookmark).

### Will it work without internet?

**Yes — fully offline once installed.** The first time you open it, all the voice clips and background images cache to your phone (~16 MB). After that you can turn off WiFi, switch on aeroplane mode, anything — the app keeps working. No data is sent anywhere. Ever.

---

## 🍎 iPhone — 3 taps to install

### Step 1 — Open the link in Safari (not Chrome)

On iPhone, **Safari is required** — Chrome on iOS doesn't support PWA install. Open Safari and visit:

> ### 👉 [tarunabhdutta.github.io/box-breathing-studio](https://tarunabhdutta.github.io/box-breathing-studio/)

### Step 2 — Tap the Share button

At the bottom of Safari, tap the **Share icon** (the square with an arrow pointing up).

### Step 3 — Scroll down and tap "Add to Home Screen"

In the share sheet, scroll the options until you see **"Add to Home Screen"**. Tap it, then tap **"Add"** in the top right.

✅ Done. The icon appears on your home screen. Tap to launch.

> **Note:** iOS supports PWAs but with slightly fewer features than Android. Voice and visuals work fully. Offline support works after first visit.

---

## 🪟 Windows PC — 5 minute setup

The Windows version is the most immersive — full-screen, smooth animations, slightly more detailed visuals than the mobile version.

### Easiest path — download the ready-made ZIP

1. Go to the **[Releases page](https://github.com/tarunabhdutta/box-breathing-studio/releases/latest)** of this repo.
2. Under "Assets", download **`BoxBreathingApp-windows.zip`** (~140 MB).
3. **Right-click the ZIP → Extract All** to any folder you like (Desktop, Documents, anywhere).
4. Open the extracted folder and double-click **`install_app.bat`**.
5. A console window appears for ~5 seconds, then closes. A **"Box Breathing"** shortcut now sits on your Desktop.
6. Double-click the shortcut to launch.

### Will it ask for admin access? Install anything weird?

**No.** Everything lives inside the folder you extracted. The installer just creates a Desktop shortcut and a Start Menu entry. To uninstall: delete the folder. Nothing is registered with Windows. Nothing is added to PATH. No drivers, no admin prompts, no antivirus warnings (it's just Python + sounds + images).

### What if Windows Defender / SmartScreen warns me?

That's normal for any unsigned `.bat` file — Microsoft only stops warning once an app has been downloaded thousands of times by other users. If you trust the source (this GitHub repo), click **"More info"** → **"Run anyway"**. You can verify safety by reading [`windows/app.py`](windows/app.py) directly on GitHub before downloading — it's plain Python source, ~1500 lines, no obfuscation, MIT-licensed.

### Advanced — build from source

If you'd rather build from the GitHub source instead of downloading the ZIP, see the [main README](README.md#-windows-desktop--install-on-your-pc).

---

## ❓ Frequently asked

**Is this really free?** Yes. MIT-licensed, no ads, no signup, no tracking, no data sent anywhere. Made by a filmmaker in Guwahati who built it for his own daily practice and decided to share.

**What does the app actually do?** It guides you through nine different breathing techniques used in pranayama and modern breathwork research — Box Breathing, 4-7-8, Bhramari (humming), Nadi Shodhana (alternate-nostril), and more. A calm voice tells you when to inhale, hold, exhale; a soft animated circle expands and contracts in sync; sine-wave tones mark each phase. There's also a 3-question Smart Wizard that picks the best routine for you based on how stressed/tired you currently feel.

**Why these techniques specifically?** They're backed by clinical research on heart-rate variability, parasympathetic activation, vagal tone, and sleep quality. Useful for: getting to sleep, calming panic, lowering anxiety, releasing the tension that builds during long sedentary workdays.

**Will it drain my battery?** Minimal — the animation is lightweight CSS, the audio is short cues, the screen stays on only during active sessions. About the same battery usage as reading an article.

**Can I share it?** Yes please. Forward this link to anyone:

> **[github.com/tarunabhdutta/box-breathing-studio](https://github.com/tarunabhdutta/box-breathing-studio)**

**Found a bug? Want a new feature?** Open an issue on GitHub or DM me on social media.

---

## ⚠️ Safety / contraindications

Breathwork is generally very safe, but please read these once:

- **High blood pressure** — skip the post-inhale hold. Use *Extended Exhale* or *Custom Builder* with Hold In = 0.
- **Pregnancy** — avoid breath retention. Stick to Extended Exhale.
- **If you ever feel lightheaded** — stop, breathe normally, sit down. You may be over-retaining.
- This is a personal-practice tool, not medical treatment. If you have a respiratory condition or anxiety disorder, run it past your doctor first.

---

## Credits

**Developed by:** Tarunabh Dutta · TD Film Studio, Guwahati 🇮🇳
**Visuals:** Generated with Higgsfield AI
**Voice:** Microsoft Edge Neural TTS (Aria, slowed for meditation)
**License:** MIT

© 2026 Tarunabh Dutta
