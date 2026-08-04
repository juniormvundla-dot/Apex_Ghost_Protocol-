import os
import time
import subprocess
import threading
from core.config import config
from voice.tts import speak_text

class FocusGuard:
    """
    Orchestrates the active distraction lock (Iron Focus Guard).
    Monitors and terminates blacklisted programs, and redirects distracting web domains.
    """
    def __init__(self) -> None:
        self._running = False
        self._monitor_thread = None
        self._hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
        self._marker_start = "# APEX_GHOST_BLOCK_START\n"
        self._marker_end = "# APEX_GHOST_BLOCK_END\n"
        self._last_spoken = {} # Tracks {app_name: timestamp} to prevent voice spamming

    def start_guard(self) -> None:
        """
        Starts the active distraction monitoring.
        """
        if self._running:
            return

        self._running = True
        
        # 1. Apply hosts domain blocking if enabled
        if getattr(config.private_mode, "enable_hosts_block", False):
            self._apply_hosts_block()

        # 2. Start background process monitor if enabled
        if getattr(config.private_mode, "enable_process_guard", True):
            self._monitor_thread = threading.Thread(
                target=self._process_monitor_loop,
                daemon=True
            )
            self._monitor_thread.start()

    def stop_guard(self) -> None:
        """
        Stops monitoring and restores system hosts file to normal.
        """
        self._running = False
        if getattr(config.private_mode, "enable_hosts_block", False):
            self._remove_hosts_block()

    def _process_monitor_loop(self) -> None:
        """
        Background daemon loop querying active processes and killing distractions.
        """
        blocked_apps = [
            app.lower().strip() 
            for app in getattr(config.private_mode, "blocked_processes", [])
        ]
        if not blocked_apps:
            return

        while self._running:
            try:
                # Query running processes using tasklist (native Windows, no external dependencies)
                cmd = ["tasklist", "/NH", "/FO", "CSV"]
                # CREATE_NO_WINDOW prevents command prompt flashing
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                if result.returncode == 0:
                    running_list = result.stdout.splitlines()
                    for line in running_list:
                        # tasklist CSV format: "chrome.exe","1234","Console","1","50,000 K"
                        parts = line.split(",")
                        if not parts:
                            continue
                        proc_name = parts[0].strip('"').lower()
                        
                        if proc_name in blocked_apps:
                            # Terminate the process
                            self._kill_process(proc_name)
                            self._trigger_voice_warning(proc_name)
                            
            except Exception as e:
                print(f"[Focus Guard] Error in monitor loop: {e}")

            # Run check every 8 seconds to balance quick response and CPU usage
            time.sleep(8.0)

    def _kill_process(self, proc_name: str) -> None:
        """
        Terminate process and all sub-processes forcefully.
        """
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.run(
                ["taskkill", "/F", "/T", "/IM", proc_name],
                capture_output=True,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except Exception as e:
            print(f"[Focus Guard] Failed to kill {proc_name}: {e}")

    def _trigger_voice_warning(self, proc_name: str) -> None:
        """
        Have J.A.R.V.I.S. warn the user verbally (throttled to once every 60s per app).
        """
        now = time.time()
        last_spoken = self._last_spoken.get(proc_name, 0)
        
        if now - last_spoken > 60:
            self._last_spoken[proc_name] = now
            app_clean_name = proc_name.replace(".exe", "").capitalize()
            warning_text = (
                f"Workspace protocols are active, Sir. "
                f"I have closed {app_clean_name}. Please remain focused."
            )
            
            # Speak in a separate thread to keep process monitor loop reactive
            threading.Thread(
                target=speak_text,
                args=(warning_text,),
                daemon=True
            ).start()

    def _apply_hosts_block(self) -> None:
        """
        Append domain redirection blocks to the local hosts file.
        Requires Administrator privileges.
        """
        domains = getattr(config.private_mode, "blocked_domains", [])
        if not domains:
            return

        try:
            # Read existing hosts
            content = ""
            if os.path.exists(self._hosts_path):
                with open(self._hosts_path, "r", encoding="utf-8") as f:
                    content = f.read()

            # Clean out any old/stale blocks first
            cleaned = self._strip_blocks(content)

            # Construct new block lines
            block_lines = [self._marker_start]
            for domain in domains:
                block_lines.append(f"127.0.0.1 {domain}\n")
                block_lines.append(f"127.0.0.1 www.{domain}\n")
            block_lines.append(self._marker_end)

            new_content = cleaned + "".join(block_lines)

            # Write back to hosts
            with open(self._hosts_path, "w", encoding="utf-8") as f:
                f.write(new_content)
                
            print("Focus Guard: Website blocking activated.")
        except PermissionError:
            print(
                "\n[WARNING] Focus Guard failed to write to hosts file (Permission Denied).\n"
                "To enable website blocking, please run the command shell as Administrator.\n"
            )
        except Exception as e:
            print(f"[Focus Guard] Failed to apply website blocks: {e}")

    def _remove_hosts_block(self) -> None:
        """
        Restore hosts file by removing domain redirection blocks.
        """
        if not os.path.exists(self._hosts_path):
            return

        try:
            with open(self._hosts_path, "r", encoding="utf-8") as f:
                content = f.read()

            cleaned = self._strip_blocks(content)

            with open(self._hosts_path, "w", encoding="utf-8") as f:
                f.write(cleaned)
                
            print("Focus Guard: Website blocking deactivated.")
        except PermissionError:
            pass # Suppress warning on exit since user already saw start warning
        except Exception as e:
            print(f"[Focus Guard] Failed to restore hosts file: {e}")

    def _strip_blocks(self, content: str) -> str:
        """
        Helper to strip focus guard redirection lines from a file content string.
        """
        if self._marker_start not in content:
            return content

        lines = content.splitlines(keepends=True)
        cleaned_lines = []
        skipping = False
        
        for line in lines:
            if line == self._marker_start:
                skipping = True
                continue
            if line == self._marker_end:
                skipping = False
                continue
            if not skipping:
                cleaned_lines.append(line)
                
        return "".join(cleaned_lines)
