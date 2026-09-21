import os
import sys
import json
import webbrowser
import threading
import contextlib
import io
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from pathlib import Path
from datetime import date, datetime
from urllib.parse import urlparse, parse_qs

# Add project root to sys.path to allow imports
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from quests.xp import xp_system
from quests.goal_manager import goal_manager
from quests.goal_planner import goal_planner
from quests.goals import GoalsConfig, HunterProfile, YearlyGoal
from quests.service import quest_service
from quests.models import QuestStatus, QuestCategory
from storage.repositories import quest_repository
from storage.db import database_manager
from core.treasury_service import treasury_service
from core.treasury_models import TreasuryTransaction, BudgetRules
from voice.treasury_brain import generate_spending_audit
from scrapers.opportunity_hunter import opportunity_hunter

PORT = 5000
STATIC_DIR = Path(__file__).resolve().parent / "static"

# Global session variables for the web dashboard controls
active_focus_controller = None
active_session_id = None
lock = threading.Lock()

# Thread-safe log list for piping stdout of background tasks to front-end console
web_logs = []
web_logs_lock = threading.Lock()

# Stores the latest parsed intelligence brief in memory
latest_intelligence_brief = None

class WebConsoleStream(io.TextIOBase):
    """
    Custom stdout redirect stream that captures outputs line-by-line 
    and inserts them into the web logs buffer.
    """
    def __init__(self, log_list, lock):
        self.log_list = log_list
        self.lock = lock
        self.line_buffer = ""

    def write(self, s):
        self.line_buffer += s
        while "\n" in self.line_buffer:
            line, self.line_buffer = self.line_buffer.split("\n", 1)
            line = line.strip()
            if line:
                with self.lock:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    self.log_list.append(f"[{timestamp}] {line}")
                    if len(self.log_list) > 600:
                        self.log_list.pop(0)
        return len(s)

def add_web_log(msg):
    """
    Manually add an explicit log message to the HUD console.
    """
    with web_logs_lock:
        timestamp = datetime.now().strftime("%H:%M:%S")
        web_logs.append(f"[{timestamp}] {msg}")
        if len(web_logs) > 600:
            web_logs.pop(0)

def execute_background_job(target_func, job_name):
    """
    Run a python core procedure in a daemon background thread,
    redirecting all print() stdout outputs to the J.A.R.V.I.S. console logs.
    """
    def wrapper():
        add_web_log(f"[SYSTEM] Starting background job: {job_name}")
        stream = WebConsoleStream(web_logs, web_logs_lock)
        with contextlib.redirect_stdout(stream):
            try:
                target_func()
                add_web_log(f"[SYSTEM] Background job completed: {job_name}")
            except Exception as e:
                add_web_log(f"[ERROR] Job '{job_name}' failed: {e}")
    threading.Thread(target=wrapper, daemon=True).start()

def run_scraper_job():
    """
    Worker job to run scraper and capture the generated brief globally in-memory
    """
    global latest_intelligence_brief
    from scrapers.intelligence_service import run_intelligence_brief
    brief = run_intelligence_brief()
    
    # Map dataclass output to structured dictionary for REST API consumption
    latest_intelligence_brief = {
        "generated_at": brief.generated_at.strftime("%Y-%m-%d %H:%M:%S"),
        "total_items": brief.total_items,
        "trend_summary": brief.trend_summary.content,
        "security_findings": [
            {
                "title": f.title,
                "source": f.source,
                "url": f.url,
                "sentiment_score": f.sentiment_score
            } for f in brief.security_findings
        ]
    }


