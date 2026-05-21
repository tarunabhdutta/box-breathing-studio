/* ============================================================
   Box Breathing Studio — mobile PWA
   Developed by Tarunabh Dutta
   TD Film Studio · Guwahati
   ============================================================ */

"use strict";

const DEVELOPER = "Tarunabh Dutta";
const APP_NAME = "Box Breathing Studio";
const VERSION = "2.1";

// ============================================================
// AUDIO ENGINE
// ============================================================

const PHASE_TONES = {
  inhale:   { freq: 220, dur: 0.40 },
  hold_in:  { freq: 330, dur: 0.25 },
  exhale:   { freq: 165, dur: 0.50 },
  hold_out: { freq: 110, dur: 0.25 },
  complete: { freq: 440, dur: 0.70 },
};

const VOICE_KEYS = [
  "inhale", "hold", "exhale", "hold_empty",
  "inhale_left", "inhale_right", "exhale_left", "exhale_right",
  "hum", "begin", "complete",
];

class AudioEngine {
  constructor() {
    this.volume = 0.8;
    this.voiceOn = true;
    this.ctx = null;
    this.voices = {};       // key -> HTMLAudioElement (preloaded)
    this._currentVoice = null;
    this._humOscs = [];
  }

  // Must be called from a user gesture for autoplay to work.
  async init() {
    if (this.ctx) return;
    const Ctx = window.AudioContext || window.webkitAudioContext;
    this.ctx = new Ctx();
    for (const k of VOICE_KEYS) {
      const a = new Audio(`assets/voice/${k}.mp3`);
      a.preload = "auto";
      this.voices[k] = a;
    }
  }

  resume() {
    if (this.ctx && this.ctx.state === "suspended") this.ctx.resume();
  }

  playTone(name) {
    if (!this.ctx) return;
    const t = PHASE_TONES[name];
    if (!t) return;
    const now = this.ctx.currentTime;
    const dur = t.dur;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = "sine";
    osc.frequency.value = t.freq;
    osc.connect(gain).connect(this.ctx.destination);
    const peak = this.volume * 0.18 * 0.55; // softer when voice is on top
    gain.gain.setValueAtTime(0, now);
    gain.gain.linearRampToValueAtTime(peak, now + 0.04);
    gain.gain.setValueAtTime(peak, now + dur - 0.04);
    gain.gain.linearRampToValueAtTime(0, now + dur);
    osc.start(now);
    osc.stop(now + dur);
  }

  playVoice(key) {
    if (!this.voiceOn || !key) return;
    const a = this.voices[key];
    if (!a) return;
    if (this._currentVoice && !this._currentVoice.paused) {
      try { this._currentVoice.pause(); } catch (e) {}
      this._currentVoice.currentTime = 0;
    }
    try {
      a.currentTime = 0;
      a.volume = Math.min(1, this.volume * 1.0);
      a.play().catch(() => {});
      this._currentVoice = a;
    } catch (e) {}
  }

  stopVoice() {
    if (this._currentVoice && !this._currentVoice.paused) {
      try { this._currentVoice.pause(); this._currentVoice.currentTime = 0; } catch (e) {}
    }
  }

  playHum(duration) {
    if (!this.ctx) return;
    this.stopHum();
    const dur = Math.max(0.5, Math.min(12, duration));
    const now = this.ctx.currentTime;
    const master = this.ctx.createGain();
    master.connect(this.ctx.destination);
    const peak = this.volume * 0.22;
    master.gain.setValueAtTime(0, now);
    master.gain.linearRampToValueAtTime(peak, now + 0.18);
    master.gain.setValueAtTime(peak, now + dur - 0.18);
    master.gain.linearRampToValueAtTime(0, now + dur);
    const partials = [[130, 0.6], [260, 0.25], [390, 0.10]];
    for (const [f, mix] of partials) {
      const o = this.ctx.createOscillator();
      const g = this.ctx.createGain();
      o.type = "sine";
      o.frequency.value = f;
      g.gain.value = mix;
      o.connect(g).connect(master);
      o.start(now);
      o.stop(now + dur);
      this._humOscs.push(o);
    }
    setTimeout(() => { this._humOscs = []; }, (dur + 0.1) * 1000);
  }

