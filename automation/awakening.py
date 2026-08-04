from __future__ import annotations

# This file contains the Morning Awakening Protocol.
# It plays a fixed sequence of motivational videos from the assets folder.
# VLC is used so each video finishes before the next one starts.

from dataclasses import dataclass
from pathlib import Path
import subprocess
from datetime import date

import sys
from pathlib import Path

# Add project root to sys.path to allow running this script directly
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from core.config import config
import time
from voice.tts import speak_text
from voice.script_builder import build_morning_awakening_script


@dataclass(frozen=True)
class AwakeningVideo:
    # A simple data structure that stores one video in the awakening queue.
    # name = friendly label for logs
    # filename = actual file stored in /assets
    name: str
    filename: str


class MorningAwakeningProtocol:
    """
    This class controls the phase 1 awakening sequence.

    Responsibilities:
    - find video files inside the assets folder
    - launch them in order
    - optionally ask for proof of life
    - remember if the protocol already ran today
    """

    def __init__(
        self,
        assets_dir: Path | None = None,
        vlc_path: str | None = None,
    ) -> None:
        # Resolve the project root by moving one level above /automation
        self.project_root = Path(__file__).resolve().parent.parent

        # If no assets_dir is given, use the default /assets folder in the project root
        self.assets_dir = assets_dir or (self.project_root / "assets")

        # This file is used to store the date of the last successful awakening run
        self.state_file = self.project_root / "core" / ".awakening_state.txt"

        self.vlc_path = Path(vlc_path or config.awakening.vlc_path)

        # Define the awakening queue here.
        # Change filenames here if your actual asset names change later.
        self.video_queue: list[AwakeningVideo] = [
            AwakeningVideo(
                name="Goggins Wake-Up Blast",
                filename="5-MINUTE-AUDIO-FOR-GYMRAT.mp4",
            ),
            AwakeningVideo(
                name="Batman Discipline Shift",
                filename="BREAK-YOUR-LIMIT.mp4",
            ),
            AwakeningVideo(
                name="Kill the Boy, Let the Man Be Born",
                filename="KILL-THE-BOY-AND-LET-THE-MAN-BE-BORN.mp4",
            ),
            AwakeningVideo(
                name="Solo Leveling Final Push",
                filename="SOLO-LEVELING.mp4",
            ),
            AwakeningVideo(
                name="They Don't Know Me Son",
                filename="THEY-DON-T-KNOW-ME-SON.mp4",
            ),
        ]

    def _load_last_run_date(self) -> str | None:
        """
        Read the last run date from the state file.
        """
        if not self.state_file.exists():
            return None

        try:
            return self.state_file.read_text(encoding="utf-8").strip() or None
        except OSError:
            return None

    def _save_last_run_date(self) -> None:
        """
        Save today's date so the protocol does not run twice in one day.
        """
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(str(date.today()), encoding="utf-8")

    def already_ran_today(self) -> bool:
        """
        Check whether the awakening protocol already ran today.
        """
        last_run = self._load_last_run_date()
        return last_run == str(date.today())

    def _get_video_path(self, filename: str) -> Path:
        """
        Build the full path to a video file and verify that it exists.
        """
        path = self.assets_dir / filename
        if not path.exists():
            raise FileNotFoundError(
                f"Missing video file: {path}. "
                f"Please check the filename in the assets folder."
            )
        return path

    def _find_vlc_path(self) -> Path | None:
        """
        Attempt to automatically discover VLC path on Windows.
        Returns resolved Path or None.
        """
        # 1. Check user configured path
        if self.vlc_path and self.vlc_path.exists():
            return self.vlc_path

        # 2. Check standard paths
        standard_paths = [
            Path(r"C:\Program Files\VideoLAN\VLC\vlc.exe"),
            Path(r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"),
        ]
        for p in standard_paths:
            if p.exists():
                return p

        # 3. Check registry key App Paths
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

    def _play_with_fallback(self, video_path: Path) -> None:
        """
        Play video using standard default Windows app launcher (os.startfile).
        """
        import os
        print(f"VLC not found. Launching via default media player: {video_path.name}")
        try:
            os.startfile(str(video_path))
            input("Press Enter to continue to the next video...")
        except Exception as exc:
            print(f"Fallback playback failed: {exc}")

    def _play_with_vlc(self, vlc_executable: Path, video_path: Path) -> None:
        """
        Play a video using VLC and wait until it finishes.
        """
        vlc_command = [
            str(vlc_executable),
            "--fullscreen",
            "--play-and-exit",
            "--no-one-instance",
            str(video_path),
        ]
        # subprocess.run waits until VLC exits, so the next video will not start early.
        subprocess.run(vlc_command, check=True)

    def play_video(self, video: AwakeningVideo) -> None:
        """
        Play one video from the queue.
        The next video starts only after this one finishes.
        """
        video_path = self._get_video_path(video.filename)

        print(f"\nNow playing: {video.name}")
        print(f"File: {video_path}")

        vlc_exe = self._find_vlc_path()
        if vlc_exe:
            self._play_with_vlc(vlc_exe, video_path)
        else:
            self._play_with_fallback(video_path)

    def run(self) -> None:
        """
        Execute the full awakening sequence.

        Steps:
        1. Prevent duplicate runs on the same day
        2. Play each video in the queue
        3. Save today's run date
        """
        if self.already_ran_today():
            print("Awakening protocol already completed today.")
            return

        print("\n==============================")
        print("APEX GHOST - AWAKENING ENGINE")
        print("==============================")
        print("Initiating morning protocol...\n")

        vlc_exe = self._find_vlc_path()
        if vlc_exe:
            print("Launching complete awakening video sequence via VLC playlist...")
            video_paths = []
            for video in self.video_queue:
                p = self._get_video_path(video.filename)
                if p and p.exists():
                    print(f"- Queued: {video.name}")
                    video_paths.append(str(p))
            if video_paths:
                # --no-one-instance ensures VLC runs a dedicated process that blocks until the final video in the playlist completes
                vlc_command = [
                    str(vlc_exe),
                    "--fullscreen",
                    "--play-and-exit",
                    "--no-one-instance",
                ] + video_paths
                subprocess.run(vlc_command, check=True)
        else:
            for video in self.video_queue:
                self.play_video(video)

        # Save completion so it doesn't run again today
        self._save_last_run_date()

        print("\nAwakening video queue complete. Initializing J.A.R.V.I.S. morning voice protocol...")
        time.sleep(2)  # 2-second buffer between video close and voice initiation
        try:
            morning_script = build_morning_awakening_script()
            print(f"\n[J.A.R.V.I.S. Morning Briefing]: {morning_script}\n")
            speak_text(morning_script)
        except Exception as exc:
            print(f"[Awakening Engine] Could not play morning briefing: {exc}")

        print("\nAwakening protocol complete. You are now active.")


def run_awakening_protocol() -> None:
    """
    Convenience function so other files can start the protocol easily.
    """
    protocol = MorningAwakeningProtocol()
    protocol.run()


if __name__ == "__main__":
    run_awakening_protocol()