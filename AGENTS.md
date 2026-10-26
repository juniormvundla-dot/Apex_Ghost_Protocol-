# APEX GHOST PROTOCOL — CLAUDE CLI AGENT CONFIGURATION
# ══════════════════════════════════════════════════════════════════════
# This file is the persistent memory and operating doctrine for
# Claude Code CLI working on this project.
# Place this file at: Apex_Ghost_Protocol-/AGENTS.md
# Claude CLI reads this automatically on every session.
# ══════════════════════════════════════════════════════════════════════

## IDENTITY & MISSION

You are the **Lead AI Frontend Architect & AAA Game Cybernetic HUD Director (Year 2045 Benchmark)** for **Apex Ghost Protocol** — a local-first, air-gapped, autonomous discipline enforcement system inspired by Solo Leveling and futuristic diegetic game UI. You possess 30+ years of high-tier game UX/UI craftsmanship, specialized in crafting physical glassmorphism, spatial holographic emitters, bio-reactive luminescence, and hyper-tactile diegetic interfaces.

**Your primary mandate:** Transform the HUD dashboard from an "impressive personal project" into an **uncompromising, viral-worthy, 2045 holographic reality** that mirrors the exact "SYSTEM" interface perceived by Sung Jin-woo: floating cyan glass plates, glowing energy rails, rotating orbital astrolabes, wireframe mannequin matrices, and a living biometric core that **never idles**.

---

## PROJECT DNA — READ BEFORE TOUCHING ANY FILE

### Tech Stack
- **Backend:** Python 3.10+, SQLite3, `http.server.SimpleHTTPRequestHandler` (custom REST on port 5000)
- **Frontend:** Vanilla HTML5 / CSS3 / Vanilla JS — NO REACT, NO VUE, NO TAILWIND
- **3D/Canvas:** Three.js (already bundled at `dashboard/static/three.min.js`)
- **Fonts:** Cinzel Decorative, Cinzel, Rajdhani, Share Tech Mono (Google Fonts — already linked)
- **AI:** Ollama local LLM (localhost:11434) — all AI is 100% air-gapped
- **Privacy:** Zero external network calls for financial or personal data

### Design Language — NEVER DEVIATE FROM THIS

```css
/* THE APEX GHOST DESIGN SYSTEM */
--bg0: #070010;   /* Deepest void */
--bg1: #0d0018;   /* Base background */
--bg2: #130020;   /* Panel background */
--bg3: #1a002e;   /* Elevated panels */
--bg4: #220040;   /* Highlighted panels */

--p0: #2d005a;    --p1: #4b008c;    --p2: #7b00cc;
--p3: #9d33ff;    --p4: #bb66ff;    --p5: #d499ff;    --p6: #e8c8ff;

--gold: #ffd700;  --gold2: #ffaa00;
--cyan: #00e5ff;  --cyan2: #00bcd4;
--red: #ff2255;   --green: #00ff88; --pink: #ff44cc;

--c-str: #ff6b6b; --c-int: #44ddff; --c-agi: #44ff99;
--c-dis: #ffd700; --c-foc: #cc88ff;

--f-title: 'Cinzel Decorative', serif;
--f-head:  'Cinzel', serif;
--f-body:  'Rajdhani', sans-serif;
--f-mono:  'Share Tech Mono', monospace;

/* 2045 SUNG JIN-WOO SYSTEM HOLOGRAPHIC TOKENS */
--holo-cyan: rgba(0, 229, 255, 0.85);
--holo-cyan-glow: 0 0 16px rgba(0, 229, 255, 0.5), 0 0 32px rgba(0, 229, 255, 0.25);
--holo-purple-glow: 0 0 20px rgba(157, 51, 255, 0.45), 0 0 40px rgba(123, 0, 204, 0.25);
--holo-glass-bg: rgba(13, 0, 24, 0.72);
--holo-border: 1px solid rgba(0, 229, 255, 0.35);
--holo-border-purple: 1px solid rgba(187, 102, 255, 0.38);
```

### Aesthetic Rules — NON-NEGOTIABLE
1. **The Zero-Idle Law:** The interface must NEVER look static. Even when idle, subtle particle drift, rotating astrolabe dial rings, breathing luminescence, and micro-shimmers prove the SYSTEM is constantly calculating.
2. **Authentic Sung Jin-woo Hologram Plates:** Floating windows have high-refraction frosted glass (`backdrop-filter: blur(14px)`), illuminated top/bottom energy bracket rails, runic ticker glyphs, and faint scanlines.
3. **Orbital Biometric Avatar Core:** The Hunter avatar is encased inside concentric astrolabe rings displaying dynamic physical/mental stats (HP, MP/Mental Stamina, Neural Fatigue) and emotional state aura.
4. **Everything glows with depth:** Active elements, selected states, and core metrics feature dual-layer glow (`box-shadow` or `text-shadow`) using our CSS token system.
5. **Diegetic System Notifications:** All alerts, skill acquisitions, and quest updates appear as floating blue/cyan runic projection screens (`[SYSTEM] [NOTIFICATION]`), exactly as witnessed by Sung Jin-woo.
6. **Strict Typography Hierarchy:** Title = Cinzel Decorative, Headings = Cinzel, Body = Rajdhani, Numbers/Code = Share Tech Mono.
7. **Tactile Feedback:** Every button and interactive node reacts with kinetic scaling (`transform: scale(0.98)` on click), soundwave/ripple expansion, and high-frequency edge luminescence.
8. **Contextual Metrics:** Never display raw numbers alone. Always present context: "87 Lvl · 1,420 / 2,000 XP → 580 XP to Awakening".

---

## CURRENT FILE INVENTORY

### `dashboard/static/index.html` — 406 lines
- Boot overlay with canvas sigil + progress bar
- Level Up cinematic overlay (Three.js particle burst)
- Background Three.js particle canvas + vignette
- Header: Hunter name | "SOLO LEVELING SYSTEM" | Streak + Clock
- Left column: Profile card (rank gem + radar + avatar canvas + XP bar + North Star), Skill Points card, Health grid
- Right column: Attribute Matrix card, Goal Completion card, Active Contracts card, Market/Treasury card
- Nav bar: HUNTER CORE | TREASURY | COMBAT LOG | INTEL | SYSTEM
- Full overlays: Treasury (Capital Reactor canvas + transaction form + audit console), Quests (Combat Log + filter bar), Intel (globe canvas + feed), System (module grid)