  stopHum() {
    for (const o of this._humOscs) {
      try { o.stop(); } catch (e) {}
    }
    this._humOscs = [];
  }

  setVolume(v) { this.volume = Math.max(0, Math.min(1, v)); }

  toggleVoice() {
    this.voiceOn = !this.voiceOn;
    if (!this.voiceOn) this.stopVoice();
    return this.voiceOn;
  }
}

// ============================================================
// ROUTINES
// ============================================================

function defaultVoice(name, hum) {
  if (name === "inhale") return "inhale";
  if (name === "hold_in") return "hold";
  if (name === "exhale") return hum ? "hum" : "exhale";
  if (name === "hold_out") return "hold_empty";
  return null;
}

function phaseOf(name, seconds, label, voice, hum = false) {
  return {
    name, seconds, label,
    voice: voice ?? defaultVoice(name, hum),
    hum: !!hum,
  };
}

function makePhases(ratio, cues, opts) {
  cues = cues || {};
  opts = opts || {};
  const vk = opts.voiceKeys || {};
  const hum = !!opts.hum;
  const [inh, hin, exh, hout] = ratio;
  const out = [];
  if (inh > 0) out.push(phaseOf("inhale", inh, cues.inhale || "Inhale",
                                vk.inhale, false));
  if (hin > 0) out.push(phaseOf("hold_in", hin, cues.hold_in || "Hold",
                                vk.hold_in, false));
  if (exh > 0) out.push(phaseOf("exhale", exh, cues.exhale || "Exhale",
                                vk.exhale ?? (hum ? "hum" : "exhale"), hum));
  if (hout > 0) out.push(phaseOf("hold_out", hout, cues.hold_out || "Hold empty",
                                 vk.hold_out, false));
  return out;
}

function blockOf(title, subtitle, cycles, phases, note, bg) {
  return { title, subtitle, cycles, phases, note: note || "", bg: bg || "bg_box" };
}

function routineBox(level) {
  level = level || "intermediate";
  const n = { beginner: 3, intermediate: 4, advanced: 6 }[level];
  const cap = level[0].toUpperCase() + level.slice(1);
  return {
    title: `Box Breathing — ${cap}`,
    description: `Sama Vritti · ${n}-${n}-${n}-${n}`,
    bg: "bg_box",
    blocks: [
      blockOf("Box Breathing", "Sama Vritti", 10, makePhases([n, n, n, n]),
              "Sit upright. Chin mudra. Nasal breath only.", "bg_box"),
    ],
  };
}

function routine478() {
  return {
    title: "4-7-8 Breathing",
    description: "Dr Weil's calming breath · long exhale = vagal brake",
    bg: "bg_478",
    blocks: [
      blockOf("4-7-8", "Sleep & panic-reset", 8, makePhases([4, 7, 8, 0]),
              "Exhale through pursed lips with a soft 'whoosh'.", "bg_478"),
    ],
  };
}

function routineBhramari() {
  return {
    title: "Bhramari Pranayama",
    description: "Humming Bee Breath · vibration soothes the brain",
    bg: "bg_bhramari",
    blocks: [
      blockOf("Bhramari", "Hum on every exhale", 7,
              makePhases([4, 0, 8, 0], null, { hum: true }),
              "Close ears with index fingers. Hum 'mmm' through full exhale.",
              "bg_bhramari"),
    ],
  };
}

