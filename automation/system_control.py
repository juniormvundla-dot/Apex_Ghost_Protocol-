from __future__ import annotations

# This file contains low-level system helper functions for Apex Ghost.
# It is meant to support other modules like private_mode.py and
# future features such as voice control, volume management, and app launching.

from dataclasses import dataclass
from pathlib import Path
import subprocess
import webbrowser


@dataclass(frozen=True)
class AppLaunchConfig:
    """
    Configuration for launching an app.

    executable_path:
        Full path to the application executable.
    arguments:
        Optional list of extra command-line arguments.
    """
    executable_path: str
    arguments: list[str] | None = None


class SystemController:
    """
    Provides reusable system-level helper methods.

    This class does not decide *when* actions happen.
    It only knows *how* to perform them.
    """

    def open_url(self, url: str) -> None:
        """
        Open a single website in the default browser.
        """
        webbrowser.open_new_tab(url)

    def open_urls(self, urls: list[str]) -> None:
        """
        Open multiple websites in a brand new dedicated browser window.
        Uses subprocess --new-window to guarantee window separation.
        """
        if not urls:
            return

        import os
        from core.config import config

        # Prioritize the user's preferred browser
        pref = getattr(config.private_mode, "browser_name", "chrome").lower()
        
        all_browsers = {
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "brave": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            "msedge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        }
        
        search_list = []
        if pref in all_browsers:
            search_list.append(all_browsers[pref])
        for name, path in all_browsers.items():
            if name != pref:
                search_list.append(path)
                
        search_list.extend([
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ])
        
        browser_found = None
        for path in search_list:
            if os.path.exists(path):
                browser_found = path
                break
                
        if browser_found:
            try:
                import time
                subprocess.Popen([browser_found, "--new-window", urls[0]])
                time.sleep(1.2)
                for url in urls[1:]:
                    subprocess.Popen([browser_found, url])
                    time.sleep(0.1)
                return
            except Exception as exc:
                print(f"Failed to launch dedicated browser window via subprocess: {exc}. Falling back to default.")

        # Fallback to standard webbrowser module
        webbrowser.open_new(urls[0])
        for url in urls[1:]:
            webbrowser.open_new_tab(url)

    def launch_app(self, config: AppLaunchConfig) -> None:
        """
        Launch an application using its executable path.

        This is useful when you know the exact .exe path.
        """
        command = [config.executable_path]
        if config.arguments:
            command.extend(config.arguments)

        subprocess.Popen(command)

    def launch_app_by_path(self, executable_path: str) -> None:
        """
        Launch an application when you only have the executable path.
        """
        subprocess.Popen([executable_path])

    def run_shell_command(self, command: list[str]) -> None:
        """
        Run a command safely without using shell=True.

        Use this when you want to run a known command or utility.
        """
        subprocess.Popen(command)

    def set_windows_volume_placeholder(self, level: int) -> None:
        """
        Placeholder for Windows volume control.

        This method is intentionally simple for now.
        Later we can connect it to:
        - pycaw
        - keyboard media keys
        - Windows sound APIs
        """
        print(f"Requested volume level: {level}%")
        print("Volume control is not fully implemented yet.")

    def ensure_path_exists(self, path: str | Path) -> None:
        """
        Check whether a file or folder exists.

        This is helpful before launching apps or accessing resources.
        """
        if not Path(path).exists():
            raise FileNotFoundError(f"Path does not exist: {path}")


# Reusable instance for other modules to import.
system_controller = SystemController()