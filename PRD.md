# APEX GHOST PROTOCOL — PRODUCT REQUIREMENTS DOCUMENT (PRD)
> Version: 2.0 | Status: Active Development | Last Updated: October 2026

---

## 1. PRODUCT OVERVIEW

### 1.1 Product Vision
Apex Ghost Protocol is a **local-first, air-gapped, autonomous discipline enforcement system** — a personal AI Operating System that enforces high-performance habits with real, escalating consequences. Inspired by the Solo Leveling universe, it treats the user as a Hunter leveling up through real-world achievements.

**Tagline:** *"The system that fights back."*

### 1.2 Mission Statement
Most productivity tools are passive, polite, and trivially easy to cheat. Apex Ghost Protocol is the antithesis: a hostile, consequence-driven AI that refuses XP unless evidence passes AI scrutiny, locks the machine when quests are missed, and deploys a CFO-grade financial auditor — all 100% on-device.

### 1.3 Target Users
| Persona | Description | Pain Point |
|---|---|---|
| **The High-Performer** | Developer / engineer / student | Lacks accountability system that fights back |
| **The Biohacker** | Fitness + productivity optimizer | No tool ties physical output to digital rewards |
| **The Self-Hosted Dev** | r/selfhosted, r/unixporn audience | All productivity tools require cloud/subscriptions |
| **The Solo Leveling Fan** | Anime/manhwa enthusiast + productivity seeker | No real-world system captures that universe |
| **The SA Professional** | South African knowledge worker | No local-first finance tool understands SA banking |

---

## 2. CORE FEATURE REQUIREMENTS

### 2.1 The Quest System (CORE)
**Priority: P0 — Must Ship**

| Feature | Requirement | Status |
|---|---|---|
| Daily Quest Generation | AI generates 3–8 quests per day based on goals + fatigue | ✅ Built |
| Quest Categories | CORE / BOSS / HABIT / SIDE — with different penalty weights | ✅ Built |
| Quest Completion | Mark complete via CLI or HUD toggle | ✅ Built |
| Evidence Requirement | BOSS quests require text/image/git proof before XP awarded | ✅ Built (text only) |
| Evidence — Vision AI | Submit gym selfie → local LLaVA verifies it | 🔴 Not built |
| Evidence — Git Commits | Submit commit hash → verifier checks diff lines | 🔴 Not built |
| Dynamic Difficulty (DDA) | Fatigue index scales quest count + difficulty automatically | ✅ Built |
| Quest Chaining | Completing Quest A unlocks Quest B | 🟡 Partial |
| Boss Raid (Co-op) | 4–10 users share a dungeon — one fails, all take damage | 🔴 Not built |

### 2.2 The XP & Rank System (CORE)
**Priority: P0 — Must Ship**

| Feature | Requirement | Status |
|---|---|---|
| XP Accumulation | Add XP on quest completion | ✅ Built |
| XP Decay / Penalty | Deduct XP on quest miss | ✅ Built |
| Rank Progression | E → D → C → B → A → S tier advancement | ✅ Built |
| Level System | Level = XP / 1000 threshold | ✅ Built |
| Rank Gate Exams | D→C requires 48h challenge; B→A requires 30-day sprint | 🔴 Not built |
| Level Up Cinematic | Three.js particle burst on level up | ✅ Built |
| Stat Decay | Attributes decay if inactive | ✅ Built |
| Attribute Matrix | STR / INT / AGI / DIS / FOC — tracked & displayed | ✅ Built |

### 2.3 The Midnight Enforcer (CORE)
**Priority: P0 — Must Ship**

| Feature | Requirement | Status |
|---|---|---|
| Tier 1 Enforcement | 1st miss: XP penalty + JARVIS voice callout | ✅ Built |
| Tier 2 Enforcement | 2nd miss: Tier 1 + Focus Guard activates (2h block) | ✅ Built |
| Tier 3 Enforcement | 3rd miss: Machine hostile until accountability submitted | ✅ Built |
| Recovery Quest | Auto-spawns redemption quest after any failure | ✅ Built |
| Accountability Gate | System boot blocked until 150-char statement submitted | ✅ Built |
| Task Scheduler Hook | Fires automatically at 23:45 via Windows Task Scheduler | ✅ Built |

### 2.4 The Focus Guard (CORE)
**Priority: P0 — Must Ship**