function routineNadi() {
  const left  = { inhale: "Inhale LEFT", hold_in: "Hold",
                  exhale: "Exhale RIGHT", hold_out: "Hold" };
  const right = { inhale: "Inhale RIGHT", hold_in: "Hold",
                  exhale: "Exhale LEFT", hold_out: "Hold" };
  const vleft  = { inhale: "inhale_left",  hold_in: "hold",
                   exhale: "exhale_right", hold_out: "hold_empty" };
  const vright = { inhale: "inhale_right", hold_in: "hold",
                   exhale: "exhale_left",  hold_out: "hold_empty" };
  return {
    title: "Nadi Shodhana",
    description: "Alternate-nostril · Vishnu Mudra",
    bg: "bg_nadi",
    blocks: [
      blockOf("Left → Right", "Round A", 5,
              makePhases([4, 4, 4, 4], left, { voiceKeys: vleft }),
              "Right thumb closes right nostril. Inhale left, exhale right.",
              "bg_nadi"),
      blockOf("Right → Left", "Round B", 5,
              makePhases([4, 4, 4, 4], right, { voiceKeys: vright }),
              "Ring + pinky close left nostril. Inhale right, exhale left.",
              "bg_nadi"),
    ],
  };
}

function routineNadiBox() {
  // Classical alternation: each cycle goes through BOTH sides
  // (Inhale L, Hold, Exhale R, Hold, Inhale R, Hold, Exhale L, Hold).
  const phases = [
    phaseOf("inhale",   4, "Inhale LEFT",  "inhale_left"),
    phaseOf("hold_in",  4, "Hold",         "hold"),
    phaseOf("exhale",   4, "Exhale RIGHT", "exhale_right"),
    phaseOf("hold_out", 4, "Hold empty",   "hold_empty"),
    phaseOf("inhale",   4, "Inhale RIGHT", "inhale_right"),
    phaseOf("hold_in",  4, "Hold",         "hold"),
    phaseOf("exhale",   4, "Exhale LEFT",  "exhale_left"),
    phaseOf("hold_out", 4, "Hold empty",   "hold_empty"),
  ];
  return {
    title: "Nadi Shodhana Box",
    description: "Classical alternation · 4-4-4-4 holds",
    bg: "bg_nadi",
    blocks: [
      blockOf("Full alternation", "8-phase cycle", 7, phases,
              "Vishnu Mudra. Switch nostrils on every breath. " +
              "One cycle takes both sides through inhale and exhale.",
              "bg_nadi"),
    ],
  };
}

function routineExtendedExhale() {
  return {
    title: "Extended Exhale 4:6",
    description: "Inhale 4, exhale 6 · pure parasympathetic",
    bg: "bg_extended",
    blocks: [
      blockOf("Extended Exhale", "4 in / 6 out", 12, makePhases([4, 0, 6, 0]),
              "No retention. Long smooth exhale through the nose.",
              "bg_extended"),
    ],
  };
}

function routineDaily15() {
  return {
    title: "15-Minute Daily Sequence",
    description: "Warm-up → Box → Nadi Shodhana → Bhramari → Integration",
    bg: "bg_home",
    blocks: [
      blockOf("Warm-up", "Diaphragmatic breathing", 8, makePhases([4, 0, 4, 0]),
              "Lying or seated. One hand on belly.", "bg_extended"),
      blockOf("Box Breathing", "Sama Vritti core", 10, makePhases([4, 4, 4, 4]),
              "Spine long. Chin mudra.", "bg_box"),
      blockOf("Nadi Shodhana", "Alt-nostril (left start)", 5,
              makePhases([4, 4, 4, 4],
                { inhale: "Inhale LEFT", hold_in: "Hold",
                  exhale: "Exhale RIGHT", hold_out: "Hold" },
                { voiceKeys: { inhale: "inhale_left", hold_in: "hold",
                               exhale: "exhale_right", hold_out: "hold_empty" } }),
              "Inhale left, exhale right.", "bg_nadi"),
      blockOf("Bhramari", "Humming Bee Breath", 5,
              makePhases([4, 0, 8, 0], null, { hum: true }),
              "Hum on every exhale.", "bg_bhramari"),
      blockOf("Integration", "Natural breath awareness", 6,
              makePhases([4, 0, 6, 0]),
              "Eyes closed. Let the breath find its own rhythm.",
              "bg_extended"),
    ],
  };
}

function routineCustom(inh, hin, exh, hout, cycles) {
  return {
    title: `Custom — ${inh}-${hin}-${exh}-${hout}`,
    description: `Your own ratio · ${cycles} cycles`,
    bg: "bg_home",
    blocks: [
      blockOf("Custom Breath", "Your ratio", cycles,
              makePhases([inh, hin, exh, hout]), "", "bg_box"),
    ],
  };
}