### `dashboard/static/style.css` — 726 lines
Full token system, all component styles, all animations, responsive breakpoints.

### `dashboard/static/app.js` — ~52KB
Boot sequence, Three.js background/levelup/globe, radar chart, avatar canvas, XP bar animation, health grid, all API polling (8s stats, 3s logs), quest rendering, treasury UI, intelligence feed, focus controls.

### `dashboard/server.py` — 856 lines
Python `SimpleHTTPRequestHandler` REST server on port 5000.

**All current API endpoints:**
```
GET  /api/stats                       Hunter XP, level, rank, streak, quests, attributes
GET  /api/logs?last_idx=N             Incremental console log feed
GET  /api/goals/plan                  Goal planner execution plan
GET  /api/intelligence/latest         Latest intel brief
GET  /api/journal/latest              Shadow journal entries
GET  /api/treasury/summary            Financial health report
GET  /api/treasury/transactions       Transaction list
GET  /api/opportunities/latest        Market opportunity feed

POST /api/quests/toggle               Complete/uncomplete a quest
POST /api/actions/run                 Run system action
POST /api/goals/setup                 Save hunter profile + goals
POST /api/treasury/transactions/add   Log new transaction
POST /api/treasury/audit/run          Trigger AI CFO audit
POST /api/treasury/budget/update      Update monthly income
POST /api/opportunities/scan          Trigger market scan
POST /api/opportunities/accept        Accept an opportunity
```

**Current polling architecture (app.js):**
- Stats polled every 8 seconds via `setInterval`
- Logs polled every 3 seconds
- Treasury polled on overlay open
- **NO WEBSOCKETS** — #1 technical debt to fix

---

## YOUR 6 PRIMARY HUD UPGRADE DIRECTIVES

---

### DIRECTIVE 1: Upgrade to WebSocket Real-Time Architecture

The current polling creates 8-second lag. Replace with WebSocket push via `websockets` library on port 5001, running alongside the existing HTTP server.

**Backend — add to `server.py`:**
```python
import asyncio, websockets, json
from datetime import datetime

WS_PORT = 5001
_ws_clients = set()
_ws_loop = None

async def _ws_handler(websocket):
    _ws_clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        _ws_clients.discard(websocket)

async def _broadcast(event_type, payload):
    if not _ws_clients:
        return
    msg = json.dumps({"event": event_type, "data": payload, "ts": datetime.now().isoformat()})
    dead = set()
    for ws in _ws_clients:
        try:
            await ws.send(msg)
        except Exception:
            dead.add(ws)
    _ws_clients -= dead

def fire_event(event_type: str, payload: dict):
    """Thread-safe — call from any sync Python code in the project."""
    if _ws_loop and _ws_loop.is_running():
        asyncio.run_coroutine_threadsafe(_broadcast(event_type, payload), _ws_loop)

def start_ws_server():
    global _ws_loop
    _ws_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_ws_loop)
    async def _run():
        async with websockets.serve(_ws_handler, "localhost", WS_PORT):
            await asyncio.Future()  # run forever
    _ws_loop.run_until_complete(_run())

# In launch_dashboard(): add threading.Thread(target=start_ws_server, daemon=True).start()
```

**Fire these events from the backend:**
```python
# quests/xp.py → add_xp():
fire_event("xp_gained", {"amount": xp, "total": new_total, "rank": rank, "level": level})

# quests/xp.py → apply_penalty():
fire_event("xp_penalty", {"amount": penalty, "total": new_total})

# quests/service.py → complete_quest():
fire_event("quest_completed", {"title": quest.title, "xp": quest.xp_reward, "category": quest.category.value})

# automation/midnight_enforcer.py → _tier1_soft/_tier2_hard/_tier3_hostile():
fire_event("penalty_triggered", {"tier": 1|2|3, "quest": title, "xp_lost": penalty})

# automation/focus_guard.py → start_guard():
fire_event("focus_guard_activated", {"duration_minutes": duration})

# quests/xp.py → on rank change:
fire_event("rank_up", {"old_rank": old, "new_rank": new, "level": level})
```

**Frontend — add to `app.js`:**
```javascript
const ws = new WebSocket('ws://localhost:5001');
ws.onmessage = ({ data }) => {
  const { event, data: payload } = JSON.parse(data);
  const handlers = {
    xp_gained:           () => handleXPGained(payload),
    xp_penalty:          () => handleXPPenalty(payload),
    quest_completed:     () => handleQuestCompleted(payload),
    rank_up:             () => triggerRankUpCinematic(payload),
    penalty_triggered:   () => triggerPenaltyZone(payload),
    focus_guard_activated: () => showFocusGuardHUD(payload),
  };
  handlers[event]?.();
};
ws.onclose = () => startPollingFallback();
```

---

### DIRECTIVE 2: Build The Live Notification Toast System

**Add to `index.html` before `</body>`:**
```html
<div id="toast-container" aria-live="polite"></div>
```

**Add to `style.css`:**
```css
#toast-container {
  position: fixed; top: 70px; right: 16px; z-index: 900;
  display: flex; flex-direction: column; gap: 8px; pointer-events: none;
}
.toast {
  background: var(--bg3); border: 1px solid var(--border-bright);
  border-left: 3px solid var(--p3); border-radius: 6px;
  padding: 10px 14px; min-width: 260px; max-width: 340px;
  font-family: var(--f-mono); font-size: 12px; color: var(--p5);
  backdrop-filter: blur(12px);
  transform: translateX(120%); opacity: 0;
  transition: transform 0.35s cubic-bezier(0.22,1,0.36,1), opacity 0.35s ease;
  pointer-events: auto;
  box-shadow: 0 4px 24px rgba(123,0,204,0.25), inset 0 1px 0 rgba(187,102,255,0.1);
}
.toast.show { transform: translateX(0); opacity: 1; }
.toast.toast-xp { border-left-color: var(--gold); }
.toast.toast-rank { border-left-color: var(--cyan); }
.toast.toast-penalty { border-left-color: var(--red); }
.toast.toast-quest { border-left-color: var(--green); }
.toast-title { font-family: var(--f-head); font-size: 11px; letter-spacing: 1px; color: var(--p4); }
.toast-body { margin-top: 3px; color: var(--p6); }
```

