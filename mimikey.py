import customtkinter as ctk
import pyautogui
import time
import random
import threading
import sys
import platform
import json
import os
import datetime
from tkinter import messagebox, filedialog
from pynput import keyboard

# -------------------------------------------------------------------
# CONSTANTS & CONFIGURATION
# -------------------------------------------------------------------

ADJACENCY_MAP = {
    'a': ['q', 'w', 's', 'z'], 'b': ['v', 'g', 'h', 'n'], 'c': ['x', 'd', 'f', 'v'],
    'd': ['s', 'e', 'r', 'f', 'c', 'x'], 'e': ['w', 's', 'd', 'r'], 'f': ['d', 'r', 't', 'g', 'v', 'c'],
    'g': ['f', 't', 'y', 'h', 'b', 'v'], 'h': ['g', 'y', 'u', 'j', 'n', 'b'], 'i': ['u', 'j', 'k', 'o'],
    'j': ['h', 'u', 'i', 'k', 'm', 'n'], 'k': ['j', 'i', 'o', 'l', 'm'], 'l': ['k', 'o', 'p'],
    'm': ['n', 'j', 'k'], 'n': ['b', 'h', 'j', 'm'], 'o': ['i', 'k', 'l', 'p'], 'p': ['o', 'l'],
    'q': ['a', 'w'], 'r': ['e', 'd', 'f', 't'], 's': ['a', 'w', 'e', 'd', 'x', 'z'],
    't': ['r', 'f', 'g', 'y'], 'u': ['y', 'h', 'j', 'i'], 'v': ['c', 'f', 'g', 'b'],
    'w': ['q', 'a', 's', 'e'], 'x': ['z', 's', 'd', 'c'], 'y': ['t', 'g', 'h', 'u'],
    'z': ['a', 's', 'x'], ' ': [' '],
}

COMMON_MISTAKES = {
    'their': 'there', 'there': 'their', 'youre': 'your', 'your': 'youre',
    'too': 'to', 'to': 'too', 'its': 'it\'s', 'it\'s': 'its',
    'effect': 'affect', 'affect': 'effect', 'than': 'then', 'then': 'than'
}

SETTINGS_FILE = "mimikey_settings.json"

pyautogui.FAILSAFE = True

# --- Theme Palettes ---
THEMES = {
    "Jungle": {
        "bg": "#073b3a", "frame": "#0b6e4f", "accent": "#6bbf59",
        "text": "#FFF8E7", "text_sec": "#ddb771", "hover": "#4a9c3d" 
    },
    "Cyber": {
        "bg": "#001011", "frame": "#093a3e", "accent": "#3aafb9",
        "text": "#E0FFFF", "text_sec": "#97f3f7", "hover": "#2a8f99"
    },
    "Spice": {
        "bg": "#cc5803", "frame": "#e2711d", "accent": "#ffb627",
        "text": "#FFFFFF", "text_sec": "#ffe6b3", "hover": "#e09f1f"
    },
    "Cotton Candy": {
        "bg": "#ffe8f2", "frame": "#fff0f6", "accent": "#ffb7b2",
        "text": "#6d6d6d", "text_sec": "#888888", "hover": "#ffdac1"
    },
    "Matrix": {
        "bg": "#000000", "frame": "#0d0d0d", "accent": "#00ff41",
        "text": "#00ff41", "text_sec": "#008f11", "hover": "#003b00"
    },
    "Dracula": {
        "bg": "#282a36", "frame": "#44475a", "accent": "#bd93f9",
        "text": "#f8f8f2", "text_sec": "#6272a4", "hover": "#ff79c6"
    }
}

class MimikeyApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("Mimikey V10.0 - Masterpiece")
        self.geometry("950x850") # Increased height for Log Terminal
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Logic State
        self.is_running = False
        self.is_paused = False
        self.pause_event = threading.Event()
        self.stop_event = threading.Event()
        self.typing_thread = None
        self.last_ui_update_time = 0

        # Config Params
        self.current_wpm = 70.0
        self.current_error_rate = 0.02
        self.current_perfectionism = 0.95
        self.start_delay = 5 # Default
        
        # Internal Burst State
        self.in_burst_mode = True
        self.words_until_switch = 0
        
        # Initial Theme
        self.current_theme = "Cyber" 

        self.setup_ui()
        
        self.after(1000, self.start_hotkey_listener)
        
        # Load Settings (Overrides Defaults)
        self.load_settings()

    def setup_ui(self):
        # --- Layout: Sidebar + Main ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. Sidebar (Controls)
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=30)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        self.setup_sidebar()

        # 2. Main Area (Input & Monitor)
        self.main_area = ctk.CTkFrame(self, corner_radius=30)
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=(0, 15), pady=15)
        self.setup_main_area()

    def setup_sidebar(self):
        self.sidebar.grid_rowconfigure(20, weight=1) # Push bottom items down

        # Branding
        self.lbl_brand = ctk.CTkLabel(self.sidebar, text="Mimikey", font=("Roboto Medium", 28, "bold"))
        self.lbl_brand.grid(row=0, column=0, padx=25, pady=(20, 5), sticky="w")
        
        self.lbl_subtitle = ctk.CTkLabel(self.sidebar, text="Humanize Your Text", font=("Roboto Medium", 14))
        self.lbl_subtitle.grid(row=1, column=0, padx=27, pady=(0, 15), sticky="w")

        # --- Theme Selector ---
        self.lbl_theme = ctk.CTkLabel(self.sidebar, text="Theme", font=("Roboto Medium", 14), anchor="w")
        self.lbl_theme.grid(row=2, column=0, padx=25, pady=(5, 5), sticky="w")
        
        self.opt_theme = ctk.CTkOptionMenu(self.sidebar, 
                                           values=list(THEMES.keys()),
                                           command=self.apply_theme,
                                           corner_radius=20,
                                           font=("Roboto Medium", 12))
        self.opt_theme.grid(row=3, column=0, padx=25, pady=(0, 10), sticky="ew")

        # --- Divider ---
        self.div1 = ctk.CTkFrame(self.sidebar, height=2, corner_radius=10)
        self.div1.grid(row=4, column=0, sticky="ew", padx=25, pady=5)

        # --- Presets ---
        self.lbl_preset = ctk.CTkLabel(self.sidebar, text="Presets", font=("Roboto Medium", 14), anchor="w")
        self.lbl_preset.grid(row=5, column=0, padx=25, pady=(5, 5), sticky="w")
        
        self.opt_preset = ctk.CTkOptionMenu(self.sidebar, 
                                            values=["Student (Fast/Messy)", "Professional (Clean)", "Grandma (Slow)", "Speed Demon (Max)"],
                                            command=self.apply_preset,
                                            corner_radius=20,
                                            font=("Roboto Medium", 12))
        self.opt_preset.grid(row=6, column=0, padx=25, pady=(0, 10), sticky="ew")
        self.opt_preset.set("Professional (Clean)")

        # --- Sliders ---
        self.lbl_wpm = ctk.CTkLabel(self.sidebar, text="Target WPM: 70", font=("Roboto Medium", 13), anchor="w")
        self.lbl_wpm.grid(row=7, column=0, padx=25, pady=(5, 5), sticky="w")
        self.slider_wpm = ctk.CTkSlider(self.sidebar, from_=10, to=230, number_of_steps=220, command=self.update_wpm_label)
        self.slider_wpm.grid(row=8, column=0, padx=25, pady=(0, 10), sticky="ew")
        self.slider_wpm.set(70)
        self.slider_wpm.bind("<ButtonRelease-1>", lambda e: self.calculate_estimated_time())

        # Sloppiness
        self.lbl_error = ctk.CTkLabel(self.sidebar, text="Sloppiness: 2%", font=("Roboto Medium", 13), anchor="w")
        self.lbl_error.grid(row=9, column=0, padx=25, pady=(5, 0), sticky="w")
        self.lbl_error_desc = ctk.CTkLabel(self.sidebar, text="Chance of miss-hitting adjacent keys.", font=("Roboto", 10), text_color="gray60", anchor="w")
        self.lbl_error_desc.grid(row=10, column=0, padx=25, pady=(0, 5), sticky="w")
        
        self.slider_error = ctk.CTkSlider(self.sidebar, from_=0, to=10, number_of_steps=100, command=self.update_error_label)
        self.slider_error.grid(row=11, column=0, padx=25, pady=(0, 10), sticky="ew")
        self.slider_error.set(2)

        # Perfectionism
        self.lbl_perfect = ctk.CTkLabel(self.sidebar, text="Perfectionism: 95%", font=("Roboto Medium", 13), anchor="w")
        self.lbl_perfect.grid(row=12, column=0, padx=25, pady=(5, 0), sticky="w")
        self.lbl_perfect_desc = ctk.CTkLabel(self.sidebar, text="Chance the bot fixes its own typos.", font=("Roboto", 10), text_color="gray60", anchor="w")
        self.lbl_perfect_desc.grid(row=13, column=0, padx=25, pady=(0, 5), sticky="w")

        self.slider_perfect = ctk.CTkSlider(self.sidebar, from_=80, to=100, number_of_steps=20, command=self.update_perfect_label)
        self.slider_perfect.grid(row=14, column=0, padx=25, pady=(0, 10), sticky="ew")
        self.slider_perfect.set(95)
        
        # --- Start Delay (New) ---
        self.lbl_delay = ctk.CTkLabel(self.sidebar, text=f"Start Delay: {self.start_delay}s", font=("Roboto Medium", 13), anchor="w")
        self.lbl_delay.grid(row=15, column=0, padx=25, pady=(5, 5), sticky="w")
        self.slider_delay = ctk.CTkSlider(self.sidebar, from_=2, to=10, number_of_steps=8, command=self.update_delay_label)
        self.slider_delay.grid(row=16, column=0, padx=25, pady=(0, 10), sticky="ew")
        self.slider_delay.set(self.start_delay)

        # --- Bottom Status ---
        self.lbl_action_log = ctk.CTkLabel(self.sidebar, text="System Ready", font=("Roboto Medium", 11))
        self.lbl_action_log.grid(row=21, column=0, padx=25, pady=(10, 0), sticky="s")
        
        self.lbl_hotkeys = ctk.CTkLabel(self.sidebar, text="Hotkeys: F9 (Start/Pause) • F10 (Stop)", font=("Roboto Medium", 10))
        self.lbl_hotkeys.grid(row=22, column=0, padx=25, pady=(0, 5), sticky="s")

        # Pin Switch
        self.switch_pin = ctk.CTkSwitch(self.sidebar, text="Pin on Top", font=("Roboto Medium", 10), command=self.toggle_pin)
        self.switch_pin.grid(row=23, column=0, padx=25, pady=(5, 20), sticky="s")


    def setup_main_area(self):
        self.main_area.grid_rowconfigure(1, weight=1) # Textbox gets weight
        self.main_area.grid_columnconfigure(0, weight=1)

        # 0. File Import Controls
        self.frame_file = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.frame_file.grid(row=0, column=0, sticky="ew", padx=30, pady=(25, 0))
        
        self.btn_load = ctk.CTkButton(self.frame_file, text="📂 Load Text File", width=140, command=self.load_text_file, font=("Roboto Medium", 12))
        self.btn_load.pack(side="left", padx=(0, 10))
        
        self.btn_clear = ctk.CTkButton(self.frame_file, text="❌ Clear", width=80, fg_color="#555", hover_color="#333", command=self.clear_text, font=("Roboto Medium", 12))
        self.btn_clear.pack(side="left")

        # 1. Input Area
        self.textbox = ctk.CTkTextbox(self.main_area, font=("Roboto Medium", 15), corner_radius=20, border_width=2)
        self.textbox.grid(row=1, column=0, sticky="nsew", padx=30, pady=(15, 20))
        self.textbox.insert("0.0", "Paste your text or load a file...")
        self.textbox.bind("<KeyRelease>", self.calculate_estimated_time)

        # 2. Monitor & Controls Bar
        self.frame_monitor = ctk.CTkFrame(self.main_area, height=180, corner_radius=25, fg_color="transparent")
        self.frame_monitor.grid(row=2, column=0, sticky="ew", padx=30, pady=(0, 20))
        self.frame_monitor.grid_columnconfigure(1, weight=1)

        # Monitor Content Container
        self.frame_stats = ctk.CTkFrame(self.frame_monitor, corner_radius=20)
        self.frame_stats.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        self.frame_stats.grid_columnconfigure(1, weight=1)

        # Stats Row
        self.status_capsule = ctk.CTkLabel(self.frame_stats, text=" READY ", width=110, height=32, corner_radius=16, fg_color="gray30", font=("Roboto Medium", 12, "bold"))
        self.status_capsule.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        self.lbl_stats = ctk.CTkLabel(self.frame_stats, text="Est. Time: --:--", font=("Roboto Medium", 16, "bold"))
        self.lbl_stats.grid(row=0, column=1, padx=20, pady=15, sticky="e")
        
        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self.frame_stats, height=14, corner_radius=7)
        self.progress_bar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 20))
        self.progress_bar.set(0)

        # 3. Live Action Terminal
        self.txt_log = ctk.CTkTextbox(self.frame_monitor, height=80, corner_radius=15, font=("Courier", 12), fg_color="#1e1e1e", text_color="#00ff41")
        self.txt_log.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        self.txt_log.insert("0.0", f"[{datetime.datetime.now().strftime('%H:%M:%S')}] System initialized.\n")
        self.txt_log.configure(state="disabled")

        # 4. Media Controls
        self.frame_media = ctk.CTkFrame(self.frame_monitor, fg_color="transparent")
        self.frame_media.grid(row=3, column=0, columnspan=2)
        
        self.btn_play = ctk.CTkButton(self.frame_media, text="▶ START", width=130, height=45, corner_radius=22, font=("Roboto Medium", 14), command=self.start_typing_thread)
        self.btn_play.pack(side="left", padx=10)
        
        self.btn_pause = ctk.CTkButton(self.frame_media, text="⏸ PAUSE", width=130, height=45, corner_radius=22, font=("Roboto Medium", 14), state="disabled", command=self.pause_typing)
        self.btn_pause.pack(side="left", padx=10)
        
        self.btn_stop = ctk.CTkButton(self.frame_media, text="⏹ STOP", width=130, height=45, corner_radius=22, font=("Roboto Medium", 14), state="disabled", command=self.stop_typing)
        self.btn_stop.pack(side="left", padx=10)


    # --- Theme Logic ---
    def apply_theme(self, theme_name):
        self.current_theme = theme_name
        colors = THEMES[theme_name]
        
        self.configure(fg_color=colors["bg"])
        self.sidebar.configure(fg_color=colors["frame"])
        self.div1.configure(fg_color=colors["accent"])
        
        text_col = colors["text"]
        
        for lbl in [self.lbl_brand, self.lbl_subtitle, self.lbl_theme, self.lbl_preset, self.lbl_wpm, self.lbl_error, self.lbl_perfect, self.lbl_hotkeys, self.lbl_delay, self.lbl_error_desc, self.lbl_perfect_desc]:
             if "desc" in str(lbl):
                 lbl.configure(text_color=colors.get("text_sec", "gray60"))
             else:
                 lbl.configure(text_color=text_col)
             
        self.lbl_action_log.configure(text_color=colors["text_sec"])
        self.switch_pin.configure(text_color=text_col, progress_color=colors["accent"])

        self.main_area.configure(fg_color=colors["bg"])
        self.textbox.configure(fg_color=colors["frame"], text_color=text_col, border_color=colors["accent"])
        self.frame_stats.configure(fg_color=colors["frame"])
        self.lbl_stats.configure(text_color=text_col)
        
        self.opt_theme.configure(fg_color=colors["bg"], button_color=colors["accent"], text_color=text_col) 
        self.opt_preset.configure(fg_color=colors["bg"], button_color=colors["accent"], text_color=text_col)
        
        self.slider_wpm.configure(button_color=colors["accent"], progress_color=colors["accent"])
        self.slider_error.configure(button_color=colors["accent"], progress_color=colors["accent"])
        self.slider_perfect.configure(button_color=colors["accent"], progress_color=colors["accent"])
        self.slider_delay.configure(button_color=colors["accent"], progress_color=colors["accent"])
        self.progress_bar.configure(progress_color=colors["accent"])

        # Log Terminal Coloring
        self.txt_log.configure(text_color=colors["accent"], fg_color="#1a1a1a")

        self.btn_play.configure(fg_color=colors["accent"], hover_color=colors["hover"], text_color=colors["bg"]) 
        self.btn_pause.configure(fg_color=colors["text_sec"], hover_color=colors["hover"], text_color=colors["bg"])
        self.btn_stop.configure(fg_color="#ff5e5e", hover_color="#c93838", text_color="white")
        
        self.btn_load.configure(fg_color=colors["frame"], hover_color=colors["accent"], text_color=text_col)

        self.status_capsule.configure(fg_color=colors["bg"], text_color=text_col)

    # --- Callbacks ---

    def toggle_pin(self):
        self.attributes('-topmost', self.switch_pin.get())

    def update_delay_label(self, value):
        self.start_delay = int(value)
        self.lbl_delay.configure(text=f"Start Delay: {self.start_delay}s")

    def load_text_file(self):
        try:
            filename = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.clear_text()
                    self.textbox.insert("0.0", content)
                    self.calculate_estimated_time()
                    self.log_action(f"Loaded file: {os.path.basename(filename)}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load file: {e}")

    def clear_text(self):
        self.textbox.delete("0.0", "end")
        self.calculate_estimated_time()
        self.lbl_stats.configure(text="Est. Time: --:--")
        self.log_action("Cleared text buffer.")

    def calculate_estimated_time(self, event=None):
        if self.is_running: return # Use live stats while running
        
        text = self.textbox.get("1.0", "end-1c")
        if not text:
            self.lbl_stats.configure(text="Est. Time: --:--")
            return

        wpm = max(5, self.current_wpm)
        avg_char_delay = 60.0 / (wpm * 5.0)
        total_chars = len(text)
        
        est_sec = total_chars * avg_char_delay * 1.1 # 10% buffer
        mins, secs = divmod(int(est_sec), 60)
        self.lbl_stats.configure(text=f"Est. Time: {mins:02}:{secs:02}")

    def update_wpm_label(self, value):
        self.current_wpm = value
        text = f"Target WPM: {int(value)}"
        if value > 150:
            text += " (HIGH RISK!)"
            self.lbl_wpm.configure(text=text, text_color="#ff5e5e")
        else:
            colors = THEMES[self.current_theme]
            self.lbl_wpm.configure(text=text, text_color=colors["text"])
        self.opt_preset.set("Custom")
        self.calculate_estimated_time()

    def update_error_label(self, value):
        self.current_error_rate = value / 100.0
        self.lbl_error.configure(text=f"Sloppiness: {int(value)}%")
        self.opt_preset.set("Custom")
        
    def update_perfect_label(self, value):
        self.current_perfectionism = value / 100.0
        self.lbl_perfect.configure(text=f"Perfectionism: {int(value)}%")
        self.opt_preset.set("Custom")

    def apply_preset(self, choice):
        if "Student" in choice:
            self.slider_wpm.set(120); self.slider_error.set(8); self.slider_perfect.set(85)
        elif "Professional" in choice:
            self.slider_wpm.set(70); self.slider_error.set(1); self.slider_perfect.set(99)
        elif "Grandma" in choice:
            self.slider_wpm.set(25); self.slider_error.set(2); self.slider_perfect.set(90)
        elif "Speed Demon" in choice:
            self.slider_wpm.set(200); self.slider_error.set(5); self.slider_perfect.set(95)
        
        self.update_wpm_label(self.slider_wpm.get())
        self.update_error_label(self.slider_error.get())
        self.update_perfect_label(self.slider_perfect.get())
        self.opt_preset.set(choice)
        self.log_action(f"Applied preset: {choice}")

    def update_ui_state(self, state):
        colors = THEMES[self.current_theme]
        if state == "running":
            self.btn_play.configure(state="disabled", text="RUNNING")
            self.btn_pause.configure(state="normal", text="⏸ PAUSE")
            self.btn_stop.configure(state="normal")
            self.textbox.configure(state="disabled")
            self.status_capsule.configure(text=" TYPING ", fg_color=colors["accent"], text_color=colors["bg"])
            self.btn_load.configure(state="disabled")
            self.btn_clear.configure(state="disabled")
        elif state == "paused":
            self.btn_pause.configure(text="▶ RESUME")
            self.status_capsule.configure(text=" PAUSED ", fg_color=colors["text_sec"], text_color=colors["bg"])
            self.log_action("Engine paused.")
        elif state == "stopped":
            self.btn_play.configure(state="normal", text="▶ START")
            self.btn_pause.configure(state="disabled", text="⏸ PAUSE")
            self.btn_stop.configure(state="disabled")
            self.textbox.configure(state="normal")
            self.status_capsule.configure(text=" STOPPED ", fg_color="#ff5e5e", text_color="white")
            self.btn_load.configure(state="normal")
            self.btn_clear.configure(state="normal")
            self.progress_bar.set(0)
            self.calculate_estimated_time()
            self.log_action("Engine stopped.")

    # --- Persistence ---
    def save_settings(self):
        data = {
            "wpm": self.slider_wpm.get(),
            "error_rate": self.slider_error.get(),
            "perfectionism": self.slider_perfect.get(),
            "theme": self.current_theme,
            "pinned": self.switch_pin.get(),
            "start_delay": self.start_delay
        }
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def load_settings(self):
        if not os.path.exists(SETTINGS_FILE): return
        try:
            with open(SETTINGS_FILE, 'r') as f:
                data = json.load(f)
            
            if "wpm" in data: 
                self.slider_wpm.set(data["wpm"])
                self.update_wpm_label(data["wpm"])
            if "error_rate" in data: 
                self.slider_error.set(data["error_rate"])
                self.update_error_label(data["error_rate"])
            if "perfectionism" in data: 
                self.slider_perfect.set(data["perfectionism"])
                self.update_perfect_label(data["perfectionism"])
            if "theme" in data: 
                self.apply_theme(data["theme"])
                self.opt_theme.set(data["theme"])
            if "pinned" in data: 
                if data["pinned"]: 
                    self.switch_pin.select()
                    self.toggle_pin()
            if "start_delay" in data:
                self.start_delay = data["start_delay"]
                self.slider_delay.set(self.start_delay)
                self.update_delay_label(self.start_delay)
                
        except Exception as e:
            print(f"Failed to load settings: {e}")

    def on_close(self):
        self.save_settings()
        self.destroy()

    # --- Live Action Terminal ---
    def log_action(self, message):
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        full_msg = f"[{timestamp}] {message}\n"
        
        def _log():
            self.txt_log.configure(state="normal")
            self.txt_log.insert("end", full_msg)
            self.txt_log.see("end")
            self.txt_log.configure(state="disabled")
            
        self.after(0, _log)


    # --- Hotkeys & Threading ---

    def start_hotkey_listener(self):
        def on_press(key):
            try:
                if key == keyboard.Key.f9:
                    if not self.is_running:
                        self.after(0, self.start_typing_thread)
                    else:
                        self.after(0, self.pause_typing)
                elif key == keyboard.Key.f10:
                    if self.is_running:
                        self.after(0, self.stop_typing)
            except Exception as e:
                print(f"Hotkey Error: {e}")

        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.start()

    def sanitize_text(self, text):
        replacements = {'“': '"', '”': '"', "‘": "'", "’": "'", '–': '-', '—': '-'}
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        clean_text = ""
        for char in text:
            if ord(char) < 65535: 
                clean_text += char
        return clean_text

    def start_typing_thread(self):
        raw_text = self.textbox.get("1.0", "end-1c")
        if not raw_text: return
        
        text = self.sanitize_text(raw_text)

        self.is_running = True
        self.is_paused = False
        self.pause_event.set()
        self.stop_event.clear()
        
        self.update_ui_state("running")
        self.log_action("Engine started. Initializing...")
        
        self.typing_thread = threading.Thread(target=self.typing_logic, args=(text,))
        self.typing_thread.daemon = True
        self.typing_thread.start()

    def pause_typing(self):
        if self.is_paused:
            self.is_paused = False
            self.pause_event.set()
            self.update_ui_state("running")
            self.log_action("Engine resumed.")
        else:
            self.is_paused = True
            self.pause_event.clear()
            self.update_ui_state("paused")

    def stop_typing(self):
        if self.is_running:
            self.stop_event.set()
            self.pause_event.set()
            self.is_running = False
            self.update_ui_state("stopped")

    # --- Typist Logic ---
    def release_modifiers(self):
        if platform.system() == 'Darwin':
            for key in ['command', 'ctrl', 'option', 'shift']:
                pyautogui.keyUp(key)
            try: pyautogui.keyUp('fn')
            except: pass

    def rapid_nav_press(self, key, count):
        if count <= 0: return
        while not self.pause_event.is_set(): 
            time.sleep(0.1)
            if self.stop_event.is_set(): return

        pyautogui.press(key, presses=count, interval=0.02)
        
        if platform.system() == 'Darwin' and key in ['left', 'right', 'up', 'down', 'home', 'end']:
            pyautogui.keyUp('ctrl')
            try: pyautogui.keyUp('fn') 
            except: pass

    def get_current_delay(self):
        wpm = max(5, self.current_wpm)
        avg_char_delay = 60.0 / (wpm * 5.0)

        if self.words_until_switch <= 0:
            self.in_burst_mode = not self.in_burst_mode
            if self.in_burst_mode: 
                self.words_until_switch = random.randint(3, 8)
                self.lbl_action_log.configure(text="Mode: Burst (Fast)")
            else: 
                self.words_until_switch = random.randint(1, 2)
                self.lbl_action_log.configure(text="Mode: Fatigue (Slow)")
        
        if self.in_burst_mode:
            base = avg_char_delay * 0.8 
            variance = base * 0.2
        else:
            base = avg_char_delay * 1.5
            variance = base * 0.2

        return max(0.001, random.gauss(base, variance))

    def typing_logic(self, text):
        # User Defined Countdown
        self.log_action(f"Counting down {self.start_delay}s...")
        for i in range(self.start_delay, 0, -1):
            if self.stop_event.is_set(): 
                self.update_ui_state("stopped")
                return
            self.status_capsule.configure(text=f" T-{i}s ")
            time.sleep(1)

        self.status_capsule.configure(text=" TYPING ", fg_color=THEMES[self.current_theme]["accent"])
        self.log_action("Typing started.")
        self.release_modifiers()
        time.sleep(0.5)

        total_chars = len(text)
        chars_typed = 0
        
        major_break_threshold = random.randint(200, 500)
        wandering_threshold = random.randint(600, 900)
        
        # O(1) Optimization: Dict for corrections logic
        # {trigger_index: {error_index, correct_char}}
        pending_corrections = {} 
        
        try:
            i = 0
            while i < len(text):
                if self.stop_event.is_set(): break
                
                while not self.pause_event.is_set():
                    time.sleep(0.1)
                    if self.stop_event.is_set(): break
                
                char = text[i]

                # --- 1. Major Break ---
                if chars_typed >= major_break_threshold:
                    self.status_capsule.configure(text=" THINKING ", fg_color="orange")
                    self.log_action("Simulating human pause (thinking)...")
                    duration = random.uniform(8, 15)
                    try:
                        x, y = pyautogui.position()
                        pyautogui.moveTo(x+10, y, 0.5)
                        time.sleep(duration/2)
                        pyautogui.moveTo(x, y, 0.5)
                        time.sleep(duration/2)
                    except: time.sleep(duration)
                    chars_typed = 0
                    major_break_threshold = random.randint(200, 500)
                    self.status_capsule.configure(text=" TYPING ", fg_color=THEMES[self.current_theme]["accent"])

                # --- 2. Wandering Cursor ---
                if i > 0 and i % wandering_threshold == 0:
                     self.status_capsule.configure(text=" NAVIGATING ", fg_color="purple")
                     self.log_action("Cursor wandering...")
                     steps = random.randint(5, 10)
                     self.rapid_nav_press('up', steps)
                     time.sleep(random.uniform(1.0, 2.0))
                     self.rapid_nav_press('down', steps)
                     wandering_threshold = random.randint(600, 900)
                     self.status_capsule.configure(text=" TYPING ", fg_color=THEMES[self.current_theme]["accent"])

                # --- 3. Delayed Corrections (O(1) Lookup) ---
                if i in pending_corrections:
                    correction = pending_corrections[i] # Pop logic later to keep safe? Dictionary is safe.
                    
                    self.status_capsule.configure(text=" FIXING ", fg_color="red")
                    self.log_action(f"Navigating back to fix '{correction['wrong_char']}' -> '{correction['correct_char']}'")
                    time.sleep(0.3) 
                    
                    target = correction['error_index'] + 1
                    moves = i - target
                    if moves > 0:
                        self.rapid_nav_press('left', moves)
                        pyautogui.press('backspace')
                        time.sleep(0.05) 
                        pyautogui.write(correction['correct_char'])
                        self.rapid_nav_press('right', moves)
                    
                    del pending_corrections[i] # Remove done correction
                    time.sleep(0.3)
                    self.status_capsule.configure(text=" TYPING ", fg_color=THEMES[self.current_theme]["accent"])

                # --- 4. Typing & Context Errors & Typos ---
                typed_char = char
                
                if (i == 0 or text[i-1] in [' ', '\n']) and char.isalpha():
                    j = i
                    word = ""
                    while j < len(text) and text[j].isalpha():
                        word += text[j]
                        j += 1
                    
                    lower_word = word.lower()
                    if lower_word in COMMON_MISTAKES and random.random() < 0.10: 
                        wrong_word = COMMON_MISTAKES[lower_word]
                        if word[0].isupper(): wrong_word = wrong_word.capitalize()
                        
                        self.log_action(f"Context error: typed '{wrong_word}' instead of '{word}'.")
                        
                        if random.random() > self.current_perfectionism:
                            for wc in wrong_word:
                                pyautogui.write(wc)
                                time.sleep(self.get_current_delay())
                            i = j 
                            chars_typed += len(wrong_word)
                            continue 
                        else:
                            # Immediate fix simulation
                            for wc in wrong_word:
                                pyautogui.write(wc)
                                time.sleep(self.get_current_delay())
                            time.sleep(0.5)
                            for _ in range(len(wrong_word)):
                                pyautogui.press('backspace')
                            pass 

                if char in [' ', '\n']: self.words_until_switch -= 1
                
                # Removed speed cap check
                if char.lower() in ADJACENCY_MAP and random.random() < self.current_error_rate:
                    wrong = random.choice(ADJACENCY_MAP[char.lower()])
                    if random.random() > self.current_perfectionism:
                        typed_char = wrong
                    else:
                        if random.random() < 0.50: 
                            offset = random.randint(5, 20)
                            trigger = min(i + offset, len(text))
                            # Add to dict
                            pending_corrections[trigger] = {'error_index': i, 'correct_char': char, 'wrong_char': wrong}
                            self.log_action(f"Oops, typed '{wrong}'. Fixing in {offset} chars...")
                            typed_char = wrong
                        else:
                            # Immediate backspace
                            pyautogui.write(wrong)
                            time.sleep(random.uniform(0.05, 0.15))
                            pyautogui.press('backspace')
                            time.sleep(0.05)

                pyautogui.write(typed_char)

                delay = self.get_current_delay()
                punc_factor = 0.5 if self.current_wpm > 100 else 1.0
                if char in '.!?\n': delay += (0.4 * punc_factor)
                elif char in ',;:': delay += (0.2 * punc_factor)
                
                time.sleep(delay)
                chars_typed += 1
                i += 1 

                # Smart UI Debouncing (10 FPS limit)
                now = time.time()
                if now - self.last_ui_update_time >= 0.1:
                    pct = (i + 1) / total_chars
                    self.progress_bar.set(pct)
                    rem_chars = total_chars - (i + 1)
                    est_sec = rem_chars * delay
                    mins, secs = divmod(int(est_sec), 60)
                    self.lbl_stats.configure(text=f"Time Remaining: {mins:02}:{secs:02}")
                    self.last_ui_update_time = now

            for trigger, correction in pending_corrections.items():
                if self.stop_event.is_set(): break
                self.status_capsule.configure(text=" CLEANUP ")
                self.log_action(f"Cleanup: fixing missed typo '{correction['wrong_char']}'")
                self.rapid_nav_press('left', (len(text)-correction['error_index']-1))
                pyautogui.press('backspace')
                pyautogui.write(correction['correct_char'])
                self.rapid_nav_press('right', (len(text)-correction['error_index']-1))

            self.update_ui_state("stopped")
            self.status_capsule.configure(text=" DONE ", fg_color="#2CC985")
            self.progress_bar.set(1.0)
            self.lbl_stats.configure(text="Time Remaining: 00:00")
            self.log_action("Typing complete.")

        except pyautogui.FailSafeException:
            self.update_ui_state("stopped")
            self.status_capsule.configure(text=" FAILSAFE ", fg_color="red")
            self.log_action("Emergency Failsafe Triggered!")
        except Exception as e:
            print(f"Error: {e}")
            self.log_action(f"Error: {e}")
            self.update_ui_state("stopped")

if __name__ == "__main__":
    app = MimikeyApp()
    app.mainloop()