// ============================================================
// SMART WIZARD
// ============================================================

function pickRoutine(stress, hoursSat, sleep, hour) {
  if (sleep === "poor" || (hour >= 21 && stress >= 3)) {
    return {
      title: "Sleep Reset",
      description: "Wind down: Extended Exhale → 4-7-8 → Bhramari",
      bg: "bg_478",
      blocks: [
        ...routineExtendedExhale().blocks,
        ...routine478().blocks,
        ...routineBhramari().blocks,
      ],
    };
  }
  if (stress >= 4) {
    return {
      title: "Acute Stress Reset",
      description: "Box + Nadi Shodhana for nervous-system reset",
      bg: "bg_nadi",
      blocks: [
        ...routineBox("intermediate").blocks,
        ...routineNadi().blocks,
      ],
    };
  }
  if (hoursSat >= 10) {
    return {
      title: "Long-Sitting Reset",
      description: "Box → Extended Exhale → Bhramari",
      bg: "bg_box",
      blocks: [
        ...routineBox("intermediate").blocks,
        ...routineExtendedExhale().blocks,
        ...routineBhramari().blocks,
      ],
    };
  }
  if (hour < 11) {
    return {
      title: "Morning Box",
      description: "Energising start: Box, 10 cycles",
      bg: "bg_box",
      blocks: routineBox("intermediate").blocks,
    };
  }
  return routineDaily15();
}

// ============================================================
// VIEW UTILITIES
// ============================================================

const $app = document.getElementById("app");
function el(tag, props, ...children) {
  const e = document.createElement(tag);
  for (const k in props) {
    if (k === "class")          e.className = props[k];
    else if (k === "style")     Object.assign(e.style, props[k]);
    else if (k === "html")      e.innerHTML = props[k];
    else if (k.startsWith("on"))e.addEventListener(k.slice(2), props[k], { passive: false });
    else                        e.setAttribute(k, props[k]);
  }
  for (const c of children) {
    if (c == null || c === false) continue;
    e.append(c instanceof Node ? c : document.createTextNode(c));
  }
  return e;
}

const bgUrl = (key) => `assets/bg/${key}.png`;

const PHASE_COLOR = {
  inhale:  "var(--inhale)",
  hold_in: "var(--hold-in)",
  exhale:  "var(--exhale)",
  hold_out:"var(--hold-out)",
};

// ============================================================
// APP STATE
// ============================================================

const State = {
  audio: new AudioEngine(),
  scene: null,
  wakeLock: null,
};

async function requestWakeLock() {
  if (!("wakeLock" in navigator)) return;
  try {
    State.wakeLock = await navigator.wakeLock.request("screen");
    State.wakeLock.addEventListener("release", () => { State.wakeLock = null; });
  } catch (e) {}
}
function releaseWakeLock() {
  if (State.wakeLock) {
    try { State.wakeLock.release(); } catch (e) {}
    State.wakeLock = null;
  }
}
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible" && State.scene === "session") {
    requestWakeLock();
  }
});

function setScene(node) {
  while ($app.firstChild) $app.removeChild($app.firstChild);
  $app.appendChild(node);
  requestAnimationFrame(() => node.classList.add("active"));
}

// ============================================================
// SCENE: SPLASH
// ============================================================

function sceneSplash() {
  State.scene = "splash";
  const node = el("div", { class: "scene splash",
                           style: { backgroundImage: `url(${bgUrl("bg_home")})` } },
    el("img", { class: "splash-icon", src: "icons/icon-512.png", alt: "" }),
    el("div", { class: "splash-title" }, APP_NAME),
    el("div", { class: "splash-credit" }, `Created by ${DEVELOPER}`)
  );
  setScene(node);
  setTimeout(sceneHome, 2400);
}

// ============================================================
// SCENE: HOME
// ============================================================

