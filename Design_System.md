# APEX GHOST PROTOCOL — DESIGN SYSTEM
> Version: 2.0 | Aesthetic: Gothic Dark Fantasy · Shadow Monarch · Cyberpunk

---

## RULE ZERO — READ BEFORE WRITING ANY UI CODE

Every visual decision in this system must answer YES to two questions:
1. **Does it glow?** — Active, selected, and important elements must emit light.
2. **Does it feel alive?** — Even at idle, the HUD must breathe, pulse, and shift.

If your component is flat, static, or uses a plain color — it is wrong. Fix it.

---

## 1. COLOR TOKENS

All colors are defined as CSS custom properties on `:root`. **Never hardcode hex values.**
Always reference tokens. This ensures global theme changes (e.g., Penalty Zone red takeover) work correctly.

### 1.1 Background Depths
```css
:root {
  --bg0: #070010;   /* Deepest void — main page background */
  --bg1: #0d0018;   /* Base background layer */
  --bg2: #130020;   /* Standard panel background */
  --bg3: #1a002e;   /* Elevated panel (cards, overlays) */
  --bg4: #220040;   /* Highlighted / focused panel */
}
```
**Usage rule:** Use `--bg0` for page, `--bg2` for cards, `--bg3` for elevated elements, `--bg4` for active/hover states.

### 1.2 Purple Family (Primary Brand Color)
```css
:root {
  --p0: #2d005a;   /* Deep shadow purple */
  --p1: #4b008c;   /* Core purple */
  --p2: #7b00cc;   /* Glow purple */
  --p3: #9d33ff;   /* Active purple — borders, icons */
  --p4: #bb66ff;   /* Light purple — secondary text */
  --p5: #d499ff;   /* Pale purple — body text */
  --p6: #e8c8ff;   /* Near-white purple — primary text */
}
```

### 1.3 Accent Colors
```css
:root {
  --gold:  #ffd700;   /* Wealth, assets, gold tier */
  --gold2: #ffaa00;   /* Gold glow, secondary gold */
  --cyan:  #00e5ff;   /* Data, focus, information */
  --cyan2: #00bcd4;   /* Cyan depth, glow base */
  --red:   #ff2255;   /* Danger, penalty, failure */
  --green: #00ff88;   /* Success, completion, health */
  --pink:  #ff44cc;   /* Special, rare, legendary */
}
```

### 1.4 Stat Colors (Attribute-Specific)
```css
:root {
  --c-str: #ff6b6b;   /* Strength — warm red */
  --c-int: #44ddff;   /* Intelligence — bright cyan */
  --c-agi: #44ff99;   /* Agility — neon green */
  --c-dis: #ffd700;   /* Discipline — gold */
  --c-foc: #cc88ff;   /* Focus — soft purple */
}
```

### 1.5 Pre-Built Glow Helpers
```css
:root {
  --g-p:    0 0 8px var(--p3),  0 0 24px var(--p2),  0 0 48px rgba(123,0,204,.3);
  --g-gold: 0 0 8px var(--gold), 0 0 20px var(--gold2);
  --g-cyan: 0 0 8px var(--cyan), 0 0 20px var(--cyan2);
  --g-red:  0 0 8px var(--red),  0 0 20px rgba(255,34,85,.4);
}
```

### 1.6 Border System
```css
:root {
  --border:        rgba(155,51,255,0.28);   /* Standard panel border */
  --border-bright: rgba(187,102,255,0.5);   /* Active / hover border */
  --border-gold:   rgba(255,215,0,0.4);     /* Treasury / wealth elements */
  --border-red:    rgba(255,34,85,0.4);     /* Penalty / danger elements */
  --border-cyan:   rgba(0,229,255,0.3);     /* Focus / data elements */
}
```

---

## 2. TYPOGRAPHY

### 2.1 Font Stack
```css
:root {
  --f-title: 'Cinzel Decorative', serif;   /* Main titles, overlays, cinematics */
  --f-head:  'Cinzel', serif;              /* Panel headings, labels, badges */
  --f-body:  'Rajdhani', sans-serif;       /* Body text, descriptions, quest titles */
  --f-mono:  'Share Tech Mono', monospace; /* Numbers, XP values, timestamps, code */
}
```

### 2.2 Typography Hierarchy
```
Level 1 — Page Titles          font: var(--f-title), 24–32px, letter-spacing: 4px
Level 2 — Section Titles       font: var(--f-head),  14–18px, letter-spacing: 2–3px
Level 3 — Panel Headings       font: var(--f-head),  11–13px, letter-spacing: 1.5–2px
Level 4 — Body Text            font: var(--f-body),  13–15px, letter-spacing: 0.5px
Level 5 — Data / Numbers       font: var(--f-mono),  12–28px, letter-spacing: 0
Level 6 — Labels / Badges      font: var(--f-head),  8–10px,  letter-spacing: 2px, UPPERCASE
```

