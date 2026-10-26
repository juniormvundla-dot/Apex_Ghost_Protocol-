# APEX GHOST PROTOCOL — SYSTEM ARCHITECTURE
> Version: 2.0 | Stack: Python 3.10+ · SQLite3 · Vanilla JS · Three.js · Ollama

---

## 1. SYSTEM OVERVIEW

Apex Ghost Protocol is a **monolithic local-first application** running entirely on the user's machine. There is no cloud backend, no external database, and no external API dependency for core functionality. All AI inference happens through Ollama on `localhost:11434`.

```
┌─────────────────────────────────────────────────────────┐
│                  USER'S LOCAL MACHINE                   │
│                                                         │
│  ┌──────────────┐    ┌──────────────┐   ┌───────────┐  │
│  │  HUD Browser │◄──►│  HTTP Server │◄──│  SQLite   │  │
│  │  (localhost) │    │  Port 5000   │   │  Database │  │
│  └──────────────┘    └──────┬───────┘   └───────────┘  │
│                             │                           │
│  ┌──────────────┐    ┌──────▼───────┐   ┌───────────┐  │
│  │  Task Sched  │───►│  Python Core │◄──│  Ollama   │  │
│  │  (23:45 etc) │    │  (modules)   │   │  :11434   │  │
│  └──────────────┘    └──────────────┘   └───────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 2. DIRECTORY STRUCTURE

```
Apex_Ghost_Protocol-/
│
├── main.py                        # Entry point — argparse CLI
├── AGENTS.md                      # Claude CLI persistent memory
├── PRD.md                         # Product requirements
├── Design_System.md               # Design system reference
├── Architecture.md                # This file
├── STRATEGIC_MASTERPLAN.md        # Business & go-to-market plan
├── requirements.txt               # Python dependencies
├── apex.bat                       # Windows one-click launcher
├── register_apex_task.ps1         # Windows Task Scheduler registration
│
├── core/                          # Business logic & shared services
│   ├── __init__.py
│   ├── config.py                  # Pydantic config model (awakening, private_mode, paths)
│   ├── state.py                   # Player state singleton (XP, rank, streak)
│   ├── paths.py                   # Centralized path resolver
│   ├── logging_setup.py           # Logging configuration (file + console)
│   ├── daily_orchestrator.py      # Master coordinator for daily protocol
│   ├── events.py                  # Internal event bus (not WebSocket)
│   ├── treasury_models.py         # FinancialHealthReport, TreasuryTransaction
│   ├── treasury_service.py        # CRUD for financial transactions (14KB)
│   ├── bank_statement_importer.py # CSV/TSV parser → PII scrub → ML classify
│   ├── local_transaction_classifier.py  # Tier1: rules | Tier2: TF-IDF NaiveBayes
│   ├── financial_privacy.py       # On-device PII redactor
│   ├── apex_ghost_config.json     # Runtime config (hunter name, goals, preferences)
│   └── yearly_goals.json          # Annual goal configuration
│
├── quests/                        # The gamification engine
│   ├── models.py                  # Quest, QuestStatus, QuestCategory, QuestLevel
│   ├── service.py                 # QuestService (create/start/complete/miss)
│   ├── xp.py                      # XP system: add/deduct, rank/level calculation
│   ├── daily_generator.py         # AI-driven daily quest generation (11KB)
│   ├── goal_manager.py            # Long-term goal CRUD (12KB)
│   ├── goal_planner.py            # Goal → daily action decomposition
│   ├── goals.py                   # GoalsConfig, HunterProfile dataclasses
│   ├── predictive_engine.py       # RandomForest + circadian focus predictor
│   ├── circadian_optimizer.py     # Circadian rhythm model
│   ├── coach.py                   # AI coach behavioral feedback
│   ├── penalties.py               # Penalty calculation & logging
│   ├── progress.py                # Progress history tracker
│   ├── stat_decay.py              # Attribute decay when inactive
│   └── quest_tree.py              # Quest prerequisite dependency graph
│
├── automation/                    # Background enforcement daemons
│   ├── awakening.py               # Morning protocol (volume ramp → VLC → briefing)
│   ├── midnight_enforcer.py       # 23:45 Tier1/2/3 consequence engine (18KB)
│   ├── focus_guard.py             # Iron Focus Guard (process kill + hosts block)
│   ├── cognitive_monitor.py       # Keyboard/mouse rhythm → flow state detection
│   ├── soundscape_engine.py       # Dynamic music switching via VLC
│   ├── scheduler.py               # Background daemon scheduler
│   ├── ollama_client.py           # Ollama HTTP client (localhost:11434)
│   ├── rag_engine.py              # TF-IDF RAG for journal retrieval
│   ├── private_mode.py            # Privacy mode orchestration
│   ├── cloud_sync.py              # Optional AWS S3 E2E encrypted sync
│   └── system_control.py         # OS-level controls (Win32, volume, etc.)
│
├── voice/                         # J.A.R.V.I.S. voice system
│   ├── tts.py                     # TTS engine (pyttsx3 / Windows SAPI)
│   ├── jarvis_brain.py            # Core AI intelligence orchestrator
│   ├── script_builder.py          # Morning briefing script builder
│   ├── treasury_brain.py          # Air-gapped CFO audit generator
│   └── jinwoo_voice.py            # Solo Leveling character voice pack
│
├── dashboard/                     # HUD web application
│   ├── server.py                  # HTTP REST server (port 5000) — 856 lines
│   └── static/
│       ├── index.html             # Single-page HUD application — 406 lines
│       ├── style.css              # Complete design system styles — 726 lines
│       ├── app.js                 # All frontend logic — 52KB
│       ├── three.min.js           # Three.js r159 (bundled, no CDN)
│       └── jinwoo.jpg             # Hunter avatar image
│
├── storage/                       # Data persistence layer
│   ├── db.py                      # DatabaseManager singleton (SQLite3)
│   ├── repositories.py            # Repository pattern (quest, progress, penalty)
│   └── Modelfile.apex-cfo        # Ollama custom CFO model definition
│
├── scrapers/                      # Market intelligence scrapers
│   ├── intelligence_service.py    # Runs scraping + generates brief
│   └── opportunity_hunter.py     # Opportunity feed aggregator
│
├── ui/
│   └── cli.py                     # Rich terminal CLI menu
│
├── assets/                        # Video + media assets
│   └── awakening_assets.json      # Asset registry for morning videos
│
└── logs/                          # Runtime log files
```

---

## 3. DATA ARCHITECTURE

### 3.1 Database: SQLite3
Single file database at `storage/apex_ghost.db`.
Managed exclusively through `storage/db.py` — `DatabaseManager` singleton.

**Never use raw sqlite3 directly. Always use:**
```python
from storage.db import database_manager
database_manager.execute("INSERT INTO ...", (params,))
database_manager.fetch_all("SELECT * FROM ...")
database_manager.fetch_one("SELECT * FROM ... WHERE id = ?", (id,))
```

### 3.2 Schema — Core Tables

```sql
-- Player state (single row, id=1)
CREATE TABLE IF NOT EXISTS player_state (
  id               INTEGER PRIMARY KEY CHECK (id = 1),
  hunter_name      TEXT DEFAULT 'Hunter',
  total_xp         INTEGER DEFAULT 0,
  level            INTEGER DEFAULT 1,
  rank             TEXT DEFAULT 'E',
  streak           INTEGER DEFAULT 0,
  gold             INTEGER DEFAULT 0,
  missed_wake_ups  INTEGER DEFAULT 0,
  last_active_date TEXT
);