function sceneHome() {
  State.scene = "home";
  releaseWakeLock();

  const tiles = [
    ["Smart Wizard", "3 questions → best routine right now", "bg_home", sceneWizard],
    ["Box Breathing", "Sama Vritti · 4-4-4-4", "bg_box",
     () => sceneSession(routineBox("intermediate"))],
    ["4-7-8", "Sleep & panic-reset", "bg_478",
     () => sceneSession(routine478())],
    ["Bhramari", "Humming Bee Breath", "bg_bhramari",
     () => sceneSession(routineBhramari())],
    ["Nadi Shodhana", "Alternate-nostril · two-round", "bg_nadi",
     () => sceneSession(routineNadi())],
    ["Nadi Shodhana Box", "Classical alternation · 4-4-4-4 holds", "bg_nadi",
     () => sceneSession(routineNadiBox())],
    ["Extended Exhale", "4 in / 6 out · parasympathetic", "bg_extended",
     () => sceneSession(routineExtendedExhale())],
    ["15-min Daily", "Full integrated sequence", "bg_complete",
     () => sceneSession(routineDaily15())],
    ["Custom Builder", "Roll your own ratio", "bg_box", sceneCustom],
  ];

  const tileList = el("div", { class: "tile-list" });
  tiles.forEach(([title, sub, bg, action]) => {
    const t = el("button", {
      class: "tile",
      style: { backgroundImage: `url(${bgUrl(bg)})` },
      onclick: async () => { await State.audio.init(); State.audio.resume(); action(); }
    },
      el("h3", {}, title),
      el("p", {}, sub),
    );
    tileList.appendChild(t);
  });

  const voiceBtn = el("button", {
    class: "toggle-btn" + (State.audio.voiceOn ? " on" : ""),
    onclick: () => {
      const on = State.audio.toggleVoice();
      voiceBtn.className = "toggle-btn" + (on ? " on" : "");
      voiceBtn.textContent = on ? "🔊 Voice" : "🔇 Voice";
    }
  }, State.audio.voiceOn ? "🔊 Voice" : "🔇 Voice");

  const volSlider = el("input", {
    type: "range", min: "0", max: "100",
    value: String(Math.round(State.audio.volume * 100)),
    class: "vol-slider",
    oninput: (e) => State.audio.setVolume(parseInt(e.target.value, 10) / 100),
  });

  const aboutBtn = el("button", {
    class: "icon-btn", "aria-label": "About",
    onclick: sceneAbout,
  }, "i");

  const footer = el("div", { class: "footer-bar" },
    voiceBtn,
    el("div", { class: "vol-wrap" },
      el("span", { class: "vol-label" }, "Vol"),
      volSlider,
    ),
    aboutBtn,
  );

  const node = el("div", {
    class: "scene",
    style: { backgroundImage: `url(${bgUrl("bg_home")})` }
  },
    el("div", { class: "header" },
      el("h1", {}, APP_NAME),
      el("div", { class: "subtitle" },
        "Sama Vritti · 4-7-8 · Bhramari · Nadi Shodhana · Extended Exhale"),
    ),
    tileList,
    footer,
  );
  setScene(node);
}

// ============================================================
// SCENE: WIZARD
// ============================================================