| Feature | Requirement | Status |
|---|---|---|
| Process Kill | Terminates blacklisted apps (Discord, Steam, etc.) | ✅ Built (Win32) |
| Hosts File Block | Redirects distracting domains to 127.0.0.1 | ✅ Built (Windows) |
| JARVIS Voice Warning | Speaks when a blocked app is closed | ✅ Built |
| macOS Support | Use `pkill` + `scutil` on macOS | 🔴 Not built |
| Linux Support | Use `xdotool` + `systemctl` on Linux | 🔴 Not built |
| Focus Timer | Countdown displayed in HUD during active session | 🟡 Partial |

### 2.5 The J.A.R.V.I.S. Voice System (CORE)
**Priority: P0 — Must Ship**

| Feature | Requirement | Status |
|---|---|---|
| Morning Briefing | TTS reads: rank, streak, quests, north star | ✅ Built |
| Penalty Callout | Voice announces failures at 23:45 | ✅ Built |
| Treasury Briefing | Voice reads financial runway update | ✅ Built |
| Windows SAPI TTS | pyttsx3 / Windows Speech API | ✅ Built |
| Jinwoo Voice Pack | Custom Solo Leveling character voice | 🟡 Stub |
| JARVIS Voice Pack | Movie-accurate Tony Stark JARVIS voice | 🔴 Not built (Pro tier) |

### 2.6 The Awakening Protocol (CORE)
**Priority: P1**

| Feature | Requirement | Status |
|---|---|---|
| Volume Ramp | Gradually raises system volume from 30% → 100% | ✅ Built |
| VLC Video Queue | Plays motivational MP4s at full screen | ✅ Built |
| Asset Registry | JSON config for video paths | ✅ Built |
| JARVIS Post-Briefing | Morning stats read aloud after videos | ✅ Built |
| Non-VLC Fallback | Uses OS default player if VLC not installed | ✅ Built |
| Cross-Platform | macOS/Linux awakening support | 🔴 Not built |

### 2.7 The Treasury System (CORE)
**Priority: P1**

| Feature | Requirement | Status |
|---|---|---|
| Transaction Logging | Manual income/expense entry via HUD | ✅ Built |
| CSV Bank Import | Parse SA bank statements (multi-format) | ✅ Built |
| PII Scrubbing | On-device redaction before any processing | ✅ Built |
| Local ML Classifier | TF-IDF + NaiveBayes auto-categorises transactions | ✅ Built |
| Deterministic Rules | SA vendor catalog (Woolworths, EasyEquities, etc.) | ✅ Built |
| apex-cfo AI Audit | Local Ollama CFO model audits spending | ✅ Built |
| Kiyosaki Ratios | Asset % / Liability % / Waste % tracked | ✅ Built |
| Wealth Trajectory | 12-month cashflow projection chart | 🔴 Not built |
| OFX Parser | FNB/ABSA OFX format support | 🔴 Not built |
| PDF Statement Parser | Banks that only export PDF | 🔴 Not built |

### 2.8 The Predictive Engine (CORE)
**Priority: P1**

| Feature | Requirement | Status |
|---|---|---|
| Focus Probability | RandomForest predicts success % by hour | ✅ Built |
| Fatigue Index | Composite score from session history + wake-ups | ✅ Built |
| Operational Mode | BALANCED / OVERDRIVE / ACTIVE_RECOVERY | ✅ Built |
| Circadian Windows | Identifies 2h peak and 3h slump daily | ✅ Built |
| HUD Display | Neural State panel shows fatigue ring + mode | 🔴 Not built (HUD only) |

### 2.9 The HUD Dashboard (P0 — HIGHEST VISUAL PRIORITY)
**Priority: P0**

| Feature | Requirement | Status |
|---|---|---|
| Cyberpunk Boot Sequence | Sigil canvas + animated progress bar | ✅ Built |
| Background Particle Field | Three.js particle canvas | ✅ Built |
| Radar Chart | Live attributes plotted as animated spider chart | ✅ Built |
| XP Bar | Animated fill with shimmer effect | ✅ Built |
| Rank Badge | Cyberpunk rank gem (E/D/C/B/A/S) | ✅ Built |
| Health Grid | HP/MP/stats as pixel-block grid | ✅ Built |
| Goal Completion % | Today's contract clear rate | ✅ Built |
| Treasury Panel | Income, Runway, Frugality Score | ✅ Built |
| Capital Reactor | Donut chart (assets/liabilities/waste/income) | ✅ Built |
| Intel Globe | Three.js rotating globe for market intelligence | ✅ Built |
| WebSocket Real-Time | Live push updates (no 8-second poll lag) | 🔴 Not built |
| Toast Notifications | In-HUD event toasts (XP gain, penalty, rank) | 🔴 Not built |
| Neural State Panel | Fatigue gauge + Op Mode badge + focus windows | 🔴 Not built |
| Penalty Zone Overlay | Hostile red lockout overlay with statement input | 🔴 Not built |
| Boss Quest Timer | Live countdown in header for active boss quest | 🔴 Not built |
| Wealth Trajectory | 12-month line chart in Treasury | 🔴 Not built |

