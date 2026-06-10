import tkinter as tk

# Główny ekran menu umożliwiający wybór ćwiczenia
class SelectionScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        tk.Label(self, text="CYBER TRENER", font=("Helvetica", 48, "bold"), fg="#333333", bg="white").pack(pady=20)
        tk.Label(self, text="Wybierz ćwiczenie do wykonania:", font=("Helvetica", 24), fg="#333333", bg="white").pack(
            pady=20)

        # Generowanie przycisków wyboru ćwiczeń
        for exercise in ["Pajacyki", "Skip A", "Wykroki"]:
            btn = self.controller.create_button(self, exercise, lambda e=exercise: self.select_exercise(e))
            btn.pack(pady=10)

        # Przycisk historii
        self.btn_history = self.controller.create_button(
            self,
            text="HISTORIA TRENINGÓW",
            command=lambda: controller.show_screen("HistoryScreen"),
            bg="#333333",
            font=("Helvetica", 12, "bold"),
            pady=10
        )
        self.btn_history.pack(pady=20)

    # Zapisuje wybrane ćwiczenie i przechodzi do konfiguratora
    def select_exercise(self, exercise):
        self.controller.selected_exercise = exercise
        self.controller.show_screen("ConfigScreen")

    # Metoda wywoływana przy wchodzeniu na ekran
    def refresh_data(self): 
        pass