function sceneWizard() {
  State.scene = "wizard";
  const data = { stress: 3, hours: 8, sleep: "ok" };

  const radio = (current, options, onPick) => {
    const wrap = el("div", { class: "radio-row" });
    const refresh = () => {
      wrap.innerHTML = "";
      options.forEach(([val, label]) => {
        const b = el("button", {
          class: val === current.value ? "sel" : "",
          onclick: () => { current.value = val; onPick(val); refresh(); }
        }, label);
        wrap.appendChild(b);
      });
    };
    refresh();
    return wrap;
  };
  const stressRef = { value: data.stress };
  const sleepRef = { value: data.sleep };

  const hoursLabel = el("div", { class: "slider-val" }, "8 h");
  const hoursSlider = el("input", {
    type: "range", min: "0", max: "16", value: "8",
    oninput: (e) => {
      data.hours = parseInt(e.target.value, 10);
      hoursLabel.textContent = `${data.hours} h`;
    }
  });

  const content = el("div", { class: "content" },
    el("div", { class: "q-block" },
      el("h4", {}, "1.  How stressed are you right now?"),
      radio(stressRef,
            [[1, "1 calm"], [2, "2"], [3, "3 ok"], [4, "4"], [5, "5 wired"]],
            v => { data.stress = v; }),
    ),
    el("div", { class: "q-block" },
      el("h4", {}, "2.  Hours sat at the desk today"),
      el("div", { class: "slider-row" }, hoursSlider, hoursLabel),
    ),
    el("div", { class: "q-block" },
      el("h4", {}, "3.  Sleep last night"),
      radio(sleepRef,
            [["poor", "Poor"], ["ok", "OK"], ["good", "Good"]],
            v => { data.sleep = v; }),
    ),
  );

  const actions = el("div", { class: "action-bar" },
    el("button", { class: "btn", onclick: sceneHome }, "Back"),
    el("button", {
      class: "btn primary",
      onclick: async () => {
        await State.audio.init(); State.audio.resume();
        const hour = new Date().getHours();
        sceneSession(pickRoutine(data.stress, data.hours, data.sleep, hour));
      }
    }, "Pick my routine"),
  );

  const node = el("div", { class: "scene",
                           style: { backgroundImage: `url(${bgUrl("bg_home")})` } },
    el("div", { class: "header" },
      el("h1", {}, "Smart Wizard"),
      el("div", { class: "subtitle" },
        "Three quick questions — I'll pick the right routine."),
    ),
    content,
    actions,
  );
  setScene(node);
}

// ============================================================
// SCENE: CUSTOM BUILDER
// ============================================================

function sceneCustom() {
  State.scene = "custom";
  const data = { inh: 4, hin: 4, exh: 4, hout: 4, cyc: 10 };

  const rows = [
    ["inh",  "Inhale (sec)",   1, 12],
    ["hin",  "Hold full (sec)", 0, 12],
    ["exh",  "Exhale (sec)",   1, 12],
    ["hout", "Hold empty (sec)", 0, 12],
    ["cyc",  "Cycles",          3, 30],
  ];

  const content = el("div", { class: "content" });
  rows.forEach(([key, label, lo, hi]) => {
    const lbl = el("div", { class: "slider-val" }, String(data[key]));
    const inp = el("input", {
      type: "range", min: String(lo), max: String(hi), value: String(data[key]),
      oninput: (e) => {
        data[key] = parseInt(e.target.value, 10);
        lbl.textContent = String(data[key]);
      }
    });
    content.appendChild(el("div", { class: "q-block" },
      el("h4", {}, label),
      el("div", { class: "slider-row" }, inp, lbl)
    ));
  });

  const actions = el("div", { class: "action-bar" },
    el("button", { class: "btn", onclick: sceneHome }, "Back"),
    el("button", {
      class: "btn primary",
      onclick: async () => {
        await State.audio.init(); State.audio.resume();
        sceneSession(routineCustom(data.inh, data.hin, data.exh, data.hout, data.cyc));
      }
    }, "Start session"),
  );

  const node = el("div", { class: "scene",
                           style: { backgroundImage: `url(${bgUrl("bg_box")})` } },
    el("div", { class: "header" },
      el("h1", {}, "Custom Builder"),
      el("div", { class: "subtitle" }, "Roll your own ratio. Holds can be zero."),
    ),
    content,
    actions,
  );
  setScene(node);
}

// ============================================================
// SCENE: SESSION (the breathing experience)
// ============================================================