---

## 3. NON-FUNCTIONAL REQUIREMENTS

### 3.1 Privacy & Security
- **NFR-01:** Zero financial data transmitted outside localhost. Guaranteed.
- **NFR-02:** All PII (card numbers, account numbers, SA ID numbers) scrubbed on-device before storage or processing.
- **NFR-03:** Ollama models run entirely on localhost:11434. No cloud API calls.
- **NFR-04:** Optional AWS S3 sync must use client-side encryption before upload.

### 3.2 Performance
- **NFR-05:** HUD must render at 60 FPS on a mid-range machine (8GB RAM, integrated GPU).
- **NFR-06:** API responses must complete under 500ms for all GET endpoints.
- **NFR-07:** Boot sequence must complete in under 3 seconds.
- **NFR-08:** WebSocket events must be received and rendered within 100ms of firing.

### 3.3 Reliability
- **NFR-09:** If Ollama is offline, all AI features must degrade gracefully to deterministic fallbacks.
- **NFR-10:** If WebSocket is unavailable, HUD must fall back to polling without user intervention.
- **NFR-11:** Midnight enforcer must fire even if the dashboard is closed.

### 3.4 Installability
- **NFR-12:** Full setup must complete in under 5 minutes on a machine with Python installed.
- **NFR-13:** A one-line PowerShell installer must handle all setup steps automatically.
- **NFR-14:** System must function without VLC (graceful fallback to OS default player).

---

## 4. MONETIZATION MODEL

### 4.1 Tier Structure
```
FREE (Open Source / Self-Hosted)
├── Full local desktop system
├── CLI + HUD dashboard
├── All enforcement mechanics
├── Local AI anti-cheat (text only)
├── Treasury with SA bank classifier
└── J.A.R.V.I.S. (system voices only)

APEX CLOUD PRO ($15/month)
├── Cloud Vision AI (no local GPU required)
├── Multi-device sync (E2E encrypted)
├── Mobile companion app (iOS/Android)
├── Premium voice packs (JARVIS / Jinwoo)
├── Weekly AI coach report
└── Advanced biometric integration

ENTERPRISE / GUILDS ($99+/month)
├── Team dashboards
├── Boss Raid co-op (up to 50 hunters)
├── HR accountability integrations
└── Custom branding

HARDWARE ($149–$299 one-time)
└── Apex Cyber-Deck desk companion device
```

### 4.2 Wager Platform (Phase 3)
- Users lock $50–$200 into 30-day transformation sprint pool
- AI verifies daily quest completion via evidence
- Winners split the pool from those who failed (5% platform take-rate)

---

## 5. GO-TO-MARKET

### 5.1 Launch Communities
- `r/sololeveling` — "I built the Solo Leveling system in real life"
- `r/selfhosted` — "Air-gapped local AI discipline OS"
- `r/unixporn` — "My cyberpunk HUD that locks me out when I miss quests"
- `r/Python` — "Built an autonomous J.A.R.V.I.S. that enforces my goals"
- Twitter/X, TikTok Dev — 90-second demo video

### 5.2 Success Milestones
| Milestone | Metric | Timeline |
|---|---|---|
| Viral demo | 50K video views | Month 1 |
| Community | 1K GitHub stars | Month 2 |
| Traction | 500 active users | Month 3 |
| Revenue | $1K MRR | Month 4 |
| Growth | $10K MRR | Month 8 |
| Fundable | $100K ARR | Month 12 |

---

## 6. OUT OF SCOPE (Current Version)

- Mobile native app (companion app is Pro tier, future)
- Windows-to-macOS/Linux porting (abstraction layer required first)
- Multiplayer Boss Raids (requires backend infrastructure)
- Biometric hardware integration (Garmin/WHOOP/Apple Health)
- Payment processing / Stripe integration (post-500 users)