class DashboardRequestHandler(SimpleHTTPRequestHandler):
    """
    Sleek request handler routing static assets and REST API endpoints
    with zero external dependencies.
    """
    def translate_path(self, path):
        path_str = super().translate_path(path)
        clean_path = path_str.split("?")[0]
        rel_path = os.path.relpath(clean_path, os.getcwd())
        return os.path.join(str(STATIC_DIR), rel_path)

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_GET(self):
        if self.path.startswith("/api/stats"):
            self.serve_api_stats()
        elif self.path.startswith("/api/logs"):
            self.serve_api_logs()
        elif self.path.startswith("/api/goals/plan"):
            self.serve_goals_plan()
        elif self.path.startswith("/api/intelligence/latest"):
            self.serve_intelligence_latest()
        elif self.path.startswith("/api/journal/latest"):
            self.serve_journal_latest()
        elif self.path.startswith("/api/treasury/summary"):
            self.serve_treasury_summary()
        elif self.path.startswith("/api/treasury/transactions"):
            self.serve_treasury_transactions()
        elif self.path.startswith("/api/opportunities/latest"):
            self.serve_opportunities_latest()
        else:
            clean_path = self.path.split("?")[0]
            if clean_path == "/" or clean_path == "":
                self.path = "/index.html"
            super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/quests/toggle"):
            self.handle_quest_toggle()
        elif self.path.startswith("/api/actions/run"):
            self.handle_action_run()
        elif self.path.startswith("/api/goals/setup"):
            self.handle_goals_setup()
        elif self.path.startswith("/api/treasury/transactions/add"):
            self.handle_treasury_add_transaction()
        elif self.path.startswith("/api/treasury/audit/run"):
            self.handle_treasury_run_audit()
        elif self.path.startswith("/api/treasury/budget/update"):
            self.handle_treasury_update_budget()
        elif self.path.startswith("/api/opportunities/scan"):
            self.handle_opportunities_scan()
        elif self.path.startswith("/api/opportunities/accept"):
            self.handle_opportunities_accept()
        else:
            self.send_error(404, "Endpoint not found")

    def serve_api_stats(self):
        global active_focus_controller
        try:
            summary = xp_system.get_summary()
            goals = goal_manager.load()
            hunter_name = goals.profile.hunter_name or "Hunter"
            north_star = goals.profile.north_star or ""

            today_quests = quest_service.get_today_daily_quests()
            daily_list = []
            for q in today_quests:
                daily_list.append({
                    "title": q.title,
                    "description": q.description,
                    "xp_reward": q.xp_reward,
                    "penalty_xp": q.penalty_xp,
                    "status": q.status.value,
                    "category": q.category.value
                })

            all_quests = quest_repository.get_all_quests()
            weekly_list = []
            for q in all_quests:
                if q.level.value == "weekly":
                    weekly_list.append({
                        "title": q.title,
                        "description": q.description,
                        "xp_reward": q.xp_reward,
                        "status": q.status.value,
                        "category": q.category.value
                    })

            focus_rows = database_manager.fetch_all(
                "SELECT * FROM focus_sessions ORDER BY start_time DESC LIMIT 10"
            )
            focus_history = []
            for row in focus_rows:
                focus_history.append(dict(row))

            from quests.stat_decay import stat_decay_system
            attrs = stat_decay_system.check_and_apply_decay() or {"strength": 10, "intelligence": 10, "agility": 10, "discipline": 10}

            response_data = {
                "hunter_name": hunter_name,
                "north_star": north_star,
                "level": summary.get("level", 1),
                "xp": summary.get("xp", 0),
                "xp_threshold": summary.get("level", 1) * 1000,
                "rank": summary.get("rank", "E"),
                "streak": summary.get("streak", 0),
                "gold": summary.get("gold", 0),
                "daily_quests": daily_list,
                "weekly_quests": weekly_list,
                "focus_history": focus_history,
                "focus_active": active_focus_controller is not None,
                "attributes": attrs
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode("utf-8"))

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

    def serve_api_logs(self):
        try:
            parsed_url = urlparse(self.path)
            params = parse_qs(parsed_url.query)
            last_idx = 0
            if "last_idx" in params:
                try:
                    last_idx = int(params["last_idx"][0])
                except ValueError:
                    pass

            with web_logs_lock:
                logs_to_send = web_logs[last_idx:]
                current_len = len(web_logs)

            response_data = {
                "logs": logs_to_send,
                "next_idx": current_len
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode("utf-8"))

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

    def serve_goals_plan(self):
        try:
            config = goal_manager.load()
            if not config.goals:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"active": False}).encode("utf-8"))
                return

            plan = goal_planner.build_plan(config)
            
            # Map ExecutionPlan model to JSON dict
            plan_data = {
                "active": True,
                "profile_name": plan.profile_name,
                "north_star": plan.north_star,
                "plan_date": plan.plan_date.isoformat(),
                "current_quarter": plan.current_quarter,
                "week_number": plan.week_number,
                "monthly_focus": plan.monthly_focus,
                "weekly_targets": plan.weekly_targets,
                "today_actions": plan.today_actions,
                "yearly_goals": [
                    {
                        "title": g.title,
                        "category": g.category,
                        "description": g.description,
                        "success_metric": g.success_metric,
                        "deadline": g.deadline.isoformat(),
                        "priority": g.priority,
                        "milestones": g.milestones,
                        "monthly_focus": g.monthly_focus,
                        "weekly_targets": g.weekly_targets,
                        "daily_habits": g.daily_habits
                    } for g in plan.yearly_goals
                ]
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(plan_data).encode("utf-8"))

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

    def serve_intelligence_latest(self):
        global latest_intelligence_brief
        try:
            if latest_intelligence_brief is None:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"active": False}).encode("utf-8"))
                return

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "active": True,
                "brief": latest_intelligence_brief
            }).encode("utf-8"))

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

    def serve_journal_latest(self):
        try:
            rows = database_manager.fetch_all(
                "SELECT * FROM shadow_journal ORDER BY created_at DESC LIMIT 15"
            )
            journal_list = []
            for row in rows:
                journal_list.append(dict(row))
                
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(journal_list).encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

    def handle_quest_toggle(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode("utf-8"))
            quest_title = payload.get("title")

            if not quest_title:
                self.send_error(400, "Quest title required")
                return

            all_quests = quest_repository.get_all_quests()
            target_quest = None
            for q in all_quests:
                if q.title == quest_title:
                    target_quest = q
                    break

            if not target_quest:
                self.send_error(404, "Quest not found")
                return

            if target_quest.status == QuestStatus.COMPLETED:
                target_quest.status = QuestStatus.PENDING
                target_quest.completed_at = None
                quest_repository.save_quest(target_quest)
                if target_quest.category in (QuestCategory.CORE, QuestCategory.BOSS):
                    xp_system.apply_penalty(target_quest.xp_reward)
                message = "Quest reset to pending"
            else:
                evidence = payload.get("evidence", "").strip()
                if target_quest.evidence_required:
                    if not evidence:
                        self.send_error(400, "Evidence required for this quest.")
                        return
                    accepted = quest_service.complete_quest_with_evidence(target_quest, evidence)
                    if not accepted:
                        self.send_error(400, "Evidence rejected by AI validation.")
                        return
                    message = "Quest completed. Evidence accepted."
                else:
                    quest_service.complete_quest(target_quest, notes="Completed via Web HUD Dashboard.")
                    message = "Quest completed successfully"

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "message": message}).encode("utf-8"))

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

    def handle_action_run(self):
        global active_focus_controller, active_session_id
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode("utf-8"))
            action = payload.get("action")

            if not action:
                self.send_error(400, "Action type required")
                return

            message = ""
            status = "success"

            with lock:
                if action == "start_private_mode":
                    if active_focus_controller is not None:
                        status = "error"
                        message = "Private Mode session is already active."
                    else:
                        add_web_log("[SYSTEM] Initializing Focus Environment Isolation...")
                        from automation.private_mode import PrivateModeController
                        active_focus_controller = PrivateModeController()
                        
                        if active_focus_controller.config.play_voice_greeting:
                            add_web_log("[J.A.R.V.I.S.] Preparing audio greeting...")
                            threading.Thread(
                                target=active_focus_controller.play_greeting,
                                daemon=True
                            ).start()
                        
                        if active_focus_controller.config.launch_browser:
                            add_web_log("[SYSTEM] Launching workspace browser focus tabs...")
                            active_focus_controller.open_browser_tabs()
                            
                        if active_focus_controller.config.launch_intellij:
                            add_web_log("[SYSTEM] Initiating IDE development interface...")
                            active_focus_controller.launch_intellij()
                            
                        add_web_log("[SYSTEM] Activating active distraction locks (Focus Guard)...")
                        active_focus_controller.focus_guard.start_guard()
                        
                        active_session_id = active_focus_controller.start_session()
                        message = "Private Mode isolation initialized."
                        add_web_log("[SYSTEM] Workspace secure. Deep work timer is running.")

                elif action == "stop_private_mode":
                    if active_focus_controller is None:
                        status = "error"
                        message = "No active Private Mode session found."
                    else:
                        add_web_log("[SYSTEM] Stopping Focus Guard monitoring...")
                        active_focus_controller.focus_guard.stop_guard()
                        
                        add_web_log("[SYSTEM] De-activating focus blocks and saving session...")
                        active_focus_controller.end_session(active_session_id)
                        
                        active_focus_controller = None
                        active_session_id = None
                        
                        message = "Private Mode workspace deactivated."
                        add_web_log("[SYSTEM] Workspace unlocked. Focus session compiled successfully.")

                elif action == "daily_protocol":
                    from core.daily_orchestrator import run_daily_protocol
                    execute_background_job(run_daily_protocol, "Daily Protocol")
                    message = "Daily Protocol script initialized."

                elif action == "awakening":
                    from automation.awakening import run_awakening_protocol
                    execute_background_job(run_awakening_protocol, "Morning Awakening")
                    message = "Morning Awakening sequence initialized."

                elif action == "intelligence_brief":
                    execute_background_job(run_scraper_job, "Scrape Intel Brief")
                    message = "Intelligence brief collector initialized."

                elif action == "cloud_sync":
                    from automation.cloud_sync import perform_cloud_sync
                    execute_background_job(perform_cloud_sync, "AWS Cloud Sync")
                    message = "AWS Cloud Sync backup initiated."

                else:
                    self.send_error(400, f"Unknown action: {action}")
                    return

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": status, "message": message}).encode("utf-8"))

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

    def handle_goals_setup(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode("utf-8"))

            hunter_name = payload.get("hunter_name", "Hunter")
            target_year = int(payload.get("target_year", date.today().year))
            north_star = payload.get("north_star", "")
            raw_goals = payload.get("goals", [])

            # 1. Compile profile
            profile = HunterProfile(
                hunter_name=hunter_name,
                year=target_year,
                north_star=north_star
            )

            # 2. Compile yearly goals list
            goals = []
            for index, rg in enumerate(raw_goals, start=1):
                deadline_date = date.fromisoformat(rg.get("deadline"))
                goals.append(YearlyGoal(
                    id=f"goal_{index}",
                    title=rg.get("title"),
                    category=rg.get("category", "Discipline"),
                    description=rg.get("description", ""),
                    success_metric=rg.get("success_metric", ""),
                    deadline=deadline_date,
                    priority=int(rg.get("priority", 3)),
                    milestones=[],
                    monthly_focus=[],
                    weekly_targets=[],
                    daily_habits=[]
                ))

            # Decompose goals and compile config
            config = GoalsConfig(profile=profile, goals=goals)
            for goal in config.goals:
                goal_manager.decompose_goal(goal)

            # 3. Save to storage JSON and synchronize Quest DB
            goal_manager.save(config)
            goal_manager.sync_quest_tree(config)

            add_web_log(f"[GOALS] Profile configured. Hunter Name: {hunter_name}.")
            add_web_log(f"[GOALS] Synced {len(goals)} yearly goals into Quest Database successfully.")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "message": "Goals plan configured and database synced."}).encode("utf-8"))

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

    def serve_treasury_summary(self):
        try:
            report = treasury_service.calculate_health_report()
            rules = treasury_service.get_budget_rules()
            data = {
                "currency": report.currency,
                "monthly_income": report.monthly_income,
                "total_expenses": report.total_expenses,
                "net_cashflow": report.net_cashflow,
                "asset_total": report.asset_total,
                "asset_pct": report.asset_pct,
                "sustenance_total": report.sustenance_total,
                "sustenance_pct": report.sustenance_pct,
                "liability_total": report.liability_total,
                "liability_pct": report.liability_pct,
                "waste_total": report.waste_total,
                "waste_pct": report.waste_pct,
                "monthly_burn_rate": report.monthly_burn_rate,
                "runway_months": report.runway_months,
                "kiyosaki_ratio": report.kiyosaki_ratio,
                "musk_frugality_score": report.musk_frugality_score,
                "rule_violations": report.rule_violations,
                "targets": {
                    "asset_target_pct": rules.asset_target_pct,
                    "sustenance_target_pct": rules.sustenance_target_pct,
                    "skill_capital_pct": rules.skill_capital_pct,
                    "runway_buffer_pct": rules.runway_buffer_pct,
                    "waste_tolerance_pct": rules.waste_tolerance_pct,
                }
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

    def serve_treasury_transactions(self):
        try:
            transactions = treasury_service.get_transactions(limit=60)
            data = [
                {
                    "id": t.id,
                    "transaction_date": t.transaction_date,
                    "title": t.title,
                    "amount": t.amount,
                    "category": t.category,
                    "transaction_type": t.transaction_type,
                    "asset_classification": t.asset_classification,
                    "necessity_score": t.necessity_score,
                    "is_recurring": t.is_recurring,
                    "notes": t.notes,
                }
                for t in transactions
            ]
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

    def serve_opportunities_latest(self):
        try:
            opps = treasury_service.get_opportunities()
            data = [
                {
                    "id": o.id,
                    "title": o.title,
                    "industry": o.industry,
                    "loophole_summary": o.loophole_summary,
                    "service_solution": o.service_solution,
                    "target_client": o.target_client,
                    "pricing_model": o.pricing_model,
                    "action_steps": o.action_steps,
                    "status": o.status,
                    "created_at": o.created_at,
                }
                for o in opps
            ]
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

    def handle_treasury_add_transaction(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            payload = json.loads(body)

            tx = TreasuryTransaction(
                id=None,
                transaction_date=payload.get("transaction_date") or date.today().strftime("%Y-%m-%d"),
                title=payload.get("title", "Expense"),
                amount=float(payload.get("amount", 0.0)),
                category=payload.get("category", "General"),
                transaction_type=payload.get("transaction_type", "expense"),
                asset_classification=payload.get("asset_classification", "sustenance"),
                necessity_score=int(payload.get("necessity_score", 5)),
                is_recurring=bool(payload.get("is_recurring", False)),
                notes=payload.get("notes", ""),
            )
            tx_id = treasury_service.add_transaction(tx)
            add_web_log(f"[TREASURY] Logged {tx.transaction_type.upper()}: {tx.title} (${tx.amount:,.2f}) [{tx.asset_classification.upper()}]")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "id": tx_id}).encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

    def handle_treasury_run_audit(self):
        try:
            add_web_log("[TREASURY] Initiating Gemini First-Principles spending audit...")
            report = treasury_service.calculate_health_report()
            transactions = treasury_service.get_transactions(limit=40)
            audit_critique = generate_spending_audit(report, transactions)
            add_web_log("[TREASURY] Financial audit compiled successfully.")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "audit": audit_critique}).encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

    def handle_treasury_update_budget(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            payload = json.loads(body)

            rules = treasury_service.get_budget_rules()
            if "monthly_income" in payload:
                rules.monthly_income = float(payload["monthly_income"])
            if "currency" in payload:
                rules.currency = str(payload["currency"])
            if "asset_target_pct" in payload:
                rules.asset_target_pct = float(payload["asset_target_pct"])

            treasury_service.update_budget_rules(rules)
            add_web_log(f"[TREASURY] Budget targets updated: Income {rules.currency}{rules.monthly_income:,.2f}")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

    def handle_opportunities_scan(self):
        try:
            add_web_log("[ARBITRAGE] Scanning live market signals and technology loopholes...")
            opps = opportunity_hunter.scan_opportunities()
            add_web_log(f"[ARBITRAGE] Market scan complete: {len(opps)} opportunities surfaced.")

            data = [
                {
                    "id": o.id,
                    "title": o.title,
                    "industry": o.industry,
                    "loophole_summary": o.loophole_summary,
                    "service_solution": o.service_solution,
                    "target_client": o.target_client,
                    "pricing_model": o.pricing_model,
                    "action_steps": o.action_steps,
                    "status": o.status,
                }
                for o in opps
            ]
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "opportunities": data}).encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

    def handle_opportunities_accept(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            payload = json.loads(body)
            opp_id = int(payload.get("opp_id", 0))

            created_quests = treasury_service.convert_opportunity_to_quests(opp_id)
            for q in created_quests:
                add_web_log(f"[ARBITRAGE CONTRACT] Generated Quest: {q}")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "quests": created_quests}).encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))