-- Quest log
CREATE TABLE IF NOT EXISTS quests (
  id                INTEGER PRIMARY KEY AUTOINCREMENT,
  title             TEXT NOT NULL,
  description       TEXT,
  level             TEXT NOT NULL,   -- 'daily' | 'weekly' | 'monthly' | 'boss'
  category          TEXT NOT NULL,   -- 'core' | 'boss' | 'habit' | 'side'
  status            TEXT NOT NULL,   -- 'pending' | 'in_progress' | 'completed' | 'missed'
  difficulty        INTEGER DEFAULT 3,
  xp_reward         INTEGER DEFAULT 100,
  penalty_xp        INTEGER DEFAULT 50,
  evidence_required INTEGER DEFAULT 0,
  evidence_submitted TEXT,
  target_date       TEXT,
  notes             TEXT,
  created_at        TEXT
);

-- Quest progress history
CREATE TABLE IF NOT EXISTS quest_progress (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  quest_id   INTEGER,
  status     TEXT,
  notes      TEXT,
  created_at TEXT
);

-- Focus sessions
CREATE TABLE IF NOT EXISTS focus_sessions (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  start_time TEXT NOT NULL,
  end_time   TEXT,
  duration   INTEGER,  -- minutes
  completed  INTEGER DEFAULT 0
);

