Box Breathing Studio  -  v2.0
Developed by Tarunabh Dutta
TD Film Studio  ·  Guwahati, India

A full-screen immersive desktop breathwork app for sleep, stress,
anxiety, elevated heart rate, and the wear-and-tear of long
sedentary work days.


Quick start
-----------
This folder is a complete, fully offline, portable app.  No Python
needs to be installed on the target PC.  No internet is required.

1. Double-click  install_app.bat   (one-time)
   - Verifies the bundled Python is present
   - Adds a "Box Breathing" shortcut to your Desktop and Start Menu

2. From then on, launch the app any of these ways:
   - Click the "Box Breathing" Desktop shortcut
   - Start menu  ->  Box Breathing
   - Double-click  run_app.bat

The whole installation lives inside this folder.  Delete the
folder to uninstall - nothing else on your machine is touched.


What's inside the app
---------------------
Smart Wizard         3-question check-in picks the right routine
                     (stress, hours sat, sleep quality, time of day)
Box Breathing        Sama Vritti  4-4-4-4   (Beginner / Intermediate / Advanced)
4-7-8                Dr Weil's sleep & panic-reset breath
Bhramari             Humming Bee Breath - with built-in hum tone
Nadi Shodhana        Two-round alternate-nostril (Left-Right then Right-Left)
Nadi Shodhana Box    Classical alternation with 4-4-4-4 holds.
                     One cycle alternates BOTH sides through inhale + exhale:
                       Inhale LEFT  -> Hold -> Exhale RIGHT -> Hold empty
                       Inhale RIGHT -> Hold -> Exhale LEFT  -> Hold empty
                     Repeated 7 times (~3:45 minutes).
Extended Exhale      4 in / 6 out  - pure parasympathetic
15-min Daily         Full integrated five-block sequence
Custom Builder       Build your own ratio (1-12 sec per phase, 3-30 cycles)


Voice guidance
--------------
A calm female voice (Microsoft Edge "Aria Neural", slowed for meditation)
guides you through every phase:
  - "Breathe in"  "Hold"  "Breathe out"  "Hold"     (generic)
  - "Inhale through the left nostril"  etc.         (Nadi Shodhana)
  - "Hum"                                            (Bhramari)
  - "Let's begin. Settle into your breath."         (session start)
  - "Session complete. Notice the calm."            (session end)

Voice is ON by default.  Toggle it on the bottom bar of the Home screen.
Sine-wave tones still play softly underneath so you have timing cues
even when voice is muted.


Look and feel
-------------
- Full-screen immersive layout (ESC to exit, SPACE to pause/resume)
- Smooth animated breathing orb that scales with phase progress
- Soft particle effects drifting inward on inhale, outward on exhale
- Higgsfield-generated ambient backgrounds per technique:
    bg_home       Aurora Ridge       (cosmic, home menu)
    bg_box        Azure Mindfulness  (sacred geometry)
    bg_478        Crescent Bay       (moonlit night)
    bg_bhramari   Sunset Sound       (golden honey)
    bg_nadi       Nadi Sangam        (two streams merging)
    bg_extended   Lac de l'Aube      (peaceful dawn)
    bg_complete   Surya Mandir       (golden mandala)


Audio
-----
Soft sine-wave tones mark each phase transition, different pitch per phase:
  - low warm tone  = inhale
  - mid tone       = hold (full)
  - lower tone     = exhale
  - lowest tone    = hold (empty)
  - bell tone      = session complete
Bhramari adds a low harmonic hum during the exhale.
Adjust the master volume on the home screen.


Keyboard shortcuts
------------------
ESC      Exit / back to home
SPACE    Pause / Resume current session


Contraindications
-----------------
- High blood pressure: skip the post-inhale hold. Use Extended Exhale
  (4-0-6-0) or Custom Builder with Hold In = 0.
- Pregnancy: avoid breath retention.
- Dizziness: stop and breathe normally.  You may be over-retaining.


Requirements
------------
- Windows 10 or 11 (64-bit)
- About 150 MB free disk space
- That's it.  No Python, no internet, no admin rights needed.


Folder contents
---------------
install_app.bat        one-click installer (creates shortcuts only)
run_app.bat            launcher used by the Desktop shortcut
app.py                 the application
assets/                visuals + app icon + voice clips
  voice/               11 narration clips (.mp3)
python_portable/       bundled Python 3.11.9 + numpy + pygame
README.txt             this file


Credits
-------
Developed by:        Tarunabh Dutta
Studio:              TD Film Studio, Guwahati
Built with:          pygame, numpy
Visuals generated:   Higgsfield AI (soul_location + z_image)
Voice generated:     Microsoft Edge TTS (en-US-AriaNeural, slowed)

(c) 2026 Tarunabh Dutta.  Personal use.
