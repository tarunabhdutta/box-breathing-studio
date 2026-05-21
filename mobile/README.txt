Box Breathing Studio — Mobile (PWA)
====================================
Developed by Tarunabh Dutta
TD Film Studio · Guwahati, India

A touch-native version of the desktop app, packaged as a Progressive
Web App.  Once installed on Android, it lives on your home screen as
a real icon, opens full-screen with no browser chrome, and works
fully offline — the same 8 backgrounds and 11 voice clips are baked
in to the install.

----------------------------------------------------------------
INSTALL ON YOUR ANDROID PHONE  (about 3 minutes)
----------------------------------------------------------------

You need to host the folder somewhere your phone can reach it.
A "Progressive Web App" must be served over HTTP/HTTPS — opening
the HTML file directly via "file://" will work but the offline cache
and Install prompt do NOT activate from file URLs.

The simplest options are below.  Pick ONE.

OPTION 1 — Quick local network (you and your phone on the same WiFi)
.....................................................................
This is the fastest way.  Your phone and PC must be on the same WiFi.

1. On the PC, open PowerShell in the BoxBreathingMobile folder and
   run:

       py -m http.server 8000

   (or  python -m http.server 8000  )

   You'll see "Serving HTTP on 0.0.0.0 port 8000".

2. Find your PC's local IP.  In PowerShell:

       ipconfig | findstr IPv4

   Look for something like  192.168.1.42

3. On your phone, open Chrome and visit:

       http://192.168.1.42:8000

   (use your actual IP)

4. Chrome will show "Add to Home screen" or "Install" in the menu
   (three dots, top right).  Tap it.

5. The "Box Breath" icon appears on your home screen.  Tap it.

   Note: once installed, the app keeps working OFFLINE — you can
   turn off WiFi or shut down the PC.  All assets are cached on
   the phone the first time you open it.


OPTION 2 — Free static host (works from anywhere, no PC needed later)
.....................................................................

1. Go to  https://app.netlify.com/drop  in any browser.

2. Drag the entire BoxBreathingMobile folder onto the drop zone.

3. Netlify gives you a unique URL like
       https://wonderful-cake-12345.netlify.app

4. Open that URL on your phone in Chrome → menu → Install.

5. Done.  No PC needed afterwards.  The icon on your home screen
   loads the app instantly and works offline.


OPTION 3 — Copy folder directly to phone (less convenient)
.....................................................................
This won't give you the "Install" prompt because Chrome restricts
PWA features on file:// URLs.  The app will still work as a web page
but won't install to home screen and won't cache offline.  Only use
this if Options 1 and 2 aren't possible.

1. Copy the entire BoxBreathingMobile folder to your phone
   (e.g. via USB cable, Google Drive, or any file-transfer app).

2. On the phone, open a file manager → navigate into the folder →
   tap index.html → open in Chrome.

----------------------------------------------------------------
WHAT YOU GET ON THE PHONE
----------------------------------------------------------------

All 8 routines from the desktop app:

  Smart Wizard          3-question check-in
  Box Breathing         Sama Vritti 4-4-4-4
  4-7-8                 Dr Weil's sleep / panic-reset
  Bhramari              Humming Bee Breath
  Nadi Shodhana         Two-round alternate-nostril
  Nadi Shodhana Box     Classical alternation with 4-4-4-4 holds
                        (the new variant — 8 phases per cycle)
  Extended Exhale       4 in / 6 out
  15-min Daily          Full integrated sequence
  Custom Builder        Roll your own ratio

Voice:
  - Same 11 calm Aria Neural voice clips as the desktop app.
  - "Voice" toggle on the bottom bar to mute/unmute.
  - Sine-wave tones play softly underneath.

Visuals:
  - Same Higgsfield ambient backgrounds per technique.
  - Animated breathing orb that scales smoothly with each phase
    (CSS transforms, 60 fps on modern phones).

Mobile-specific niceties:
  - Full-screen "standalone" mode once installed (no browser bars).
  - Screen Wake Lock during sessions so the phone doesn't dim out.
  - Hardware Back button returns to Home screen instead of closing.
  - Works in airplane mode after first install.

----------------------------------------------------------------
TROUBLESHOOTING
----------------------------------------------------------------

"No Install prompt appears in Chrome"
  - Make sure you reached the page via http:// or https://
    (not file://).  Use Option 1 or 2 above.
  - Chrome needs you to interact with the page for a moment
    before the prompt becomes available — tap anywhere first.
  - If you're using Firefox: tap menu → "Install" instead.

"Audio doesn't play on first tap"
  - Mobile browsers require a user gesture before audio plays.
    Just tap any tile once — audio unlocks for the rest of the
    session.

"It's silent during sessions"
  - Check the Voice toggle and the volume slider on the home
    screen.  Also check your phone is not on silent / DND.

"Want to uninstall"
  - Long-press the home-screen icon → Uninstall (or "Remove from
    home screen", depending on launcher).

----------------------------------------------------------------
FILES IN THIS FOLDER
----------------------------------------------------------------
index.html           shell HTML
styles.css           mobile-first dark theme
app.js               all routines, wizard, audio engine, scenes
manifest.json        makes the page installable
service-worker.js    caches everything for offline use
icons/               192px + 512px home-screen icons
assets/bg/           7 ambient backgrounds (PNG)
assets/voice/        11 narration clips (MP3)
README.txt           this file

Total bundle size: ~21 MB (mostly the backgrounds and voice clips).
The PWA cache stores everything once; subsequent launches are instant.

----------------------------------------------------------------
CREDITS
----------------------------------------------------------------
Developed by:        Tarunabh Dutta
Studio:              TD Film Studio, Guwahati
Visuals generated:   Higgsfield AI (soul_location + z_image)
Voice generated:     Microsoft Edge TTS (en-US-AriaNeural)
Built with:          Vanilla HTML / CSS / JavaScript

© 2026 Tarunabh Dutta.  Personal use.