-- Financial transactions
CREATE TABLE IF NOT EXISTS treasury_transactions (
  id                  INTEGER PRIMARY KEY AUTOINCREMENT,
  transaction_date    TEXT NOT NULL,
  title               TEXT NOT NULL,
  amount              REAL NOT NULL,
  category            TEXT,
  transaction_type    TEXT,  -- 'income' | 'expense'
  asset_classification TEXT, -- 'asset' | 'sustenance' | 'liability' | 'waste'
  necessity_score     INTEGER,
  is_recurring        INTEGER DEFAULT 0,
  notes               TEXT,
  created_at          TEXT
);

-- Shadow journal (accountability + reflections)
CREATE TABLE IF NOT EXISTS shadow_journal (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  content    TEXT NOT NULL,
  category   TEXT,  -- 'reflection' | 'accountability' | 'victory'
  created_at TEXT
);

-- Attribute matrix
CREATE TABLE IF NOT EXISTS player_attributes (
  id           INTEGER PRIMARY KEY CHECK (id = 1),
  strength     INTEGER DEFAULT 10,
  intelligence INTEGER DEFAULT 10,
  agility      INTEGER DEFAULT 10,
  discipline   INTEGER DEFAULT 10,
  focus        INTEGER DEFAULT 10,
  last_updated TEXT
);

-- Enforcement log
CREATE TABLE IF NOT EXISTS enforcement_log (
  id               INTEGER PRIMARY KEY AUTOINCREMENT,
  enforcement_date TEXT NOT NULL,
  missed_quest_title TEXT NOT NULL,
  tier             INTEGER NOT NULL,
  xp_penalty       INTEGER NOT NULL,
  action_taken     TEXT,
  created_at       TEXT
);

-- Miss streak (single row, id=1)
CREATE TABLE IF NOT EXISTS miss_streak (
  id                    INTEGER PRIMARY KEY CHECK (id = 1),
  consecutive_miss_days INTEGER DEFAULT 0,
  last_miss_date        TEXT,
  accountability_due    INTEGER DEFAULT 0
);

-- Opportunity feed
CREATE TABLE IF NOT EXISTS opportunities (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  title       TEXT,
  description TEXT,
  source      TEXT,
  url         TEXT,
  status      TEXT DEFAULT 'new',
  created_at  TEXT
);
```

---

## 4. API ARCHITECTURE

### 4.1 HTTP Server (Port 5000)
`dashboard/server.py` uses Python's built-in `http.server.SimpleHTTPRequestHandler`.
All API routes are handled in `do_GET()` and `do_POST()` with string prefix matching.

**Response pattern — add `_json_response()` helper:**
```python
def _json_response(self, data: dict, status: int = 200):
    body = json.dumps(data).encode("utf-8")
    self.send_response(status)
    self.send_header("Content-Type", "application/json")
    self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
    self.end_headers()
    self.wfile.write(body)
