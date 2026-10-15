from __future__ import annotations

# APEX GHOST — AWAKENING ENGINE
# Force UTF-8 output so symbols print correctly on Windows terminals
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ──────────────────────────────────────────────────────────────────────────────
# Phase 1 of the daily protocol. Fires automatically at the configured wake
# hour via Windows Task Scheduler (register_apex_task.ps1).
#
# Sequence:
#   1. Ramp system volume from quiet → full to break sleep inertia
#   2. Play each motivational video in the queue back-to-back via VLC
#   3. After videos complete, deliver J.A.R.V.I.S. morning briefing (TTS)
#   4. Mark today as awakened so the sequence does not repeat
#
# Design philosophy:
#   - NO PROMPTS. When auto_launch=True (the default), this fires and cannot
#     be skipped by the hunter. Skipping is not an option; it is a failure.
#   - If the hunter kills the process, the penalty system applies at 23:59.
# ──────────────────────────────────────────────────────────────────────────────

from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys
import time
from datetime import date

# Allow running this file directly from CLI
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from core.config import config
from voice.tts import speak_text
from voice.script_builder import build_morning_awakening_script


@dataclass(frozen=True)
class AwakeningVideo:
    """One entry in the awakening video queue."""
    name: str       # Friendly label for logs
    filename: str   # Actual filename inside /assets