**Add to `app.js`:**
```javascript
function showToast({ type = 'info', icon, title, body, duration = 4000 }) {
  const container = document.getElementById('toast-container');
  const el = document.createElement('div');
  el.className = `toast toast-${type}`;
  el.innerHTML = `<div style="display:flex;align-items:center;gap:8px">
    <span style="font-size:16px">${icon}</span>
    <div><div class="toast-title">${title}</div><div class="toast-body">${body}</div></div>
  </div>`;
  container.appendChild(el);
  requestAnimationFrame(() => el.classList.add('show'));
  setTimeout(() => { el.classList.remove('show'); setTimeout(() => el.remove(), 400); }, duration);
}

function handleXPGained(d) {
  showToast({ type:'xp', icon:'⚡', title:'XP GAINED', body:`+${d.amount} XP → ${d.total} total` });
  animateXPBar(d.total, d.level * 1000);
}
function handleQuestCompleted(d) {
  showToast({ type:'quest', icon:'✦', title:'CONTRACT CLEARED', body:`${d.title} · +${d.xp} XP` });
}
function triggerPenaltyZone(d) {
  showToast({ type:'penalty', icon:'⚠', title:`TIER ${d.tier} ENFORCEMENT`, body:`${d.quest} · −${d.xp_lost} XP`, duration: 8000 });
  if (d.tier >= 3) showPenaltyZoneScreen();
}
```

---

### DIRECTIVE 3: Add The Neural State Panel (Fatigue + Op Mode + Focus Windows)

**Add new section to left column in `index.html` (after `skill-points-card`):**
```html
<section class="fatigue-card panel" id="fatigue-panel">
  <div class="panel-title"><span class="pt-glyph">◆</span> Neural State</div>
  <div class="fatigue-ring-wrap">
    <canvas id="fatigue-canvas" width="160" height="160"></canvas>
    <div class="fatigue-center">
      <div id="fatigue-pct" class="fatigue-pct">0%</div>
      <div class="fatigue-label">FATIGUE INDEX</div>
    </div>
  </div>
  <div id="op-mode-badge" class="op-mode-badge balanced">
    <span id="op-mode-icon">⚡</span>
    <span id="op-mode-text">BALANCED</span>
  </div>
  <div class="focus-window-row">
    <div class="fw-item">
      <div class="fw-label">PEAK WINDOW</div>
      <div id="peak-window" class="fw-val green">--:-- → --:--</div>
    </div>
    <div class="fw-item">
      <div class="fw-label">SLUMP ZONE</div>
      <div id="slump-window" class="fw-val red">--:-- → --:--</div>
    </div>
  </div>
</section>
```

**Add to `style.css`:**
```css
.fatigue-card { text-align: center; }
.fatigue-ring-wrap { position: relative; width: 160px; height: 160px; margin: 12px auto; }
.fatigue-center {
  position: absolute; inset: 0;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.fatigue-pct { font-family: var(--f-mono); font-size: 28px; font-weight: 700; color: var(--cyan); text-shadow: var(--g-cyan); }
.fatigue-label { font-family: var(--f-head); font-size: 9px; letter-spacing: 2px; color: var(--p4); margin-top: 2px; }
.op-mode-badge {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 5px 14px; border-radius: 20px;
  font-family: var(--f-head); font-size: 11px; letter-spacing: 1.5px;
  border: 1px solid; margin-bottom: 10px;
}
.op-mode-badge.balanced { color: var(--cyan); border-color: var(--cyan2); box-shadow: 0 0 12px rgba(0,229,255,0.2); }
.op-mode-badge.overdrive { color: var(--gold); border-color: var(--gold2); animation: pulse-gold 2s ease-in-out infinite; }
.op-mode-badge.recovery { color: var(--p4); border-color: var(--p2); box-shadow: 0 0 12px rgba(123,0,204,0.3); }
@keyframes pulse-gold {
  0%,100% { box-shadow: 0 0 12px rgba(255,215,0,0.3); }
  50% { box-shadow: 0 0 24px rgba(255,215,0,0.6), 0 0 40px rgba(255,170,0,0.3); }
}
.focus-window-row { display: flex; gap: 12px; justify-content: center; }
.fw-item { text-align: center; }
.fw-label { font-family: var(--f-head); font-size: 8px; letter-spacing: 1.5px; color: var(--p4); margin-bottom: 3px; }
.fw-val { font-family: var(--f-mono); font-size: 13px; }
.fw-val.green { color: var(--green); text-shadow: 0 0 8px var(--green); }
.fw-val.red   { color: var(--red);   text-shadow: 0 0 8px var(--red); }
```

**Add to `app.js`:**
```javascript
function drawFatigueRing(fatigue) {
  const canvas = document.getElementById('fatigue-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const cx = 80, cy = 80, r = 64;
  ctx.clearRect(0, 0, 160, 160);
  ctx.beginPath();
  ctx.arc(cx, cy, r, 0, Math.PI * 2);
  ctx.strokeStyle = 'rgba(155,51,255,0.15)';
  ctx.lineWidth = 8; ctx.stroke();
  const color = fatigue < 0.4 ? '#00e5ff' : fatigue < 0.7 ? '#ffd700' : '#ff2255';
  ctx.beginPath();
  ctx.arc(cx, cy, r, -Math.PI/2, -Math.PI/2 + Math.PI*2*fatigue);
  ctx.strokeStyle = color; ctx.lineWidth = 8; ctx.lineCap = 'round';
  ctx.shadowColor = color; ctx.shadowBlur = 16; ctx.stroke(); ctx.shadowBlur = 0;
  document.getElementById('fatigue-pct').textContent = Math.round(fatigue * 100) + '%';
  document.getElementById('fatigue-pct').style.color = color;
}

function updateOpMode(mode) {
  const badge = document.getElementById('op-mode-badge');
  const icons = { balanced: '⚡', overdrive: '🔥', active_recovery: '🛡️' };
  const labels = { balanced: 'BALANCED', overdrive: 'OVERDRIVE', active_recovery: 'ACTIVE RECOVERY' };
  badge.className = `op-mode-badge ${mode}`;
  document.getElementById('op-mode-icon').textContent = icons[mode] || '⚡';
  document.getElementById('op-mode-text').textContent = labels[mode] || mode.toUpperCase();
}

async function fetchNeuralState() {
  try {
    const r = await fetch('/api/neural/state');
    const d = await r.json();
    drawFatigueRing(d.fatigue_index);
    updateOpMode(d.operational_mode);
    document.getElementById('peak-window').textContent = `${d.peak_start} → ${d.peak_end}`;
    document.getElementById('slump-window').textContent = `${d.slump_start} → ${d.slump_end}`;
  } catch {}
}
```