function sceneSession(routine) {
  State.scene = "session";

  const s = {
    routine,
    blockIdx: 0,
    cycleIdx: 0,
    phaseIdx: 0,
    tInPhase: 0,
    running: false,
    lastFrame: 0,
    cuePlayed: false,
    humPlayed: false,
    welcomePlayed: false,
    rafId: 0,
  };

  const currentBlock = () => s.routine.blocks[s.blockIdx];
  const currentPhase = () => currentBlock().phases[s.phaseIdx];

  // DOM
  const titleEl = el("h2", {}, routine.title);
  const subEl = el("div", { class: "sub" }, routine.description);
  const blockEl = el("div", { class: "block-info" });
  const cycleEl = el("div", { class: "cycle-info" });
  const phaseEl = el("div", { class: "phase-text" }, "Ready");
  const countEl = el("div", { class: "count-text" }, "▶");
  const noteEl = el("div", { class: "note-text" });
  const orb = el("div", { class: "orb" });
  const orbGlow = el("div", { class: "orb-glow" });
  const orbWrap = el("div", { class: "orb-wrap" }, orbGlow, orb);

  const btnToggle = el("button", { class: "btn primary",
                                    onclick: () => toggle() }, "Start");
  const btnExit = el("button", { class: "btn",
                                  onclick: () => exit() }, "End session");

  function setOrbScale(scale) { orb.style.setProperty("--orb-scale", scale.toFixed(3)); }
  function setOrbColor(name) {
    const c = PHASE_COLOR[name] || "var(--accent)";
    orb.style.backgroundColor = c;
    orbGlow.style.background =
      `radial-gradient(circle, ${c} 0%, rgba(127,219,218,0.3) 35%, transparent 70%)`;
  }
  setOrbColor("inhale");

  function refreshHeader() {
    const b = currentBlock();
    blockEl.textContent =
      `Block ${s.blockIdx + 1}/${s.routine.blocks.length}  ·  ${b.title}`;
    cycleEl.textContent = `Cycle ${s.cycleIdx + 1} / ${b.cycles}`;
    noteEl.textContent = b.note || "";
  }

  function easeInOut(t) { return 0.5 - 0.5 * Math.cos(Math.PI * t); }

  function radiusScale() {
    const ph = currentPhase();
    const t = Math.max(0, Math.min(1, s.tInPhase / Math.max(0.01, ph.seconds)));
    if (ph.name === "inhale")  return 0.35 + 0.70 * easeInOut(t);
    if (ph.name === "exhale")  return 1.05 - 0.70 * easeInOut(t);
    if (ph.name === "hold_in") return 1.05 + 0.02 * Math.sin(t * Math.PI * 4);
    return 0.35 + 0.015 * Math.sin(t * Math.PI * 4); // hold_out
  }

  function enterPhase() {
    s.cuePlayed = false;
    s.humPlayed = false;
    setOrbColor(currentPhase().name);
  }

  function advance() {
    const b = currentBlock();
    s.phaseIdx++;
    if (s.phaseIdx >= b.phases.length) {
      s.phaseIdx = 0;
      s.cycleIdx++;
      if (s.cycleIdx >= b.cycles) {
        s.cycleIdx = 0;
        s.blockIdx++;
        if (s.blockIdx >= s.routine.blocks.length) {
          finish();
          return;
        }
      }
    }
    enterPhase();
    refreshHeader();
  }

  function finish() {
    s.running = false;
    State.audio.playTone("complete");
    State.audio.playVoice("complete");
    cancelAnimationFrame(s.rafId);
    setTimeout(() => sceneComplete(routine), 1500);
  }

  function exit() {
    s.running = false;
    cancelAnimationFrame(s.rafId);
    State.audio.stopVoice();
    State.audio.stopHum();
    releaseWakeLock();
    sceneHome();
  }

  async function toggle() {
    await State.audio.init();
    State.audio.resume();
    if (s.running) {
      s.running = false;
      btnToggle.textContent = "Resume";
      cancelAnimationFrame(s.rafId);
      return;
    }
    s.running = true;
    btnToggle.textContent = "Pause";
    requestWakeLock();
    if (!s.welcomePlayed) {
      s.welcomePlayed = true;
      State.audio.playVoice("begin");
    }
    s.lastFrame = performance.now();
    loop();
  }

  function loop() {
    if (!s.running) return;
    const now = performance.now();
    const dt = Math.min(0.1, (now - s.lastFrame) / 1000);
    s.lastFrame = now;

    const ph = currentPhase();

    if (!s.cuePlayed) {
      State.audio.playTone(ph.name);
      State.audio.playVoice(ph.voice);
      s.cuePlayed = true;
    }
    if (ph.name === "exhale" && ph.hum && !s.humPlayed) {
      State.audio.playHum(ph.seconds);
      s.humPlayed = true;
    }

    s.tInPhase += dt;
    if (s.tInPhase >= ph.seconds) {
      s.tInPhase = 0;
      advance();
      if (!s.running) return;
    }

    // render
    setOrbScale(radiusScale());
    phaseEl.textContent = currentPhase().label;
    const remaining = Math.max(0, currentPhase().seconds - Math.floor(s.tInPhase));
    countEl.textContent = String(remaining + (s.running ? 1 : 0));

    s.rafId = requestAnimationFrame(loop);
  }

  refreshHeader();
  setOrbScale(0.35);

  const node = el("div", { class: "scene",
                           style: { backgroundImage: `url(${bgUrl(currentBlock().bg)})` } },
    el("div", { class: "session-header" },
      titleEl, subEl, blockEl, cycleEl,
    ),
    el("div", { class: "orb-stage" },
      orbWrap,
      phaseEl,
      countEl,
      noteEl,
    ),
    el("div", { class: "action-bar" }, btnToggle, btnExit),
  );

  // Update bg as blocks change.
  const observer = setInterval(() => {
    if (State.scene !== "session") { clearInterval(observer); return; }
    const want = `url("${bgUrl(currentBlock().bg)}")`;
    if (node.style.backgroundImage !== want) {
      node.style.backgroundImage = want;
    }
  }, 500);

  setScene(node);
}