```

### 4.2 Complete REST API Contract

#### GET Endpoints
| Endpoint | Returns | Handler |
|---|---|---|
| `GET /api/stats` | XP, level, rank, streak, quests, attributes | `serve_api_stats()` |
| `GET /api/logs?last_idx=N` | Incremental console log feed | `serve_api_logs()` |
| `GET /api/goals/plan` | Goal planner execution plan | `serve_goals_plan()` |
| `GET /api/intelligence/latest` | Latest intel brief | `serve_intelligence_latest()` |
| `GET /api/journal/latest` | Shadow journal entries | `serve_journal_latest()` |
| `GET /api/treasury/summary` | Financial health report | `serve_treasury_summary()` |
| `GET /api/treasury/transactions` | Transaction list | `serve_treasury_transactions()` |
| `GET /api/opportunities/latest` | Market opportunity feed | `serve_opportunities_latest()` |
| `GET /api/neural/state` | Fatigue index, op mode, focus windows | `serve_neural_state()` 🔴 |
| `GET /api/quests/boss/active` | Active boss quest + deadline | `serve_active_boss_quest()` 🔴 |

#### POST Endpoints
| Endpoint | Body | Handler |
|---|---|---|
| `POST /api/quests/toggle` | `{quest_id, status}` | `handle_quest_toggle()` |
| `POST /api/actions/run` | `{action}` | `handle_action_run()` |
| `POST /api/goals/setup` | Hunter profile + goals JSON | `handle_goals_setup()` |
| `POST /api/treasury/transactions/add` | Transaction fields | `handle_treasury_add_transaction()` |
| `POST /api/treasury/audit/run` | — | `handle_treasury_run_audit()` |
| `POST /api/treasury/budget/update` | `{monthly_income}` | `handle_treasury_update_budget()` |
| `POST /api/opportunities/scan` | — | `handle_opportunities_scan()` |
| `POST /api/opportunities/accept` | `{opportunity_id}` | `handle_opportunities_accept()` |
| `POST /api/accountability/submit` | `{statement}` | `handle_accountability_submit()` 🔴 |

*🔴 = Needs to be built*

### 4.3 WebSocket Server (Port 5001) — To Build
Real-time event push using `websockets` library.

```
ws://localhost:5001

Events pushed from server → browser:
  xp_gained              {amount, total, rank, level}
  xp_penalty             {amount, total}
  quest_completed        {title, xp, category}
  rank_up                {old_rank, new_rank, level}
  penalty_triggered      {tier, quest, xp_lost}
  focus_guard_activated  {duration_minutes}
  treasury_update        {cashflow, runway, waste_detected}
```

---

## 5. AI / OLLAMA ARCHITECTURE

### 5.1 Ollama Connectivity
All AI features use `automation/ollama_client.py` — a simple HTTP client pointing to `localhost:11434`.

```python
# Never call Ollama directly — always use the client
from automation.ollama_client import ollama_client

if ollama_client.check_connection():
    response = ollama_client.query(prompt, system_prompt)
```

### 5.2 Ollama Models Used
| Model | Purpose | Fallback |
|---|---|---|
| `llama3.2:latest` | General queries, quest AI coach | Deterministic rules |
| `apex-cfo` (custom) | Financial auditing (built from llama3.2) | Mathematical audit |
| `llava` / `minicpm-v` | Vision proof verification (to build) | Text-only check |

### 5.3 Custom Model: apex-cfo
Built from `storage/Modelfile.apex-cfo`:
```bash
ollama create apex-cfo -f storage/Modelfile.apex-cfo
```
- Base: `llama3.2:latest`
- Temperature: `0.2` (low for financial precision)
- Context: `4096` tokens (needs upgrade to `8192`)
- System: Elon Musk first-principles + Kiyosaki asset-first doctrine

### 5.4 Graceful Degradation Pattern
**Every AI feature must work without Ollama.** Pattern:
```python
if ollama_client.check_connection():
    result = ollama_client.query(prompt, system)
    if result and len(result.strip()) > 50:
        return result  # AI path
