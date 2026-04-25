
import os
import json
import time
import threading
import subprocess
import tkinter as tk
from pathlib import Path
from datetime import datetime
from tkinter import messagebox

APP_TITLE = "PANEL LOOP FULL V3 PRO"
AUTHOR = "Ahmad Nazari"
VERSION = "v3.0 FULL PRO"

PROFILE_FILE = Path(__file__).with_name("panel_loop_full_v3_profile.json")

GAMELOOP_PATHS = [
    r"C:\Program Files\TxGameAssistant\AppMarket\AppMarket.exe",
    r"C:\Program Files\TxGameAssistant\ui\AppMarket.exe",
    r"C:\Program Files\TxGameAssistant\AndroidEmulatorEx.exe",
    r"C:\Program Files\GameLoop\Launcher.exe",
    r"D:\Program Files\TxGameAssistant\AppMarket\AppMarket.exe",
    r"D:\TxGameAssistant\AppMarket\AppMarket.exe",
]

GAMELOOP_PROCESSES = [
    "AndroidEmulatorEx",
    "AndroidEmulator",
    "aow_exe",
    "AppMarket",
    "ProjectTitan",
    "AndroidRender",
    "QMEmulatorService"
]

SAFE_BACKGROUND_PROCESSES = [
    "OneDrive",
    "Widgets",
    "YourPhone",
    "PhoneExperienceHost",
    "GameBar",
    "XboxGameBar",
    "XboxAppServices"
]

def run_ps(command, timeout=30):
    try:
        flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
            capture_output=True,
            text=True,
            timeout=timeout,
            creationflags=flags
        )
        return (result.stdout or result.stderr or "").strip()
    except Exception as e:
        return str(e)

def get_wmi(prop, cls):
    out = run_ps(f"(Get-CimInstance {cls} | Select-Object -First 1 -ExpandProperty {prop})", timeout=15)
    return out.strip() if out.strip() else "Unknown"

def cpu_name():
    return get_wmi("Name", "Win32_Processor")

def gpu_name():
    return get_wmi("Name", "Win32_VideoController")

def logical_cores():
    try:
        return int(get_wmi("NumberOfLogicalProcessors", "Win32_Processor"))
    except:
        return os.cpu_count() or 4

def ram_gb():
    try:
        return round(int(get_wmi("TotalPhysicalMemory", "Win32_ComputerSystem")) / 1024 / 1024 / 1024, 2)
    except:
        return 0.0

def find_gameloop():
    for path in GAMELOOP_PATHS:
        if Path(path).exists():
            return path
    return None

def mask_skip_first(logical, use_threads=12, skip=4):
    if logical <= 1:
        return 1
    start = min(skip, logical - 1)
    end = min(logical - 1, start + use_threads - 1)
    mask = 0
    for i in range(start, end + 1):
        mask |= 1 << i
    return mask if mask else 1

def build_profile():
    logical = logical_cores()

    if logical >= 16:
        threads = 12
        mask = mask_skip_first(logical, 12, 4)
        profile = "12 Thread Ultra Stable"
    elif logical >= 12:
        threads = 8
        mask = mask_skip_first(logical, 8, 2)
        profile = "8 Thread Competitive"
    elif logical >= 8:
        threads = 6
        mask = mask_skip_first(logical, 6, 1)
        profile = "6 Thread Balanced"
    else:
        threads = max(1, logical - 1)
        mask = mask_skip_first(logical, threads, 0)
        profile = "Safe Mode"

    return {
        "cpu": cpu_name(),
        "gpu": gpu_name(),
        "ram_gb": ram_gb(),
        "logical": logical,
        "threads": threads,
        "ram_mb": 8192,
        "affinity": mask,
        "profile": profile,
        "gameloop_path": find_gameloop()
    }