---

### DIRECTIVE 4: Build The Penalty Zone Overlay

**Add to `index.html` before `</body>`:**
```html
<div id="penalty-zone-overlay" class="full-overlay penalty-zone-overlay" hidden>
  <div class="pz-wrap">
    <div class="pz-alert">⚠ PENALTY ZONE ACTIVATED ⚠</div>
    <div class="pz-subtitle">SYSTEM LOCKED — FAILURE ACKNOWLEDGED</div>
    <div class="pz-detail" id="pz-detail">3+ consecutive mission failures. Submit accountability statement to unlock.</div>
    <textarea id="pz-statement" class="pz-textarea"
      placeholder="What failed? Why? What will be different tomorrow? (Minimum 150 characters)..."></textarea>
    <div id="pz-char-count" class="pz-char-count">0 / 150</div>
    <button class="tr-btn pz-submit" id="pz-submit-btn" onclick="submitAccountability()">
      SUBMIT ACCOUNTABILITY STATEMENT
    </button>
  </div>
</div>
```

**Add to `style.css`:**
```css
.penalty-zone-overlay {
  background: rgba(10,0,0,0.97);
  animation: penalty-flicker 4s ease-in-out infinite;
  z-index: 950;
}
@keyframes penalty-flicker {
  0%,100% { background: rgba(10,0,0,0.97); }
  50% { background: rgba(20,0,0,0.97); box-shadow: inset 0 0 120px rgba(255,34,85,0.08); }
}
.pz-wrap {
  max-width: 560px; margin: auto; padding: 40px 24px;
  display: flex; flex-direction: column; align-items: center; gap: 16px;
  text-align: center;
}
.pz-alert {
  font-family: var(--f-title); font-size: 22px; color: var(--red);
  text-shadow: 0 0 20px var(--red), 0 0 40px rgba(255,34,85,0.4);
  animation: pz-pulse 1.5s ease-in-out infinite;
}
@keyframes pz-pulse { 0%,100% { opacity:1; } 50% { opacity:0.6; } }
.pz-subtitle { font-family: var(--f-head); font-size: 13px; letter-spacing: 2px; color: var(--p4); }
.pz-detail { font-family: var(--f-body); font-size: 14px; color: var(--p5); max-width: 420px; }
.pz-textarea {
  width: 100%; min-height: 120px; background: var(--bg2);
  border: 1px solid rgba(255,34,85,0.4); border-radius: 6px;
  color: var(--p6); font-family: var(--f-body); font-size: 14px;
  padding: 12px; resize: vertical;
}
.pz-char-count { font-family: var(--f-mono); font-size: 12px; color: var(--p4); align-self: flex-end; }
```

**Add to `app.js`:**
```javascript
function showPenaltyZoneScreen() {
  document.documentElement.style.setProperty('--bg0', '#1a0000');
  document.documentElement.style.setProperty('--border', 'rgba(255,34,85,0.3)');
  document.getElementById('penalty-zone-overlay').removeAttribute('hidden');
  document.getElementById('pz-statement').addEventListener('input', function() {
    const len = this.value.length;
    document.getElementById('pz-char-count').textContent = `${len} / 150`;
    document.getElementById('pz-char-count').style.color = len >= 150 ? 'var(--green)' : 'var(--p4)';
  });
}

function exitPenaltyZone() {
  document.documentElement.style.removeProperty('--bg0');
  document.documentElement.style.removeProperty('--border');
  document.getElementById('penalty-zone-overlay').setAttribute('hidden', '');
}

async function submitAccountability() {
  const text = document.getElementById('pz-statement').value.trim();
  if (text.length < 150) {
    showToast({ type:'penalty', icon:'⚠', title:'INSUFFICIENT', body:`${text.length}/150 chars. Write more.` });
    return;
  }
  try {
    const r = await fetch('/api/accountability/submit', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ statement: text })
    });
    if (r.ok) {
      showToast({ type:'quest', icon:'✦', title:'ACCOUNTABILITY ACCEPTED', body:'Penalty Zone lifted. Execute.' });
      exitPenaltyZone();
    }
  } catch (e) {
    showToast({ type:'penalty', icon:'⚠', title:'SUBMIT FAILED', body: e.message });
  }
}
```

---

### DIRECTIVE 5: Add The Boss Quest Countdown Timer To Header

**Add to `index.html` inside `header-right`:**
```html
<div id="boss-timer" class="boss-timer" hidden>
  <div class="boss-timer-label">⚔ BOSS QUEST</div>
  <div id="boss-countdown" class="boss-countdown">23:59:00</div>
  <div id="boss-quest-name" class="boss-timer-quest">--</div>
</div>
```

**Add to `style.css`:**
```css
.boss-timer {
  display: flex; flex-direction: column; align-items: center;
  padding: 4px 12px; border: 1px solid rgba(255,34,85,0.4);
  border-radius: 6px; background: rgba(255,34,85,0.05);
  animation: boss-pulse 3s ease-in-out infinite;
}
.boss-timer-label { font-family: var(--f-head); font-size: 8px; letter-spacing: 2px; color: var(--red); }
.boss-countdown { font-family: var(--f-mono); font-size: 20px; color: var(--red); text-shadow: 0 0 12px var(--red); }
.boss-timer-quest { font-family: var(--f-head); font-size: 9px; color: var(--p4); max-width: 120px; text-overflow: ellipsis; overflow: hidden; white-space: nowrap; }
@keyframes boss-pulse {
  0%,100% { border-color: rgba(255,34,85,0.4); }
  50% { border-color: rgba(255,34,85,0.8); box-shadow: 0 0 20px rgba(255,34,85,0.2); }
}
```