def start_shadow_journal():
    import subprocess
    python_exe = sys.executable
    script_path = str(Path(__file__).resolve().parent.parent / "ui" / "shadow_journal.py")
    try:
        # Start headless borderless capture window background overlay
        subprocess.Popen([python_exe, script_path], creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
        print("[SYSTEM] Shadow Journal Win+J overlay started.")
    except Exception as e:
        print(f"[SYSTEM] Failed to start Shadow Journal: {e}")

def start_cognitive_monitor():
    try:
        from automation.cognitive_monitor import cognitive_monitor
        cognitive_monitor.start()
    except Exception as e:
        print(f"[SYSTEM] Failed to start Cognitive Monitor: {e}")

def start_server():
    """
    Launch the web server daemon on Port 5000 and auto-open it in the default browser.
    """
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    TCPServer.allow_reuse_address = True
    
    # Spawn background monitoring daemons automatically
    start_shadow_journal()
    start_cognitive_monitor()
    
    with TCPServer(("", PORT), DashboardRequestHandler) as httpd:
        print("\n=========================================")
        print(f"APEX GHOST HUD SERVER ONLINE: http://localhost:{PORT}")
        print("Press Ctrl+C to shut down the server.")
        print("=========================================\n")
        
        webbrowser.open(f"http://localhost:{PORT}")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down HUD server...")
            httpd.shutdown()

if __name__ == "__main__":
    start_server()