### 2.3 Usage Examples
```css
/* Main HUD title */
.sys-big-title {
  font-family: var(--f-title);
  font-size: 20px;
  letter-spacing: 4px;
  color: var(--p4);
  text-shadow: var(--g-p);
}

/* Panel title */
.panel-title {
  font-family: var(--f-head);
  font-size: 11px;
  letter-spacing: 2px;
  color: var(--p4);
  text-transform: uppercase;
}

/* XP number */
.xp-val {
  font-family: var(--f-mono);
  font-size: 13px;
  color: var(--p5);
}

/* Large data display */
.fatigue-pct {
  font-family: var(--f-mono);
  font-size: 28px;
  font-weight: 700;
  color: var(--cyan);
  text-shadow: var(--g-cyan);
}
```

---

## 3. SPACING & LAYOUT

### 3.1 Layout Constants
```css
:root {
  --hdr-h: 56px;    /* Header height */
  --nav-h: 58px;    /* Nav bar height */
}

/* Main grid: 3-column layout */
.main-content {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 10px;
  padding: 10px;
  height: calc(100vh - var(--hdr-h) - var(--nav-h));
  overflow: hidden;
}
```

### 3.2 Panel Spacing Rules
```
Panel padding:       12–16px
Panel gap (internal): 10–12px
Card border-radius:  8–10px
Button padding:      6px 16px (small) | 10px 20px (standard)
Icon margin-right:   6–8px
Section gap:         16–20px
```

### 3.3 Z-Index Layering
```
Background canvas:   z-index: 0
Vignette:            z-index: 1
App content:         z-index: 2
Nav bar:             z-index: 10
Toast notifications: z-index: 900
Overlays:            z-index: 800
Penalty Zone:        z-index: 950
Boot overlay:        z-index: 1000
Level Up cinematic:  z-index: 990
```

---

## 4. COMPONENT LIBRARY

### 4.1 Panel (Base Card)
Every section is a `.panel` — the fundamental building block of the HUD.
```css
.panel {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px 14px;
  position: relative;
  overflow: hidden;
}

/* Subtle top-edge highlight (depth illusion) */
.panel::before {
  content: '';
  position: absolute;
  top: 0; left: 10%; right: 10%;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--p2), transparent);
}
```

### 4.2 Panel Title
```css
.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: var(--f-head);
  font-size: 11px;
  letter-spacing: 2px;
  color: var(--p4);
  text-transform: uppercase;
  margin-bottom: 12px;
}

.pt-glyph {
  color: var(--p3);
  font-size: 8px;
}
```

### 4.3 Primary Button
```css
.tr-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 16px;
  background: linear-gradient(135deg, var(--p1), var(--p0));
  border: 1px solid var(--border-bright);
  border-radius: 5px;
  color: var(--p5);
  font-family: var(--f-head);
  font-size: 11px;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 100%;
}

.tr-btn:hover {
  background: linear-gradient(135deg, var(--p2), var(--p1));
  border-color: var(--p3);
  color: var(--p6);
  box-shadow: 0 0 16px rgba(123,0,204,0.4), inset 0 1px 0 rgba(187,102,255,0.2);
}

.tr-btn:active {
  transform: scale(0.97);
}
```

### 4.4 Secondary Button
```css
.tr-btn.secondary {
  background: transparent;
  border-color: var(--border);
  color: var(--p4);
}

.tr-btn.secondary:hover {
  background: rgba(155,51,255,0.1);
  border-color: var(--p3);
  box-shadow: 0 0 12px rgba(123,0,204,0.2);
}
```

### 4.5 Nav Button
```css
.nav-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  padding: 6px 12px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 6px;
  color: var(--p4);
  font-family: var(--f-head);
  font-size: 9px;
  letter-spacing: 1.5px;
  transition: all 0.2s ease;
  cursor: pointer;
}

.nav-btn:hover {
  color: var(--p6);
  border-color: var(--border);
  background: rgba(155,51,255,0.08);
}

.nav-btn.active {
  color: var(--p3);
  border-color: var(--border-bright);
  background: rgba(123,0,204,0.12);
  box-shadow: 0 0 12px rgba(123,0,204,0.2);
}
```

### 4.6 Input Fields
```css
.tr-input {
  width: 100%;
  padding: 8px 12px;
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: 5px;
  color: var(--p5);
  font-family: var(--f-mono);
  font-size: 13px;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.tr-input:focus {
  border-color: var(--p3);
  box-shadow: 0 0 0 2px rgba(123,0,204,0.15), 0 0 8px rgba(157,51,255,0.2);
  outline: none;
}

.tr-input::placeholder {
  color: var(--p2);
  opacity: 0.6;
}
```