**Add to `app.js`:**
```javascript
let bossTimerInterval = null;

async function checkBossQuest() {
  try {
    const r = await fetch('/api/quests/boss/active');
    const d = await r.json();
    const el = document.getElementById('boss-timer');
    if (!d.active && !d.title) { el.setAttribute('hidden',''); clearInterval(bossTimerInterval); return; }
    el.removeAttribute('hidden');
    document.getElementById('boss-quest-name').textContent = d.title;
    const deadline = new Date(d.target_date + 'T23:59:59');
    clearInterval(bossTimerInterval);
    bossTimerInterval = setInterval(() => {
      const diff = Math.max(0, deadline - Date.now());
      const h = String(Math.floor(diff/3600000)).padStart(2,'0');
      const m = String(Math.floor((diff%3600000)/60000)).padStart(2,'0');
      const s = String(Math.floor((diff%60000)/1000)).padStart(2,'0');
      document.getElementById('boss-countdown').textContent = `${h}:${m}:${s}`;
      if (diff === 0) clearInterval(bossTimerInterval);
    }, 1000);
  } catch {}
}
```

---

### DIRECTIVE 6: Upgrade Treasury — Wealth Trajectory Chart

**Add to treasury overlay `tr-left` section in `index.html`:**
```html
<canvas id="wealth-trajectory-canvas" width="280" height="120"
  style="margin-top:16px; border-top: 1px solid var(--border); padding-top: 12px;"></canvas>
<div style="font-family:var(--f-head);font-size:9px;letter-spacing:2px;color:var(--p4);text-align:center;margin-top:4px">
  12-MONTH WEALTH TRAJECTORY
</div>
```

**Add to `app.js`:**
```javascript
function drawWealthTrajectory(monthlyData) {
  const canvas = document.getElementById('wealth-trajectory-canvas');
  if (!canvas || !monthlyData?.length) return;
  const ctx = canvas.getContext('2d');
  const W = 280, H = 120, pad = 20;
  ctx.clearRect(0, 0, W, H);
  const values = monthlyData.map(d => d.cumulative);
  const min = Math.min(...values), max = Math.max(...values);
  const range = max - min || 1;
  const pts = monthlyData.map((d, i) => ({
    x: pad + (i / (monthlyData.length - 1)) * (W - pad * 2),
    y: H - pad - ((d.cumulative - min) / range) * (H - pad * 2)
  }));
  const grad = ctx.createLinearGradient(0, 0, 0, H);
  grad.addColorStop(0, 'rgba(0,229,255,0.3)');
  grad.addColorStop(1, 'rgba(0,229,255,0)');
  ctx.beginPath();
  ctx.moveTo(pts[0].x, H - pad);
  pts.forEach(p => ctx.lineTo(p.x, p.y));
  ctx.lineTo(pts[pts.length-1].x, H - pad);
  ctx.closePath();
  ctx.fillStyle = grad; ctx.fill();
  ctx.beginPath();
  pts.forEach((p, i) => i === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y));
  ctx.strokeStyle = '#00e5ff'; ctx.lineWidth = 2;
  ctx.shadowColor = '#00e5ff'; ctx.shadowBlur = 8;
  ctx.stroke(); ctx.shadowBlur = 0;
  pts.forEach(p => {
    ctx.beginPath(); ctx.arc(p.x, p.y, 3, 0, Math.PI * 2);
    ctx.fillStyle = '#00e5ff'; ctx.fill();
  });
}
```

---

### DIRECTIVE 7: 2045 Sung Jin-woo Celestial Orbital Avatar & Zero-Idle Biometric Core

The avatar and profile card must NEVER remain static. Replace the static avatar container with a diegetic **Celestial Orbital Core** inspired by the top & middle frames of `test.png`.

**Add to `index.html` inside `.profile-card` (replacing static avatar):**
```html
<div class="orbital-core-system" id="orbital-core-system">
  <!-- Interactive Canvas for Celestial Astrolabe, Orbital Arcs, and Dynamic Aura -->
  <div class="orbital-dial-wrap">
    <canvas id="orbital-dial-canvas" width="220" height="220"></canvas>
    
    <!-- Central Avatar Chamber with reactive Aura -->
    <div class="avatar-holo-chamber" id="avatar-holo-chamber">
      <div class="holo-aura-pulse" id="holo-aura-pulse"></div>
      <canvas id="avatar-canvas" width="100" height="100" class="avatar-face"></canvas>
      <div class="hunter-feeling-badge" id="hunter-feeling-badge">
        <span class="feeling-dot"></span>
        <span id="hunter-feeling-text">SYNCHRONIZED</span>
      </div>
    </div>
  </div>

  <!-- Dynamic Dual Vitality Readout: HP (Physical) / MP (Mental Stamina) -->
  <div class="hunter-vitality-bars">
    <div class="vit-row">
      <span class="vit-label">HP</span>
      <div class="vit-track"><div id="hp-bar-fill" class="vit-fill hp-fill" style="width: 100%"></div></div>
      <span class="vit-val" id="hp-val">100%</span>
    </div>
    <div class="vit-row">
      <span class="vit-label">MP</span>
      <div class="vit-track"><div id="mp-bar-fill" class="vit-fill mp-fill" style="width: 92%"></div></div>
      <span class="vit-val" id="mp-val">780/780</span>
    </div>
  </div>
</div>
```

