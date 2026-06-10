import tkinter as tk
import config

# Import wątków pobocznych
from ai_service import YoloThread
from audio_service import AudioEngine, VoiceListener

# Import ekranów
from screens.menu import SelectionScreen
from screens.conf import ConfigScreen
from screens.training import TrainingScreen
from screens.summary import SummaryScreen
from screens.history import HistoryScreen

# Główne okno aplikacji i zarządzanie nawigacją
class CyberTrenerApp(tk.Tk):
    def __init__(self, model, camera1, camera2):
        super().__init__()
        self.title("Cyber Trener")

        # Dynamiczne dopasowanie rozmiaru okna
        w1 = 853 if config.CAMERA_1_MODE == "16:9" else 270
        w2 = 853 if config.CAMERA_2_MODE == "16:9" else 270
        window_w = max(1100, w1 + w2 + 80)
        window_h = 850
        self.geometry(f"{window_w}x{window_h}")

        self.state('zoomed')

        self.configure(bg="white")

        self.model = model
        self.camera1 = camera1
        self.camera2 = camera2

        self.yolo_thread = YoloThread(model, camera1, camera2)

        # Uruchamianie systemu audio i mowy
        self.audio = AudioEngine()
        self.voice_listener = VoiceListener(self)
        self.training_screen_active = False

        self.selected_exercise = "Brak"
        self.total_sets = 3
        self.total_reps = 10
        self.current_set = 1
        self.training_history = []

        self.exercise_mapping = {
            "Pajacyki": "jumping_jacks",
            "Skip A": "high_knees",
            "Wykroki": "lunges"
        }

        self.container = tk.Frame(self, bg="white")
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.screens = {}
        for ScreenClass in (SelectionScreen, ConfigScreen, TrainingScreen, SummaryScreen, HistoryScreen):
            screen_name = ScreenClass.__name__
            screen = ScreenClass(parent=self.container, controller=self)
            self.screens[screen_name] = screen
            screen.grid(row=0, column=0, sticky="nsew")

        self.show_screen("SelectionScreen")

    # Przełącza aktualnie widoczny ekran
    def show_screen(self, screen_name):
        screen = self.screens[screen_name]
        if hasattr(screen, "refresh_data"):
            screen.refresh_data()
        self.is_training_active = (screen_name == "TrainingScreen")
        screen.tkraise()

    # Generator ujednoliconych przycisków
    def create_button(self, parent, text, command, width=22, font=("Helvetica", 18, "bold"), pady=12, bg="#444444"):
        btn = tk.Button(
            parent,
            text=text,
            font=font,
            bg=bg,
            fg="white",
            width=width,
            pady=pady,
            bd=0,
            cursor="hand2",
            activebackground="#555555",
            activeforeground="white",
            command=command
        )
        # Efekt podświetlenia po najechaniu myszką
        btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#111111", fg="white") if str(b['state']) == 'normal' else None)
        btn.bind("<Leave>", lambda e, b=btn, def_bg=bg: b.config(bg=def_bg, fg="white") if str(b['state']) == 'normal' else None)
        return btn