# Always have a deterministic fallback
return build_deterministic_fallback(data)
```

---

## 6. FRONTEND ARCHITECTURE

### 6.1 Single Page Application Structure
`index.html` is a single-page app with:
- **Boot overlay** → visible on load, hides after init
- **App wrapper** → always mounted, visibility controlled by JS
- **Overlays** → Treasury, Quests, Intel, System — toggled via `hidden` attribute
- **Canvas layers** → bg-canvas (Three.js), radar-canvas, avatar-canvas, fatigue-canvas (to add)

### 6.2 JavaScript Module Pattern
`app.js` is a single file (no modules/imports). Functions are globally scoped.
Organization:
```
1. Constants & DOM refs
2. Boot sequence
3. Three.js scenes (background, levelup, globe)
4. Canvas renderers (radar, avatar, fatigue ring)
5. API polling functions (fetchStats, fetchLogs, fetchTreasury)
6. WebSocket handlers (to add)
7. Quest rendering
8. Treasury UI
9. Toast system (to add)
10. Focus session controls
11. Utility functions
```

### 6.3 State Management
No framework state — all state stored in:
- **DOM elements** (text content, classes, style)
- **Canvas draw calls** (redrawn every poll cycle)
- **Module-level JS variables** (e.g., `bossTimerInterval`, `lastLogIdx`)

### 6.4 Polling vs. WebSocket (Target State)
```
Current:                          Target:
├── stats: setInterval(8000)      ├── ws.onmessage → live push
├── logs: setInterval(3000)       ├── logs: setInterval(3000) [keep]
├── treasury: on-open             ├── treasury: on-open + ws events
└── neural: none                  └── neural: setInterval(30000)
```

---

## 7. BACKGROUND AUTOMATION ARCHITECTURE

### 7.1 Windows Task Scheduler Integration
`register_apex_task.ps1` registers two scheduled tasks:
- **Apex Ghost Awakening** — fires at configured wake time daily
- **Apex Ghost Midnight Enforcer** — fires at 23:45 every night

```
Task Scheduler
├── Apex Ghost Awakening
│   └── Runs: python automation/awakening.py
└── Apex Ghost Midnight Enforcer
    └── Runs: python automation/midnight_enforcer.py
```

### 7.2 Midnight Enforcer Flow
```
23:45 trigger
├── Scan: get all CORE + BOSS quests still PENDING/IN_PROGRESS for today
├── Check: how many completed today?
│
├── IF all complete:
│   ├── reset_miss_streak()
│   └── speak_text("All quests completed. Streak maintained.")
│
└── IF any missed:
    ├── increment_miss_streak()
    ├── FOR each missed quest:
    │   ├── streak=1 → _tier1_soft() [XP penalty + voice]
    │   ├── streak=2 → _tier2_hard() [Tier1 + focus guard 2h]
    │   └── streak≥3 → _tier3_hostile() [Tier2 + accountability gate]
    └── spawn_recovery_quest()
```

### 7.3 Focus Guard Flow
```
Focus session start
├── IF enable_hosts_block: modify /etc/hosts (Windows: C:\Windows\System32\drivers\etc\hosts)
│   └── Add 127.0.0.1 redirects for blocked_domains
└── Start _process_monitor_loop() (daemon thread, polls every 8s)
    └── FOR each running process:
        └── IF proc_name in blocked_apps:
            ├── taskkill /F /T /IM proc_name
            └── speak_text("I have closed {app}, Sir. Please remain focused.")

Focus session end
└── _remove_hosts_block()
```

---

## 8. FINANCIAL INTELLIGENCE ARCHITECTURE

### 8.1 Transaction Classification Pipeline
```
Raw CSV row
    │
    ▼
FinancialPrivacyGuard.sanitize_text()    ← Strip card#, account#, SA ID#
    │
    ▼
FinancialPrivacyGuard.normalize_vendor_name()  ← Remove POS noise, branch codes
    │
    ▼
LocalTransactionClassifier.classify_transaction()
    │
    ├── Tier 1: Deterministic vendor catalog (regex rules, 100% precision for known vendors)
    │   └── Returns: category, asset_classification, necessity_score, confidence=0.98
    │
    └── Tier 2: TF-IDF + NaiveBayes ML pipeline (self-trains on confirmed transactions)
        └── Returns: category, asset_classification, necessity_score, confidence=0.0-1.0
    │
    ▼