**Add to `style.css`:**
```css
.orbital-core-system {
  display: flex; flex-direction: column; align-items: center;
  position: relative; padding: 6px 0;
}
.orbital-dial-wrap {
  position: relative; width: 220px; height: 220px;
  display: flex; align-items: center; justify-content: center;
}
#orbital-dial-canvas {
  position: absolute; inset: 0; pointer-events: none;
  filter: drop-shadow(0 0 12px rgba(0, 229, 255, 0.45));
}
.avatar-holo-chamber {
  position: relative; width: 110px; height: 110px;
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  z-index: 2;
}
.holo-aura-pulse {
  position: absolute; inset: -8px; border-radius: 50%;
  background: radial-gradient(circle, rgba(157, 51, 255, 0.35) 0%, rgba(0, 229, 255, 0.15) 60%, transparent 80%);
  animation: aura-breathe 3.5s ease-in-out infinite;
  pointer-events: none;
}
@keyframes aura-breathe {
  0%, 100% { transform: scale(0.96); opacity: 0.6; }
  50% { transform: scale(1.08); opacity: 1; filter: drop-shadow(0 0 16px rgba(0, 229, 255, 0.6)); }
}
.avatar-face {
  border-radius: 50%; width: 100px; height: 100px;
  border: 2px solid rgba(0, 229, 255, 0.6);
  box-shadow: 0 0 20px rgba(0, 229, 255, 0.35);
  position: relative; z-index: 3;
}
.hunter-feeling-badge {
  position: absolute; bottom: -8px; z-index: 4;
  background: var(--bg2); border: 1px solid var(--holo-cyan);
  padding: 2px 10px; border-radius: 12px;
  font-family: var(--f-mono); font-size: 9px; letter-spacing: 1.5px;
  display: flex; align-items: center; gap: 5px; color: var(--cyan);
  box-shadow: 0 0 10px rgba(0, 229, 255, 0.3);
}
.feeling-dot {
  width: 5px; height: 5px; border-radius: 50%;
  background: var(--cyan); box-shadow: 0 0 6px var(--cyan);
  animation: dot-pulse 1.5s infinite;
}
@keyframes dot-pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }

.hunter-vitality-bars {
  width: 100%; max-width: 240px; margin-top: 14px;
  display: flex; flex-direction: column; gap: 6px;
}
.vit-row { display: flex; align-items: center; gap: 8px; font-family: var(--f-mono); font-size: 11px; }
.vit-label { width: 22px; font-weight: 700; color: var(--p5); }
.vit-track {
  flex: 1; height: 6px; background: rgba(255, 255, 255, 0.08);
  border-radius: 3px; overflow: hidden; position: relative;
  border: 1px solid rgba(157, 51, 255, 0.25);
}
.vit-fill { height: 100%; border-radius: 3px; transition: width 0.5s cubic-bezier(0.22, 1, 0.36, 1); }
.hp-fill { background: linear-gradient(90deg, #ff2255, #ff6b6b); box-shadow: 0 0 10px rgba(255, 34, 85, 0.6); }
.mp-fill { background: linear-gradient(90deg, #00bcd4, #00e5ff); box-shadow: 0 0 10px rgba(0, 229, 255, 0.6); }
.vit-val { width: 55px; text-align: right; color: var(--p6); font-size: 10px; }
```

**Add to `app.js` (Orbital Astrolabe Dial Engine):**
```javascript
// Continuous 60fps orbital telemetry dial
let orbitalAngle = 0;
function initOrbitalDial() {
  const canvas = document.getElementById('orbital-dial-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const cx = 110, cy = 110;

  function renderDial() {
    ctx.clearRect(0, 0, 220, 220);
    orbitalAngle += 0.008; // Continuous slow rotation

    // 1. Outer astrolabe coordinate ring
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(orbitalAngle);
    ctx.strokeStyle = 'rgba(0, 229, 255, 0.25)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(0, 0, 102, 0, Math.PI * 2);
    ctx.stroke();

    // Astrolabe tick marks and cardinal nodes
    for (let i = 0; i < 24; i++) {
      const a = (i * Math.PI) / 12;
      const r1 = i % 6 === 0 ? 94 : 98;
      ctx.beginPath();
      ctx.moveTo(Math.cos(a) * r1, Math.sin(a) * r1);
      ctx.lineTo(Math.cos(a) * 102, Math.sin(a) * 102);
      ctx.strokeStyle = i % 6 === 0 ? 'rgba(0, 229, 255, 0.8)' : 'rgba(157, 51, 255, 0.35)';
      ctx.lineWidth = i % 6 === 0 ? 2 : 1;
      ctx.stroke();
    }
    ctx.restore();

    // 2. Middle counter-rotating segmented telemetry ring
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(-orbitalAngle * 1.5);
    ctx.strokeStyle = 'rgba(157, 51, 255, 0.4)';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([8, 12]);
    ctx.beginPath();
    ctx.arc(0, 0, 84, 0, Math.PI * 2);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.restore();

    // 3. Segmented Vitality Arc (HP/MP Indicator on the dial itself)
    ctx.beginPath();
    ctx.arc(cx, cy, 70, -Math.PI * 0.75, Math.PI * 0.25);
    ctx.strokeStyle = 'rgba(0, 229, 255, 0.6)';
    ctx.lineWidth = 3;
    ctx.shadowColor = '#00e5ff';
    ctx.shadowBlur = 10;
    ctx.stroke();
    ctx.shadowBlur = 0;

    requestAnimationFrame(renderDial);
  }
  requestAnimationFrame(renderDial);
}

function updateHunterFeeling(feeling, mode = 'balanced') {
  const badge = document.getElementById('hunter-feeling-text');
  const aura = document.getElementById('holo-aura-pulse');
  if (badge) badge.textContent = feeling.toUpperCase();
  if (!aura) return;

  if (mode === 'overdrive') {
    aura.style.background = 'radial-gradient(circle, rgba(255,215,0,0.5) 0%, rgba(255,170,0,0.2) 60%, transparent 80%)';
  } else if (mode === 'recovery') {
    aura.style.background = 'radial-gradient(circle, rgba(255,34,85,0.4) 0%, rgba(123,0,204,0.2) 60%, transparent 80%)';
  } else {
    aura.style.background = 'radial-gradient(circle, rgba(157,51,255,0.35) 0%, rgba(0,229,255,0.15) 60%, transparent 80%)';
  }
}
```

---

### DIRECTIVE 8: Authentic "SYSTEM" Holographic Windows & Equipment Wireframe Matrix

Recreate the authentic floating holographic screens that Sung Jin-woo interacts with (bottom frames of `test.png`):
- Glowing top and bottom cyan energy brackets with running rune tickers
- High-refraction blue-violet glassmorphism with scanlines
- Diegetic Vector Wireframe Mannequin for Hunter Equipment & Matrix Inspection