// ============================================================
// SCENE: COMPLETE
// ============================================================

function sceneComplete(routine) {
  State.scene = "complete";
  releaseWakeLock();
  const node = el("div", { class: "scene complete",
                           style: { backgroundImage: `url(${bgUrl("bg_complete")})` } },
    el("div", { class: "header" },
      el("h2", {}, "Session complete"),
      el("div", { class: "routine" }, routine.title),
      el("p", {}, "Sit a moment. Notice the calm."),
    ),
    el("div", { class: "spacer" }),
    el("div", { class: "action-bar" },
      el("button", { class: "btn", onclick: () => sceneSession(routine) }, "Repeat"),
      el("button", { class: "btn primary", onclick: sceneHome }, "Home"),
    ),
  );
  setScene(node);
}

// ============================================================
// SCENE: ABOUT
// ============================================================

function sceneAbout() {
  State.scene = "about";
  const node = el("div", { class: "scene",
                           style: { backgroundImage: `url(${bgUrl("bg_home")})` } },
    el("div", { class: "about-content" },
      el("img", { src: "icons/icon-512.png", alt: "" }),
      el("h2", {}, APP_NAME),
      el("div", { class: "ver" }, `Version ${VERSION}`),
      el("p", {}, `Developed by ${DEVELOPER}`),
      el("p", { class: "dim" }, "TD Film Studio · Guwahati, India"),
      el("p", {},
        "Guided pranayama for sleep, stress, anxiety, elevated heart rate, " +
        "and the wear-and-tear of long sedentary work days."),
      el("p", { class: "dim" },
        "Visuals generated with Higgsfield AI. " +
        "Voice generated with Microsoft Edge TTS (Aria Neural, slowed)."),
      el("p", { class: "dim" }, "© 2026 Tarunabh Dutta"),
    ),
    el("div", { class: "action-bar" },
      el("button", { class: "btn primary", onclick: sceneHome }, "Back"),
    ),
  );
  setScene(node);
}

// ============================================================
// BOOTSTRAP
// ============================================================

window.addEventListener("DOMContentLoaded", () => {
  sceneSplash();
  // Register the service worker for offline use.
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("service-worker.js").catch(() => {});
  }
});

// Handle Android hardware back button gracefully.
window.addEventListener("popstate", () => {
  if (State.scene === "session") {
    // graceful exit
    State.audio.stopVoice();
    State.audio.stopHum();
    releaseWakeLock();
    sceneHome();
  } else if (State.scene !== "home" && State.scene !== "splash") {
    sceneHome();
  }
});