### 4.7 Toast Notification
```css
.toast {
  background: var(--bg3);
  border: 1px solid var(--border-bright);
  border-left: 3px solid var(--p3);
  border-radius: 6px;
  padding: 10px 14px;
  min-width: 260px;
  max-width: 340px;
  font-family: var(--f-mono);
  font-size: 12px;
  color: var(--p5);
  backdrop-filter: blur(12px);
  transform: translateX(120%);
  opacity: 0;
  transition: transform 0.35s cubic-bezier(0.22,1,0.36,1), opacity 0.35s ease;
  box-shadow: 0 4px 24px rgba(123,0,204,0.25), inset 0 1px 0 rgba(187,102,255,0.1);
}

/* Toast type variants */
.toast.toast-xp      { border-left-color: var(--gold); }
.toast.toast-rank    { border-left-color: var(--cyan); }
.toast.toast-penalty { border-left-color: var(--red); }
.toast.toast-quest   { border-left-color: var(--green); }
.toast.toast-info    { border-left-color: var(--p3); }
```

### 4.8 Stat Bar
```css
/* Skill / attribute progress bar */
.sk-bar-wrap {
  flex: 1;
  height: 4px;
  background: rgba(155,51,255,0.15);
  border-radius: 2px;
  overflow: hidden;
}

.sk-bar {
  height: 100%;
  border-radius: 2px;
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

/* Shimmer animation on bar */
.sk-bar::after {
  content: '';
  position: absolute;
  top: 0; right: 0;
  width: 20px;
  height: 100%;
  background: rgba(255,255,255,0.4);
  filter: blur(4px);
  animation: bar-shimmer 2s ease-in-out infinite;
}

@keyframes bar-shimmer {
  0%, 100% { opacity: 0; }
  50% { opacity: 1; }
}
```

---

## 5. ANIMATION LIBRARY

### 5.1 Standard Micro-Animations
```css
/* Gentle pulse — for rank badge, important numbers */
@keyframes apex-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.85; transform: scale(0.98); }
}

/* Shimmer — for XP bar, loading states */
@keyframes shimmer-slide {
  from { transform: translateX(-100%); }
  to   { transform: translateX(200%); }
}

/* Breathing glow — for active elements */
@keyframes glow-breathe {
  0%, 100% { box-shadow: 0 0 8px rgba(157,51,255,0.3); }
  50%       { box-shadow: 0 0 20px rgba(157,51,255,0.6), 0 0 40px rgba(123,0,204,0.3); }
}

/* Gold pulse — for OVERDRIVE mode */
@keyframes pulse-gold {
  0%, 100% { box-shadow: 0 0 12px rgba(255,215,0,0.3); }
  50%       { box-shadow: 0 0 24px rgba(255,215,0,0.6), 0 0 40px rgba(255,170,0,0.3); }
}

/* Penalty flicker — for Penalty Zone overlay */
@keyframes penalty-flicker {
  0%, 100% { background: rgba(10,0,0,0.97); }
  50% { background: rgba(20,0,0,0.97); box-shadow: inset 0 0 120px rgba(255,34,85,0.08); }
}

/* Boss pulse — for Boss Quest timer border */
@keyframes boss-pulse {
  0%, 100% { border-color: rgba(255,34,85,0.4); }
  50% { border-color: rgba(255,34,85,0.8); box-shadow: 0 0 20px rgba(255,34,85,0.2); }
}

/* Fade up — for quest cards appearing */
@keyframes fade-up {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Scan line — for boot sequence effect */
@keyframes scan-line {
  from { top: -2px; }
  to   { top: 100%; }
}
```

### 5.2 Animation Usage Guidelines
| Animation | Use Case | Duration |
|---|---|---|
| `apex-pulse` | Rank badge, live indicators | 3s infinite |
| `shimmer-slide` | XP bar, loading states | 2s infinite |
| `glow-breathe` | Active nav button, focused inputs | 3s infinite |
| `pulse-gold` | OVERDRIVE mode badge | 2s infinite |
| `penalty-flicker` | Penalty Zone full-screen | 4s infinite |
| `boss-pulse` | Boss Quest timer | 3s infinite |
| `fade-up` | Quest cards, toast notifications | 0.3s once |
| `scan-line` | Boot overlay, cinematic transitions | 2s 3× |

### 5.3 Transition Standards
```css
/* Standard hover transition — all interactive elements */
transition: all 0.2s ease;

/* Smooth layout shift — bars, progress */
transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);

/* Overlay slide-in */
transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.3s ease;

/* Toast slide */
transition: transform 0.35s cubic-bezier(0.22, 1, 0.36, 1), opacity 0.35s ease;
```