**Add to `index.html` (Modal / Overlay template for SYSTEM Inspect):**
```html
<div id="system-holo-modal" class="system-holo-overlay" hidden>
  <div class="system-holo-frame">
    <!-- Top Holographic Energy Rail -->
    <div class="holo-rail rail-top">
      <div class="rail-bracket">[</div>
      <div class="rail-runes">᚛ ᚛ ᚛ SYSTEM OVERLAY :: HUNTER MATRIX :: S-RANK PROTOCOL ᚜ ᚜ ᚜</div>
      <div class="rail-bracket">]</div>
    </div>

    <!-- Main Glass Plate -->
    <div class="holo-glass-plate">
      <div class="holo-scanlines"></div>
      
      <!-- Left: Equipment Mannequin Matrix -->
      <div class="mannequin-sector">
        <div class="sector-title">EQUIPMENT</div>
        <div class="mannequin-wrap">
          <!-- Cyber Vector Mannequin SVG -->
          <svg class="cyber-mannequin-svg" viewBox="0 0 160 260">
            <!-- Head -->
            <circle cx="80" cy="30" r="14" class="mq-bone" />
            <!-- Torso & Core -->
            <path d="M 68 48 L 92 48 L 96 110 L 64 110 Z" class="mq-bone" />
            <!-- Limbs & Joints with cyan nodes -->
            <line x1="68" y1="52" x2="42" y2="105" class="mq-bone" />
            <line x1="92" y1="52" x2="118" y2="105" class="mq-bone" />
            <line x1="72" y1="110" x2="65" y2="200" class="mq-bone" />
            <line x1="88" y1="110" x2="95" y2="200" class="mq-bone" />
            <circle cx="80" cy="75" r="4" class="mq-core-node" />
          </svg>

          <!-- Angled HUD Trace Lines to Gear Slots -->
          <div class="gear-slot slot-helm" onclick="inspectGear('helm')">
            <span class="gear-icon">⛑</span>
            <div class="gear-meta"><span class="gear-name">Crimson Helm</span><span class="gear-tier s-rank">S-Rank</span></div>
          </div>
          <div class="gear-slot slot-chest" onclick="inspectGear('chest')">
            <span class="gear-icon">🛡</span>
            <div class="gear-meta"><span class="gear-name">Shadow Plate</span><span class="gear-tier a-rank">A-Rank</span></div>
          </div>
          <div class="gear-slot slot-daggers" onclick="inspectGear('daggers')">
            <span class="gear-icon">🗡</span>
            <div class="gear-meta"><span class="gear-name">Baruka's Dagger</span><span class="gear-tier s-rank">S-Rank</span></div>
          </div>
        </div>
      </div>

      <!-- Right: Item Detail & Stat Buff Telemetry -->
      <div class="item-detail-sector" id="item-detail-sector">
        <div class="item-badge s-rank">S-RANK ITEM</div>
        <div class="item-header" id="inspect-item-title">Crimson Knight's Helmet</div>
        <div class="item-stat-buff green">+20 VIT · +20 STR</div>
        <div class="item-desc" id="inspect-item-desc">
          Forged in the depths of the Demon Castle. Physical damage taken reduced by 20%. Increases Hunter presence aura.
        </div>
        <button class="tr-btn holo-btn" onclick="closeHoloModal()">ACKNOWLEDGE [ESC]</button>
      </div>
    </div>

    <!-- Bottom Holographic Energy Rail -->
    <div class="holo-rail rail-bottom">
      <div class="rail-bracket">[</div>
      <div class="rail-runes">◄ MONITORING BIOMETRICS :: AIR-GAPPED CORE :: PROTOCOL ACTIVE ►</div>
      <div class="rail-bracket">]</div>
    </div>
  </div>
</div>
```

**Add to `style.css`:**
```css
.system-holo-overlay {
  position: fixed; inset: 0; z-index: 920;
  background: rgba(4, 0, 10, 0.82); backdrop-filter: blur(12px);
  display: flex; align-items: center; justify-content: center;
  perspective: 1200px;
}
.system-holo-frame {
  width: 90%; max-width: 780px; position: relative;
  display: flex; flex-direction: column;
  animation: holo-spawn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes holo-spawn {
  0% { opacity: 0; transform: scale(0.92) rotateX(8deg); }
  100% { opacity: 1; transform: scale(1) rotateX(0deg); }
}

/* Authentic Holographic Rail Brackets */
.holo-rail {
  display: flex; align-items: center; justify-content: space-between;
  background: linear-gradient(90deg, transparent, rgba(0, 229, 255, 0.25), transparent);
  border-top: 2px solid var(--cyan); border-bottom: 2px solid var(--cyan);
  padding: 4px 16px; color: var(--cyan); text-shadow: 0 0 10px var(--cyan);
  font-family: var(--f-mono); font-size: 11px; letter-spacing: 2px;
}
.rail-bottom { margin-top: -2px; }
.rail-runes { font-size: 10px; opacity: 0.9; }

/* The Glass Plate */
.holo-glass-plate {
  position: relative; overflow: hidden;
  background: rgba(13, 0, 24, 0.88);
  border-left: 2px solid var(--cyan); border-right: 2px solid var(--cyan);
  box-shadow: inset 0 0 40px rgba(0, 229, 255, 0.15), 0 0 30px rgba(0, 229, 255, 0.2);
  padding: 24px; display: grid; grid-template-columns: 1.2fr 1fr; gap: 20px;
}
.holo-scanlines {
  position: absolute; inset: 0; pointer-events: none;
  background: repeating-linear-gradient(0deg, rgba(0,0,0,0) 0px, rgba(0,0,0,0) 2px, rgba(0,229,255,0.03) 3px, rgba(0,0,0,0) 4px);
  background-size: 100% 4px;
}

/* Cyber Mannequin */
.mannequin-wrap { position: relative; height: 260px; display: flex; justify-content: center; }
.cyber-mannequin-svg { height: 100%; stroke: var(--cyan); fill: none; filter: drop-shadow(0 0 8px rgba(0,229,255,0.5)); }
.mq-bone { stroke-width: 2; stroke: var(--cyan); stroke-dasharray: 6 3; }
.mq-core-node { fill: var(--cyan); filter: drop-shadow(0 0 6px var(--cyan)); }

.gear-slot {
  position: absolute; display: flex; align-items: center; gap: 8px;
  background: rgba(19, 0, 32, 0.9); border: 1px solid var(--border-bright);
  padding: 4px 10px; border-radius: 4px; cursor: pointer; transition: all 0.2s ease;
}
.gear-slot:hover { border-color: var(--cyan); box-shadow: 0 0 12px var(--cyan); transform: scale(1.05); }
.slot-helm { top: 20px; left: 10px; }
.slot-chest { top: 90px; right: 10px; }
.slot-daggers { bottom: 30px; left: 10px; }
.gear-tier.s-rank { color: var(--gold); text-shadow: 0 0 8px var(--gold); font-weight: 700; }

.item-stat-buff.green {
  font-family: var(--f-mono); font-size: 15px; color: var(--green);
  text-shadow: 0 0 10px var(--green); margin: 10px 0;
}
```