class MorningAwakeningProtocol:
    """
    Controls the Phase 1 morning awakening sequence.

    On a Task Scheduler trigger this fires with zero human input.
    The hunter cannot opt out — they can only complete it or fail it.
    """

    def __init__(
        self,
        assets_dir: Path | None = None,
        vlc_path: str | None = None,
    ) -> None:
        self.project_root = Path(__file__).resolve().parent.parent
        self.assets_dir   = assets_dir or (self.project_root / "assets")
        self.state_file   = self.project_root / "core" / ".awakening_state.txt"
        self.vlc_path  = Path(vlc_path or config.awakening.vlc_path)

        # Path to the asset registry JSON
        self.asset_registry = self.project_root / "assets" / "awakening_assets.json"

        # ── VIDEO QUEUE ───────────────────────────────────────────────────────
        # Loaded from assets/awakening_assets.json at runtime.
        # Falls back to the hardcoded list below if the JSON has no paths set.
        # ─────────────────────────────────────────────────────────────────────
        self.video_queue: list[AwakeningVideo] = self._load_video_queue()

    # ── ASSET REGISTRY ────────────────────────────────────────────────────────

    def _load_video_queue(self) -> list[AwakeningVideo]:
        """
        Load the video queue from assets/awakening_assets.json.

        Each entry needs a non-empty 'path' and 'enabled': true.
        Falls back to the legacy /assets folder filenames if the registry
        has no configured paths yet (first-run or missing file).
        """
        import json

        # ── Try JSON registry first ───────────────────────────────────────────
        if self.asset_registry.exists():
            try:
                data = json.loads(self.asset_registry.read_text(encoding="utf-8"))
                entries = data.get("videos", [])
                configured = [
                    AwakeningVideo(name=e["name"], filename=e["path"])
                    for e in entries
                    if e.get("enabled", True) and e.get("path", "").strip()
                ]
                if configured:
                    print(f"[Awakening] Loaded {len(configured)} video(s) from asset registry.")
                    return configured
                else:
                    print("[Awakening] Asset registry found but no paths are set yet.")
                    print(f"  --> Edit: {self.asset_registry}")
            except Exception as exc:
                print(f"[Awakening] Could not parse asset registry: {exc}")
        else:
            print(f"[Awakening] No asset registry found at {self.asset_registry}")

        # ── Fallback: look for files directly in /assets by legacy names ──────
        print("[Awakening] Falling back to legacy /assets filename lookup.")
        return [
            AwakeningVideo(name="Goggins Wake-Up Blast",            filename="5-MINUTE-AUDIO-FOR-GYMRAT.mp4"),
            AwakeningVideo(name="Batman Discipline Shift",           filename="BREAK-YOUR-LIMIT.mp4"),
            AwakeningVideo(name="Kill the Boy, Let the Man Be Born", filename="KILL-THE-BOY-AND-LET-THE-MAN-BE-BORN.mp4"),
            AwakeningVideo(name="Solo Leveling Final Push",          filename="SOLO-LEVELING.mp4"),
            AwakeningVideo(name="They Don't Know Me Son",            filename="THEY-DON-T-KNOW-ME-SON.mp4"),
        ]

    def _load_last_run_date(self) -> str | None:
        if not self.state_file.exists():
            return None
        try:
            return self.state_file.read_text(encoding="utf-8").strip() or None
        except OSError:
            return None

    def _save_last_run_date(self) -> None:
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(str(date.today()), encoding="utf-8")

    def already_ran_today(self) -> bool:
        return self._load_last_run_date() == str(date.today())

    # ── VLC DISCOVERY ─────────────────────────────────────────────────────────

    def _find_vlc(self) -> Path | None:
        """Locate VLC executable — configured path first, then standard locations."""
        if self.vlc_path and self.vlc_path.exists():
            return self.vlc_path

        candidates = [
            Path(r"C:\Program Files\VideoLAN\VLC\vlc.exe"),
            Path(r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"),
        ]
        for p in candidates:
            if p.exists():
                return p

        # Windows registry fallback
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\vlc.exe"
            )
            val, _ = winreg.QueryValueEx(key, "")
            winreg.CloseKey(key)
            if val:
                p = Path(val)
                if p.exists():
                    return p
        except Exception:
            pass

        return None

    # ── VOLUME RAMP ───────────────────────────────────────────────────────────

    def _ramp_volume(self) -> None:
        """
        Gradually raise system volume from volume_start to volume_peak over
        ~8 seconds. This mirrors a physical alarm clock ramping up — it
        interrupts sleep without the shock of instant maximum volume.
        """
        start = getattr(config.awakening, "volume_start", 30)
        peak  = getattr(config.awakening, "volume_peak",  100)

        if start == peak:
            self._set_volume(peak)
            return

        steps = 16
        step_delay = 8.0 / steps
        for i in range(steps + 1):
            vol = int(start + (peak - start) * (i / steps))
            self._set_volume(vol)
            time.sleep(step_delay)

        print(f"[Awakening] Volume ramped {start}% → {peak}%")

    @staticmethod
    def _set_volume(level: int) -> None:
        """Set Windows master volume (0–100) via PowerShell."""
        try:
            script = (
                f"$vol = {level} / 100;"
                "[audio]::Volume = $vol"
            )
            # Use the simpler nircmd approach if available; fallback to PS
            import ctypes
            # WinMM volume: 0x0000 = mute, 0xFFFF = max
            raw = int((level / 100) * 0xFFFF)
            packed = raw | (raw << 16)
            ctypes.windll.winmm.waveOutSetVolume(0, packed)
        except Exception:
            try:
                subprocess.run(
                    ["powershell", "-Command",
                     f"$obj = New-Object -ComObject WScript.Shell; "
                     f"$obj.SendKeys([char]174 * 5)"],
                    capture_output=True, timeout=5
                )
            except Exception:
                pass

    # ── VIDEO PLAYBACK ────────────────────────────────────────────────────────

    def _resolve_video_paths(self) -> list[str]:
        """Return paths for all existing video files in the queue."""
        paths = []
        for video in self.video_queue:
            raw = video.filename.strip()
            p   = Path(raw)

            if p.is_absolute():
                # Path configured directly in awakening_assets.json
                if p.exists():
                    print(f"  [OK] {video.name}")
                    print(f"       {p}")
                    paths.append(str(p))
                else:
                    print(f"  [!!] NOT FOUND : {video.name}")
                    print(f"       Path : {p}")
                    print(f"       Fix  : update 'path' in assets/awakening_assets.json")
            else:
                # Legacy: filename relative to /assets folder
                full = self.assets_dir / raw
                if full.exists():
                    print(f"  [OK] {video.name}  ({raw})")
                    paths.append(str(full))
                else:
                    print(f"  [!!] Missing : {raw}")
                    print(f"       Add file to /assets  OR  set full path in awakening_assets.json")
        return paths


    def _play_vlc_playlist(self, vlc_exe: Path, video_paths: list[str]) -> None:
        """
        Launch all videos as a single VLC playlist in fullscreen.
        subprocess.run blocks until the last video completes.
        """
        cmd = [
            str(vlc_exe),
            "--fullscreen",
            "--play-and-exit",    # exit VLC when playlist ends
            "--no-repeat",
            "--no-loop",
            "--no-one-instance",  # always spawn a fresh VLC process
        ] + video_paths
        print(f"[Awakening] Launching VLC with {len(video_paths)} video(s)...")
        subprocess.run(cmd, check=False)   # check=False — VLC exit code is unreliable

    def _play_fallback(self, video_paths: list[str]) -> None:
        """Play via Windows default player when VLC is not installed."""
        import os
        for vp in video_paths:
            print(f"[Awakening] Fallback: opening {Path(vp).name} in default player")
            try:
                os.startfile(vp)
                # Wait 3 min per video (approximate); no blocking possible without VLC
                time.sleep(180)
            except Exception as exc:
                print(f"[Awakening] Fallback failed: {exc}")

    # ── J.A.R.V.I.S. BRIEFING ────────────────────────────────────────────────

    def _deliver_briefing(self) -> None:
        """
        After the video sequence ends, J.A.R.V.I.S. reads the morning brief:
        rank, streak, today's quests, north star, Huberman protocol update.
        """
        print("\n[Awakening] Building J.A.R.V.I.S. morning briefing...")
        time.sleep(2)   # 2-second buffer between VLC close and TTS start
        try:
            script = build_morning_awakening_script()
            print(f"\n[J.A.R.V.I.S.] {script}\n")
            speak_text(script)
        except Exception as exc:
            print(f"[Awakening] Briefing unavailable: {exc}")

    # ── PUBLIC API ────────────────────────────────────────────────────────────

    def run(self, force: bool = False) -> None:
        """
        Execute the full awakening sequence.

        Args:
            force: Skip the 'already ran today' guard. Use for testing only.
        """
        if not force and self.already_ran_today():
            print("[Awakening] Protocol already completed today. Standing by.")
            return

        print()
        print("╔══════════════════════════════════════════╗")
        print("║   APEX GHOST — AWAKENING ENGINE ONLINE   ║")
        print("╚══════════════════════════════════════════╝")
        print(f"  Date     : {date.today()}")
        print(f"  Videos   : {len(self.video_queue)} queued")
        print()

        # Step 1: Ramp volume so the beast-mode videos hit at full power
        print("[Awakening] Ramping system volume...")
        self._ramp_volume()

        # Step 2: Resolve video files
        video_paths = self._resolve_video_paths()

        # Step 3: Play
        if video_paths:
            vlc_exe = self._find_vlc()
            if vlc_exe:
                self._play_vlc_playlist(vlc_exe, video_paths)
            else:
                print("[Awakening] VLC not found — using fallback player.")
                print("  → Install VLC for precise sequential playback control.")
                self._play_fallback(video_paths)
        else:
            print("[Awakening] No video files found in /assets.")
            print("  → Add your MP4s to the project /assets folder.")
            print("  → Expected files:")
            for v in self.video_queue:
                print(f"     assets/{v.filename}")

        # Step 4: Mark complete BEFORE briefing so a crash doesn't re-trigger videos
        self._save_last_run_date()

        # Step 5: J.A.R.V.I.S. morning briefing
        self._deliver_briefing()

        print("\n[Awakening] Protocol complete. You are now active. Execute without mercy.")

    def run_force(self) -> None:
        """Run even if already triggered today. Use for testing."""
        self.run(force=True)


# ── CONVENIENCE ENTRY POINTS ──────────────────────────────────────────────────

def run_awakening_protocol() -> None:
    """Standard entry point used by the daily orchestrator and server."""
    protocol = MorningAwakeningProtocol()
    protocol.run()


def force_awakening_now() -> None:
    """Force-run for testing/manual trigger. Ignores today's state."""
    protocol = MorningAwakeningProtocol()
    protocol.run_force()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Apex Ghost Awakening Protocol")
    parser.add_argument("--force", action="store_true",
                        help="Force run even if already executed today (for testing)")
    args = parser.parse_args()

    if args.force:
        force_awakening_now()
    else:
        run_awakening_protocol()