class PanelLoopFullV3(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_TITLE} - {AUTHOR}")
        self.geometry("1280x820")
        self.minsize(1180, 740)
        self.configure(bg="#07090d")
        self.profile = build_profile()
        self.engine_running = False
        self.engine_thread = None
        self.loop_seconds = 5
        self.glow = False

        self.build_ui()
        self.refresh_cards()
        self.log("Panel Loop Full V3 Pro loaded.")
        self.log("Safe performance engine ready.")
        self.log("Recommended flow: START ULTRA STABILITY ENGINE → START GAMELOOP OPTIMIZED.")
        self.animate_title()

    def build_ui(self):
        header = tk.Frame(self, bg="#07090d", height=135)
        header.pack(fill="x")

        self.title_label = tk.Label(header, text="PANEL LOOP FULL V3 PRO", bg="#07090d",
                                    fg="#00ffd5", font=("Consolas", 34, "bold"))
        self.title_label.place(x=26, y=18)

        tk.Label(header, text="SMART STABILITY ENGINE FOR PUBG GAMELOOP",
                 bg="#07090d", fg="#00ffd5", font=("Consolas", 16, "bold")).place(x=30, y=75)

        tk.Label(header, text=f"Made by {AUTHOR} © 2026  |  {VERSION}",
                 bg="#07090d", fg="#a7a7a7", font=("Consolas", 11)).place(x=30, y=105)

        tk.Label(header, text="SAFE BUILD ☑", bg="#07090d", fg="#31ff47",
                 font=("Consolas", 14, "bold"), relief="solid", bd=1,
                 padx=15, pady=7).place(x=1010, y=30)

        self.engine_status = tk.Label(header, text="ENGINE STATUS: ● OFF",
                                      bg="#07090d", fg="#ffdf5d",
                                      font=("Consolas", 13, "bold"))
        self.engine_status.place(x=930, y=88)

        tk.Frame(self, bg="#00ffd5", height=2).pack(fill="x")

        body = tk.Frame(self, bg="#07090d")
        body.pack(fill="both", expand=True, padx=22, pady=18)

        left = tk.Frame(body, bg="#07090d", width=365)
        left.pack(side="left", fill="y")

        tk.Label(left, text="⚡ EXECUTION PROTOCOLS", bg="#07090d",
                 fg="white", font=("Consolas", 16, "bold")).pack(anchor="w", pady=(0, 12))

        self.button(left, "🔥 START ULTRA STABILITY ENGINE", "#31ff47", self.start_engine)
        self.button(left, "🛑 STOP ENGINE", "#ff4d6d", self.stop_engine)
        self.button(left, "🎮 START GAMELOOP OPTIMIZED", "#4aa3ff", self.start_gameloop)
        self.button(left, "🧠 AUTO 12 THREAD AFFINITY", "#ffdf5d", self.set_12_thread_mode)
        self.button(left, "🔁 RE-APPLY AOW/AFFINITY NOW", "#ffdf5d", self.apply_all_now)
        self.button(left, "🎯 FORCE GPU MODE", "#00ffd5", self.force_gpu_mode)
        self.button(left, "⌨ INPUT BOOST PRO", "#9b5cff", self.input_boost)
        self.button(left, "🧹 SAFE BACKGROUND CLEAN", "#ff9f43", self.safe_background_clean)
        self.button(left, "🧼 CACHE CLEAN", "#ff6b6b", self.clean_cache)
        self.button(left, "📊 REFRESH HARDWARE INFO", "#4aa3ff", self.refresh_hardware)
        self.button(left, "↩ RESTORE DEFAULTS", "#aaaaaa", self.restore_defaults)
        self.button(left, "❌ EXIT PANEL", "#ff4d6d", self.on_close)

        right = tk.Frame(body, bg="#07090d")
        right.pack(side="left", fill="both", expand=True, padx=(18, 0))

        cards = tk.Frame(right, bg="#07090d")
        cards.pack(fill="x")

        self.cpu_card = self.card(cards, "SYSTEM CPU", "#4aa3ff", 0, 0)
        self.ram_card = self.card(cards, "SYSTEM RAM", "#4aa3ff", 0, 1)
        self.gpu_card = self.card(cards, "SYSTEM GPU", "#31ff9f", 1, 0)
        self.engine_card = self.card(cards, "GAMELOOP / AOW ENGINE", "#ffdf5d", 1, 1)
        self.latency_card = self.card(cards, "INPUT / LATENCY PROFILE", "#9b5cff", 2, 0)
        self.session_card = self.card(cards, "SESSION STATUS", "#31ff47", 2, 1)

        cards.columnconfigure(0, weight=1)
        cards.columnconfigure(1, weight=1)

        log_frame = tk.Frame(right, bg="#101217", relief="solid", bd=1)
        log_frame.pack(fill="both", expand=True, pady=(16, 0))

        tk.Label(log_frame, text="> LIVE ENGINE LOG", bg="#101217",
                 fg="white", font=("Consolas", 15, "bold")).pack(anchor="w", padx=15, pady=10)

        self.log_box = tk.Text(log_frame, bg="#000000", fg="#31ff47",
                               insertbackground="#31ff47", font=("Consolas", 10),
                               height=15, relief="flat")
        self.log_box.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def button(self, parent, text, color, command):
        b = tk.Button(parent, text=text, command=command, bg="#15191f", fg=color,
                      activebackground="#232a33", activeforeground=color,
                      relief="flat", font=("Consolas", 10, "bold"),
                      anchor="w", padx=18, pady=10)
        b.pack(fill="x", pady=4)

    def card(self, parent, title, color, row, col):
        frame = tk.Frame(parent, bg="#101217", relief="solid", bd=1, width=395, height=118)
        frame.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
        frame.pack_propagate(False)

        tk.Label(frame, text=title, bg="#101217", fg=color,
                 font=("Consolas", 13, "bold")).pack(anchor="w", padx=18, pady=(12, 0))

        label = tk.Label(frame, text="", bg="#101217", fg="white",
                         font=("Consolas", 10), justify="left")
        label.pack(anchor="w", padx=18, pady=8)
        return label

    def animate_title(self):
        self.glow = not self.glow
        self.title_label.config(fg="#00ffd5" if self.glow else "#00bfa8")
        self.after(700, self.animate_title)

    def log(self, msg):
        self.log_box.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.log_box.see("end")

    def refresh_cards(self):
        p = self.profile
        self.cpu_card.config(text=f"CPU: {p['cpu']}\nLogical threads: {p['logical']}\nUsing: {p['threads']} threads\nAffinity mask: {p['affinity']}")
        self.ram_card.config(text=f"System RAM: {p['ram_gb']} GB\nGameLoop target: {p['ram_mb']} MB\nRecommended UI: 8192M")
        self.gpu_card.config(text=f"GPU: {p['gpu']}\nPreference: High Performance\nNote: GPU % depends on GameLoop")
        self.engine_card.config(text=f"Profile: {p['profile']}\nAOW + Emulator: High Priority\nLoop: {'ON' if self.engine_running else 'OFF'}")
        self.latency_card.config(text="Keyboard: fastest repeat\nMouse acceleration: OFF\nGame Mode: ON\nNo hacks / no bypass")
        self.session_card.config(text=f"Status: {'RUNNING' if self.engine_running else 'STOPPED'}\nLoop interval: {self.loop_seconds}s\nGameLoop path: {'FOUND' if p['gameloop_path'] else 'NOT FOUND'}")

    def refresh_hardware(self):
        self.profile = build_profile()
        self.refresh_cards()
        self.log("Hardware info refreshed.")

    def start_engine(self):
        if self.engine_running:
            self.log("Ultra Stability Engine already running.")
            return
        self.engine_running = True
        self.engine_status.config(text="ENGINE STATUS: ● ON", fg="#31ff47")
        self.refresh_cards()
        self.log("Ultra Stability Engine started.")
        self.apply_all_now()
        self.engine_thread = threading.Thread(target=self.engine_loop, daemon=True)
        self.engine_thread.start()

    def stop_engine(self):
        self.engine_running = False
        self.engine_status.config(text="ENGINE STATUS: ● OFF", fg="#ffdf5d")
        self.refresh_cards()
        self.log("Ultra Stability Engine stopped.")

    def engine_loop(self):
        while self.engine_running:
            try:
                self.apply_affinity_and_priority(silent=True)
                self.monitor_processes()
            except Exception as e:
                self.log(f"Engine loop error: {e}")
            time.sleep(self.loop_seconds)

    def monitor_processes(self):
        ps = "Get-Process -Name AndroidEmulatorEx,aow_exe,AppMarket -ErrorAction SilentlyContinue | Select-Object -ExpandProperty ProcessName"
        out = run_ps(ps, timeout=10)
        if out:
            self.after(0, lambda: self.engine_status.config(text="ENGINE STATUS: ● LOCKING", fg="#31ff47"))
        else:
            self.after(0, lambda: self.engine_status.config(text="ENGINE STATUS: ● WAITING", fg="#ffdf5d"))

    def set_12_thread_mode(self):
        logical = logical_cores()
        if logical >= 16:
            self.profile["threads"] = 12
            self.profile["affinity"] = mask_skip_first(logical, 12, 4)
            self.profile["profile"] = "Manual 12 Thread Ultra Stable"
            self.profile["ram_mb"] = 8192
            self.save_profile()
            self.refresh_cards()
            self.log("12 Thread mode active: CPU 4-15 for GameLoop, CPU 0-3 free for Windows.")
            self.apply_affinity_and_priority()
        else:
            self.log("CPU has less than 16 logical threads. Auto profile is recommended.")

    def apply_all_now(self):
        self.set_high_performance()
        self.force_gpu_mode()
        self.input_boost(silent=True)
        self.apply_affinity_and_priority()
        self.save_profile()
        self.refresh_cards()
        self.log("All stability optimizations applied.")

    def apply_affinity_and_priority(self, silent=False):
        mask = self.profile["affinity"]
        names = ",".join([f"'{n}'" for n in GAMELOOP_PROCESSES])
        ps = f"""
        $names=@({names});
        foreach($n in $names){{
          Get-Process -Name $n -ErrorAction SilentlyContinue | ForEach-Object {{
            try {{ if($_.ProcessName -ne 'adb'){{$_.PriorityClass='High'}} }} catch {{}}
            try {{ if($_.ProcessName -ne 'QMEmulatorService'){{$_.ProcessorAffinity={mask}}} }} catch {{}}
          }}
        }}
        """
        run_ps(ps, timeout=15)
        if not silent:
            self.log(f"Applied High priority + affinity mask {mask} to GameLoop/AOW processes.")
        self.refresh_cards()

    def start_gameloop(self):
        path = self.profile.get("gameloop_path")
        if not path:
            self.log("GameLoop not found in default paths.")
            messagebox.showwarning("GameLoop not found", "GameLoop was not found in default paths.")
            return

        if not self.engine_running:
            self.start_engine()

        try:
            subprocess.Popen([path])
            self.log(f"GameLoop launched: {path}")
            self.after(10000, self.apply_affinity_and_priority)
            self.after(18000, self.apply_affinity_and_priority)
            self.after(26000, self.apply_affinity_and_priority)
        except Exception as e:
            self.log(f"Could not start GameLoop: {e}")

    def set_high_performance(self):
        run_ps("powercfg /S SCHEME_MIN", timeout=10)
        self.log("Power plan set to High Performance.")

    def force_gpu_mode(self):
        paths = []
        if self.profile.get("gameloop_path"):
            paths.append(self.profile["gameloop_path"])
        paths.extend(GAMELOOP_PATHS)

        for exe in dict.fromkeys(paths):
            ps = f"""
            New-Item -Path 'HKCU:\\Software\\Microsoft\\DirectX\\UserGpuPreferences' -Force | Out-Null
            New-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\DirectX\\UserGpuPreferences' -Name '{exe}' -Value 'GpuPreference=2;' -PropertyType String -Force | Out-Null
            """
            run_ps(ps, timeout=10)
        self.log("Windows Graphics Preference set to High Performance for GameLoop paths.")

    def input_boost(self, silent=False):
        ps = r"""
        Set-ItemProperty -Path 'HKCU:\Control Panel\Keyboard' -Name 'KeyboardDelay' -Value 0
        Set-ItemProperty -Path 'HKCU:\Control Panel\Keyboard' -Name 'KeyboardSpeed' -Value 31
        Set-ItemProperty -Path 'HKCU:\Control Panel\Mouse' -Name 'MouseSpeed' -Value 0
        Set-ItemProperty -Path 'HKCU:\Control Panel\Mouse' -Name 'MouseThreshold1' -Value 0
        Set-ItemProperty -Path 'HKCU:\Control Panel\Mouse' -Name 'MouseThreshold2' -Value 0
        New-Item -Path 'HKCU:\Software\Microsoft\GameBar' -Force | Out-Null
        New-ItemProperty -Path 'HKCU:\Software\Microsoft\GameBar' -Name 'AllowAutoGameMode' -Value 1 -PropertyType DWORD -Force | Out-Null
        """
        run_ps(ps, timeout=10)
        self.log("Input Boost Pro applied.")
        if not silent:
            messagebox.showinfo("Input Boost", "Input Boost Pro applied. Restart Windows for best effect.")

    def safe_background_clean(self):
        names = ",".join([f"'{n}'" for n in SAFE_BACKGROUND_PROCESSES])
        ps = f"""
        $names=@({names});
        foreach($n in $names){{
            Get-Process -Name $n -ErrorAction SilentlyContinue | ForEach-Object {{
                try {{ Stop-Process -Id $_.Id -Force }} catch {{}}
            }}
        }}
        """
        run_ps(ps, timeout=15)
        self.log("Safe background cleaner completed.")

    def clean_cache(self):
        self.log("Cleaning cache...")
        dirs = [
            os.path.join(os.getenv("LOCALAPPDATA", ""), "D3DSCache"),
            os.path.join(os.getenv("LOCALAPPDATA", ""), "NVIDIA", "DXCache"),
            os.path.join(os.getenv("LOCALAPPDATA", ""), "NVIDIA", "GLCache"),
            os.getenv("TEMP", "")
        ]
        cleaned = 0
        for directory in dirs:
            if directory and os.path.exists(directory):
                for root, _, files in os.walk(directory):
                    for file in files:
                        try:
                            os.remove(os.path.join(root, file))
                            cleaned += 1
                        except:
                            pass
        self.log(f"Cache clean finished. Files cleaned: {cleaned}")

    def restore_defaults(self):
        if not messagebox.askyesno("Restore Defaults", "Restore keyboard/mouse/power defaults?"):
            return
        self.stop_engine()
        ps = r"""
        Set-ItemProperty -Path 'HKCU:\Control Panel\Keyboard' -Name 'KeyboardDelay' -Value 1
        Set-ItemProperty -Path 'HKCU:\Control Panel\Keyboard' -Name 'KeyboardSpeed' -Value 15
        Set-ItemProperty -Path 'HKCU:\Control Panel\Mouse' -Name 'MouseSpeed' -Value 1
        Set-ItemProperty -Path 'HKCU:\Control Panel\Mouse' -Name 'MouseThreshold1' -Value 6
        Set-ItemProperty -Path 'HKCU:\Control Panel\Mouse' -Name 'MouseThreshold2' -Value 10
        powercfg /S SCHEME_BALANCED
        New-Item -Path 'HKCU:\Software\Microsoft\GameBar' -Force | Out-Null
        New-ItemProperty -Path 'HKCU:\Software\Microsoft\GameBar' -Name 'AllowAutoGameMode' -Value 0 -PropertyType DWORD -Force | Out-Null
        """
        run_ps(ps, timeout=15)
        self.log("Defaults restored. Restart recommended.")

    def save_profile(self):
        try:
            PROFILE_FILE.write_text(json.dumps(self.profile, indent=2), encoding="utf-8")
        except Exception as e:
            self.log(f"Profile save failed: {e}")

    def on_close(self):
        self.engine_running = False
        self.destroy()

if __name__ == "__main__":
    app = PanelLoopFullV3()
    app.mainloop()