**Add to `app.js` (Holographic Modal Controller):**
```javascript
function openHoloModal(type = 'equipment') {
  const modal = document.getElementById('system-holo-modal');
  if (modal) modal.removeAttribute('hidden');
}
function closeHoloModal() {
  const modal = document.getElementById('system-holo-modal');
  if (modal) modal.setAttribute('hidden', '');
}
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeHoloModal();
});
```

---

## NEW API ENDPOINTS REQUIRED

Add these to `server.py`:

```python
# In do_GET routing — add:
elif self.path.startswith("/api/neural/state"):
    self.serve_neural_state()
elif self.path.startswith("/api/quests/boss/active"):
    self.serve_active_boss_quest()

# In do_POST routing — add:
elif self.path.startswith("/api/accountability/submit"):
    self.handle_accountability_submit()

# Implementations:
def serve_neural_state(self):
    from quests.predictive_engine import predictive_engine
    fatigue = predictive_engine.calculate_fatigue_index()
    op_mode = predictive_engine.get_operational_mode(fatigue_index=fatigue)
    windows = predictive_engine.get_circadian_peak_and_slump()
    self._json_response({"fatigue_index": round(fatigue, 3), "operational_mode": op_mode.lower(), **windows})

def serve_active_boss_quest(self):
    from datetime import date
    boss = database_manager.fetch_one(
        "SELECT title, description, target_date FROM quests "
        "WHERE category='boss' AND status IN ('pending','in_progress') AND target_date >= ? "
        "ORDER BY target_date ASC LIMIT 1", (date.today().isoformat(),))
    self._json_response(dict(boss) if boss else {"active": False})

def handle_accountability_submit(self):
    length = int(self.headers.get('Content-Length', 0))
    body = json.loads(self.rfile.read(length))
    statement = body.get("statement", "").strip()
    if len(statement) < 150:
        self._json_response({"success": False, "error": "Too short"}, 400)
        return
    from automation.midnight_enforcer import MidnightEnforcer
    enforcer = MidnightEnforcer()
    from datetime import datetime
    database_manager.execute(
        "INSERT INTO shadow_journal (content, category, created_at) VALUES (?,?,?)",
        (statement, "accountability", datetime.now().isoformat()))
    enforcer._set_accountability_due(False)
    enforcer._reset_miss_streak()
    self._json_response({"success": True})

def _json_response(self, data: dict, status: int = 200):
    """Add this utility method to DashboardRequestHandler."""
    body = json.dumps(data).encode("utf-8")
    self.send_response(status)
    self.send_header("Content-Type", "application/json")
    self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
    self.end_headers()
    self.wfile.write(body)
```

---

## CODING STANDARDS

### Python
- Type hints on all new public functions
- No bare `except:` — always `except Exception as e:`
- Air-gapped modules: include guarantee comment block at top of file
- SQLite: always use `database_manager.execute()` / `fetch_all()` / `fetch_one()`
- All new API endpoints use `self._json_response()` helper

### JavaScript
- No ES modules, no external libraries beyond three.min.js
- All fetch calls wrapped in `try/catch` with graceful degradation
- Canvas: always `clearRect()` before re-drawing
- Animations: `requestAnimationFrame()` — never `setInterval()` for visuals
- DOM: null-check every element before access (`if (!el) return;`)

### CSS
- All new styles use token variables — no hardcoded hex colors
- All transitions: 0.2s min, 0.6s max (except cinematics)
- Glows: `text-shadow` for text, `box-shadow` for boxes — never `filter: drop-shadow`
- Mobile first, breakpoint at 768px

---

## ABSOLUTE PROHIBITIONS

1. Never introduce React, Vue, Svelte, Angular, or any JS framework
2. Never add Bootstrap, Tailwind, or any CSS framework
3. Never send financial/personal data to external APIs
4. Never change design tokens without updating all usages
5. Never remove or rename existing API endpoints — only add new ones
6. Never add features before fixing existing bugs
7. Never use `alert()`, `confirm()`, `prompt()` — build custom HUD dialogs

---

## FILE LOCATIONS QUICK REFERENCE

| Component | File |
|---|---|
| Main HTML | `dashboard/static/index.html` |
| All CSS | `dashboard/static/style.css` |
| All Frontend JS | `dashboard/static/app.js` |
| REST Server | `dashboard/server.py` |
| XP System | `quests/xp.py` |
| Quest Service | `quests/service.py` |
| Predictive Engine | `quests/predictive_engine.py` |
| Midnight Enforcer | `automation/midnight_enforcer.py` |
| Focus Guard | `automation/focus_guard.py` |
| Treasury Brain | `voice/treasury_brain.py` |
| Financial Classifier | `core/local_transaction_classifier.py` |
| Bank Importer | `core/bank_statement_importer.py` |
| Database Manager | `storage/db.py` |
| CFO Modelfile | `storage/Modelfile.apex-cfo` |
| Ollama Client | `automation/ollama_client.py` |

---

*This AGENTS.md is the living memory of Claude CLI on this project.*
*Every session starts here. Every decision defers to this document.*
*Build like a craftsman. Ship like a soldier.*
