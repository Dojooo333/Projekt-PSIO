import tkinter as tk

# Ekran służący do konfiguracji parametrów treningu (serie i powtórzenia)
class ConfigScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller

        self.title_lbl = tk.Label(self, text="", font=("Helvetica", 32, "bold"), fg="#333333", bg="white")
        self.title_lbl.pack(pady=30)

        tk.Label(self, text="Ilość serii w całym treningu:", font=("Helvetica", 20), fg="#333333", bg="white").pack(pady=(20, 5))
        # Spinbox do wyboru liczby serii
        self.spin_sets = tk.Spinbox(self, from_=1, to=10, font=("Helvetica", 20, "bold"), width=10, justify="center", bd=2, fg="#333333")
        self.spin_sets.pack(pady=10)

        tk.Label(self, text="Ilość powtórzeń w jednej serii:", font=("Helvetica", 20), fg="#333333", bg="white").pack(pady=(20, 5))
        # Spinbox do wyboru liczby powtórzeń
        self.spin_reps = tk.Spinbox(self, from_=1, to=50, font=("Helvetica", 20, "bold"), width=10, justify="center", bd=1, fg="#333333")
        self.spin_reps.pack(pady=(5, 20))

        btn_start = self.controller.create_button(
            self,
            text="Rozpocznij ćwiczenie",
            command=self.start_training
        )
        btn_start.pack(pady=40)

        btn_back = self.controller.create_button(
            self,
            text="Powrót do MENU",
            command=lambda: self.controller.show_screen("SelectionScreen")
        )
        btn_back.pack(pady=10)

    # Aktualizuje etykietę z nazwą wybranego ćwiczenia
    def refresh_data(self):
        self.title_lbl.config(text=f"Ćwiczenie: {self.controller.selected_exercise}")

    # Pobiera parametry i przechodzi do treningu
    def start_training(self):
        try:
            self.controller.total_sets = int(self.spin_sets.get())
            self.controller.total_reps = int(self.spin_reps.get())
        except ValueError:
            return # Nie rób nic, jeśli wpisano nieliczbowe znaki
        self.controller.current_set = 1
        self.controller.show_screen("TrainingScreen")
