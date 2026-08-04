import time
import ctypes
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent

from storage.db import database_manager

user32 = ctypes.windll.user32

class ShadowJournalUI:
    """
    A frictionless, borderless dropdown overlay window mapped to a Win+J hotkey 
    for fast developer quick-captures auto-classified into tech tasks or reflections.
    """
    def __init__(self):
        self.root = None
        self.entry = None
        self.running = False

    def start(self):
        self.running = True
        
        # Start global hotkey daemon thread
        threading.Thread(target=self._hotkey_listener, daemon=True).start()
        
        # Setup GUI in main thread or dynamic loop
        self._init_gui()

    def _init_gui(self):
        self.root = tk.Tk()
        self.root.title("Shadow Journal Overlay")
        
        # Render borderless window
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#050609")
        
        # Geometry: centered at the top of screen
        screen_width = self.root.winfo_screenwidth()
        width = 600
        height = 65
        x = (screen_width - width) // 2
        y = 80
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Create glowing cyan borders inside frame
        frame = tk.Frame(self.root, bg="#050609", highlightbackground="#00f2fe", highlightthickness=2)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Inner layout elements
        lbl = tk.Label(
            frame, 
            text="J.A.R.V.I.S. // SHADOW JOURNAL CAPTURE [ESC: Cancel // ENTER: Submit]", 
            fg="#7b83ad", 
            bg="#050609", 
            font=("Courier New", 9, "bold")
        )
        lbl.pack(anchor="w", padx=15, pady=(8, 2))
        
        self.entry = tk.Entry(
            frame, 
            fg="#00f2fe", 
            bg="#0f172a", 
            insertbackground="#00f2fe", 
            font=("Outfit", 12),
            bd=0
        )
        self.entry.pack(fill=tk.X, padx=15, pady=(0, 8))
        self.entry.bind("<Return>", self._submit_capture)
        self.entry.bind("<Escape>", lambda e: self.hide())
        
        # Initially hidden
        self.root.withdraw()
        
        # Start GUI main loop
        self.root.mainloop()

    def show(self):
        if self.root:
            self.root.deiconify()
            self.root.lift()
            self.root.attributes("-topmost", True)
            self.entry.delete(0, tk.END)
            self.entry.focus_force()

    def hide(self):
        if self.root:
            self.root.withdraw()

    def _submit_capture(self, event):
        text = self.entry.get().strip()
        if not text:
            self.hide()
            return

        # Auto-tag classification heuristic
        category = "reflection"
        lower_text = text.lower()
        bug_keywords = ["bug", "fix", "broken", "refactor", "error", "issue", "compile", "failed"]
        if any(keyword in lower_text for keyword in bug_keywords):
            category = "bug_fix"

        try:
            # Write to database table
            now = datetime.now().isoformat()
            database_manager.execute(
                "INSERT INTO shadow_journal (content, category, created_at) VALUES (?, ?, ?)",
                (text, category, now)
            )
            print(f"[Shadow Journal] Captured: '{text}' [Classified: {category.upper()}]")
        except Exception as e:
            print(f"[Shadow Journal] Database save failure: {e}")
            
        self.hide()

    def _hotkey_listener(self):
        # Poll keyboard states for Win+J (0x5B/0x5C + 0x4A)
        # We also support Ctrl+Alt+J (0x11 + 0x12 + 0x4A) as a reliable backup
        while self.running:
            win_pressed = (user32.GetAsyncKeyState(0x5B) & 0x8000) or (user32.GetAsyncKeyState(0x5C) & 0x8000)
            ctrl_pressed = user32.GetAsyncKeyState(0x11) & 0x8000
            alt_pressed = user32.GetAsyncKeyState(0x12) & 0x8000
            j_pressed = user32.GetAsyncKeyState(0x4A) & 0x8000
            
            if (win_pressed and j_pressed) or (ctrl_pressed and alt_pressed and j_pressed):
                # Trigger show in the GUI thread-safe main loop
                if self.root:
                    self.root.after(0, self.show)
                # Brief sleep to prevent multiple triggers from one press
                time.sleep(0.5)
                
            time.sleep(0.1)

# Global shadow journal runner
shadow_journal_overlay = ShadowJournalUI()

if __name__ == "__main__":
    shadow_journal_overlay.start()