TreasuryTransaction (SQLite insert)
    │
    ▼
local_classifier.retrain()   ← Update ML model with new labeled data
```

### 8.2 CFO Audit Pipeline
```
User clicks "RUN AUDIT"
    │
    ▼
treasury_service.get_financial_health_report()
    ├── Calculate: monthly_income, total_expenses, net_cashflow
    ├── Calculate: asset_total, sustenance_total, liability_total, waste_total
    └── Calculate: kiyosaki_ratio, musk_frugality_score, runway_months
    │
    ▼
generate_spending_audit(report, transactions)
    │
    ├── IF Ollama online: query apex-cfo model → structured 3-section audit
    └── IF Ollama offline: build_deterministic_audit() → mathematical fallback
```

---

## 9. SECURITY MODEL

### 9.1 Air-Gap Guarantee
The following data types **never leave localhost**:
- Financial transaction data
- Bank statement CSV contents  
- PII (names, ID numbers, account numbers)
- Journal entries and accountability statements
- Hunter personal goals and metrics

### 9.2 Network Calls Map
```
ALLOWED:
├── localhost:5000    (HTTP server — browser ↔ Python)
├── localhost:5001    (WebSocket server — to build)
├── localhost:11434   (Ollama AI inference)
└── fonts.googleapis.com (Google Fonts CSS only — no data)

NEVER:
├── Any external financial API
├── Any cloud analytics / telemetry
├── Any external AI API (OpenAI, Anthropic, etc.)
└── Any user-identifying data to any server
```

---

## 10. DEPENDENCY MAP

```
main.py
├── core.logging_setup
├── core.paths
├── storage.db
├── ui.cli
│   └── dashboard.server (on HUD launch)
│
dashboard.server
├── quests.xp
├── quests.goal_manager
├── quests.goal_planner
├── quests.service
├── quests.models
├── storage.repositories
├── storage.db
├── core.treasury_service
├── core.treasury_models
├── voice.treasury_brain
└── scrapers.opportunity_hunter
│
voice.treasury_brain
├── automation.ollama_client
└── core.treasury_models
│
core.local_transaction_classifier
├── core.financial_privacy
└── storage.db (for ML retraining)
│
quests.predictive_engine
├── storage.db
├── sklearn (optional)
└── pandas (optional)
│
automation.midnight_enforcer
├── storage.db
├── quests.xp
├── voice.tts
└── automation.focus_guard
```

---

## 11. KNOWN TECHNICAL DEBT (Priority Order)

| # | Issue | Impact | File | Fix |
|---|---|---|---|---|
| 1 | `requirements.txt` missing scikit-learn, pandas, numpy, pyttsx3 | 🔴 Fresh install breaks | `requirements.txt` | Add all imports |
| 2 | No WebSocket — 8-second poll lag | 🔴 HUD feels dead | `server.py`, `app.js` | Add websockets library |
| 3 | Windows-only OS calls | 🔴 macOS/Linux excluded | `focus_guard.py`, `awakening.py` | OS abstraction layer |
| 4 | Text-only AI anti-cheat | 🟡 Core moat is incomplete | `quests/service.py` | Add vision_verifier.py |
| 5 | No one-click installer | 🟡 High friction install | root | Create install.ps1 |
| 6 | Hardcoded "Hunter La Pulga" in Modelfile | 🟡 Not generalizable | `Modelfile.apex-cfo` | Make parametric |
| 7 | VLC required for awakening | 🟡 Civilian barrier | `automation/awakening.py` | Better fallback |
| 8 | OFX/PDF bank import missing | 🟠 SA banks export these | `bank_statement_importer.py` | Add OFX parser |
| 9 | No Neural State HUD panel | 🟠 Predictive engine invisible | `index.html`, `app.js` | Build fatigue gauge |
| 10 | apex-cfo context too small (4096) | 🟠 Drops transactions | `Modelfile.apex-cfo` | Upgrade to 8192 |