---

## 6. CANVAS RENDERING GUIDELINES

All canvas elements use the same palette. When drawing, reference these exact values:

### 6.1 Standard Canvas Colors
```javascript
const CANVAS_COLORS = {
  // Background rings / tracks
  trackBg:    'rgba(155,51,255,0.15)',
  trackBgDim: 'rgba(155,51,255,0.08)',
  
  // Active fills
  purple:     '#9d33ff',
  gold:       '#ffd700',
  cyan:       '#00e5ff',
  red:        '#ff2255',
  green:      '#00ff88',
  
  // Stat colors
  str:        '#ff6b6b',
  int:        '#44ddff',
  agi:        '#44ff99',
  dis:        '#ffd700',
  foc:        '#cc88ff',
  
  // Text
  textPrimary: '#e8c8ff',
  textDim:     '#bb66ff',
};
```

### 6.2 Glow Rendering on Canvas
```javascript
// Always apply, then clear shadowBlur after stroke
ctx.shadowColor = color;
ctx.shadowBlur = 16;
ctx.stroke(); // or ctx.fill()
ctx.shadowBlur = 0; // CRITICAL — must reset or all subsequent draws glow
```

### 6.3 Canvas Animation Pattern
```javascript
// Use requestAnimationFrame — NEVER setInterval for visual updates
function animateCanvas() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawFrame(); // your drawing logic
  requestAnimationFrame(animateCanvas);
}
requestAnimationFrame(animateCanvas);
```

---

## 7. OVERLAY SYSTEM

### 7.1 Full-Screen Overlay Template
```css
.full-overlay {
  position: fixed;
  inset: 0;
  z-index: 800;
  background: rgba(7,0,16,0.97);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  animation: overlay-fade-in 0.3s ease;
}

@keyframes overlay-fade-in {
  from { opacity: 0; }
  to   { opacity: 1; }
}
```

### 7.2 Overlay Header Template
```css
.ov-head {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  background: var(--bg2);
  position: sticky;
  top: 0;
  z-index: 1;
}

.ov-title {
  font-family: var(--f-title);
  font-size: 16px;
  letter-spacing: 3px;
  color: var(--p4);
  text-shadow: var(--g-p);
}

.ov-back {
  padding: 5px 12px;
  background: transparent;
  border: 1px solid var(--border);
  border-radius: 4px;
  color: var(--p4);
  font-family: var(--f-head);
  font-size: 10px;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.ov-back:hover {
  border-color: var(--p3);
  color: var(--p6);
  box-shadow: 0 0 8px rgba(123,0,204,0.3);
}
```

---

## 8. RANK BADGE SYSTEM

Rank badges use specific colors to convey tier. Each rank has its own glow.

```javascript
const RANK_STYLES = {
  'E': { bg: '#1a0030', border: 'rgba(155,51,255,0.4)', color: '#9d33ff', glow: 'rgba(123,0,204,0.3)' },
  'D': { bg: '#001a1a', border: 'rgba(0,188,212,0.5)',  color: '#00e5ff', glow: 'rgba(0,188,212,0.3)' },
  'C': { bg: '#001a00', border: 'rgba(0,200,100,0.5)',  color: '#00ff88', glow: 'rgba(0,200,100,0.3)' },
  'B': { bg: '#1a1500', border: 'rgba(255,200,0,0.5)',  color: '#ffd700', glow: 'rgba(255,170,0,0.3)' },
  'A': { bg: '#1a0a00', border: 'rgba(255,140,0,0.5)',  color: '#ff8c00', glow: 'rgba(255,100,0,0.3)' },
  'S': { bg: '#1a0010', border: 'rgba(255,68,204,0.6)', color: '#ff44cc', glow: 'rgba(255,44,180,0.4)' },
};
```

---

## 9. WHAT IS FORBIDDEN

These patterns break the design language and must NEVER appear:

```
❌ Hardcoded hex colors (#fff, #000, #333)
❌ White backgrounds or light panels
❌ Plain colored buttons (no glow, no border)
❌ Default browser fonts (Arial, Helvetica)
❌ Flat progress bars (no shimmer, no glow)
❌ Sharp corners on cards (always border-radius)
❌ Static rank badges (must pulse)
❌ Plain text numbers (XP/stats need font-mono + color)
❌ Transitions faster than 0.15s or slower than 0.6s
❌ filter: drop-shadow (use box-shadow for performance)
❌ alert(), confirm(), prompt() — always use HUD dialogs
❌ External CSS libraries (Bootstrap, Tailwind, etc.)
```
