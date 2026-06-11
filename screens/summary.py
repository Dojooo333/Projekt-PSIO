import tkinter as tk
import os

# Ekran podsumowania treningu
class SummaryScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#FFFFFF")
        self.controller = controller
        self.end_mode = False
        tk.Label(self, text="PODSUMOWANIE WYNIKÓW", font=("Helvetica", 24, "bold"), fg="#111827", bg="#FFFFFF").pack(
            pady=20)

        # Kontener tabeli statystyk
        self.stats_container = tk.Frame(self, bg="#FFFFFF", padx=30, pady=30)
        self.stats_container.pack(fill="both", expand=True, padx=50, pady=10)

        # Główny przycisk akcji (Kolejna seria lub Zakończ)
        self.action_btn = self.controller.create_button(
            self,
            text="",
            command=self.next_step
        )
        self.action_btn.pack(pady=25)

    # Aktualizuje tabelę wyników z ekranu treningu
    def refresh_data(self):
        # Czyszczenie widżetów po poprzedniej sesji
        for w in self.stats_container.winfo_children():
            w.destroy()

        self.stats_container.config(bg="#FFFFFF", padx=20, pady=20)

        # Główny nagłówek raportu ćwiczenia
        tk.Label(
            self.stats_container,
            text=f"RAPORT: {self.controller.selected_exercise.upper()}",
            font=("Helvetica", 16, "bold"),
            fg="#111827",
            bg="#FFFFFF"
        ).pack(anchor="center", pady=(0, 20))

        # Tabela układana za pomocą siatki Grid
        table_frame = tk.Frame(self.stats_container, bg="#FFFFFF")
        table_frame.pack(fill="x", expand=True, padx=10)

        # Wyrównanie pierwszych 5 kolumn
        for i in range(5):
            table_frame.columnconfigure(i, weight=1, uniform="column")
        # Kolumna przycisku wideo (nierozciągalna)
        table_frame.columnconfigure(5, weight=0)

        # Nagłówki tabeli.
        columns = ["SERIA", "POPRAWNE", "BŁĘDNE", "CZAS", "SKUTECZNOŚĆ"]
        for col_idx, name in enumerate(columns):
            lbl = tk.Label(
                table_frame,
                text=name,
                font=("Helvetica", 10, "bold"),
                fg="#4B5563",
                bg="#F3F4F6",
                pady=10
            )
            # Wyrównanie tła nagłówków
            lbl.grid(row=0, column=col_idx, sticky="nsew", padx=1, pady=(0, 10))

        # Puste pole nagłówka nad wideo dla spójności tła
        tk.Label(table_frame, bg="#F3F4F6").grid(row=0, column=5, sticky="nsew", pady=(0, 10))

        # Generowanie wierszy wyników ze słownika sterownika
        for row_idx, s in enumerate(self.controller.training_history, start=1):
            # Efekt zebry (naprzemienne kolory wierszy)
            row_bg = "#F9FAFB" if s['set'] % 2 == 0 else "#FFFFFF"

            total = s['correct'] + s['incorrect']
            percent = round((s['correct'] / total * 100)) if total > 0 else 0

            # Kodowanie kolorami procentów
            if percent >= 80:
                color_percent = "#16A34A" # Zielony
            elif percent >= 50:
                color_percent = "#D97706" # Pomarańczowy
            else:
                color_percent = "#DC2626" # Czerwony

            # Komórki wyników w siatce tabeli
            tk.Label(
                table_frame,
                text=f"#{s['set']}",
                font=("Helvetica", 12, "bold"),
                fg="#111827",
                bg=row_bg,
                pady=8
            ).grid(row=row_idx, column=0, sticky="nsew", pady=2)
            tk.Label(
                table_frame,
                text=f"{s['correct']}",
                font=("Helvetica", 12, "bold"),
                fg="#16A34A",
                bg=row_bg
            ).grid(row=row_idx, column=1, sticky="nsew", pady=2)
            tk.Label(
                table_frame,
                text=f"{s['incorrect']}",
                font=("Helvetica", 12, "bold"),
                fg="#DC2626",
                bg=row_bg
            ).grid(row=row_idx, column=2, sticky="nsew", pady=2)
            tk.Label(
                table_frame,
                text=f"{s['time']}",
                font=("Helvetica", 12),
                fg="#4B5563",
                bg=row_bg
            ).grid(row=row_idx, column=3, sticky="nsew", pady=2)
            tk.Label(
                table_frame,
                text=f"{percent}%",
                font=("Helvetica", 12, "bold"),
                fg=color_percent,
                bg=row_bg
            ).grid(row=row_idx, column=4, sticky="nsew", pady=2)

            # Tło pod przyciskiem wideo dla spójności zebry
            bg_extra = tk.Label(table_frame, bg=row_bg)
            bg_extra.grid(row=row_idx, column=5, sticky="nsew", pady=2)

            # Przycisk odtwarzania wideo
            if s.get("video_path") and os.path.exists(s["video_path"]):
                btn_play = tk.Button(
                    table_frame,
                    text="ODTWÓRZ",
                    font=("Helvetica", 9, "bold"),
                    bg="#E5E7EB",
                    fg="#111827",
                    relief="flat",
                    bd=0,
                    padx=10,
                    pady=4,
                    cursor="hand2",
                    command=lambda p=s["video_path"]: self.play_video(p)
                )
                btn_play.grid(row=row_idx, column=5, padx=10, pady=2, sticky="e")

                # Efekt podświetlenia myszką
                btn_play.bind("<Enter>", lambda e, b=btn_play: b.config(bg="#3B82F6", fg="white"))
                btn_play.bind("<Leave>", lambda e, b=btn_play: b.config(bg="#E5E7EB", fg="#111827"))

        # Aktualizacja przycisku głównego
        if hasattr(self, 'action_btn'):
            if self.controller.current_set < self.controller.total_sets:
                self.action_btn.config(
                    text=f"PRZEJDŹ DO SERII {self.controller.current_set + 1}",
                    bg="#444444",
                    fg="white"
                )
                self.end_mode = False
            else:
                self.action_btn.config(
                    text="ZAKOŃCZ I WRÓĆ DO MENU",
                    bg="#444444",
                    fg="white"
                )
                self.end_mode = True

    # Uruchamia systemowy odtwarzacz wideo z unikaniem błędów ścieżki
    def play_video(self, path):
        import os
        abs_path = os.path.abspath(path)
        os.startfile(abs_path)

    # Nawigacja do kolejnej serii lub powrót do menu
    def next_step(self):
        if self.end_mode:
            self.controller.training_history = []
            self.controller.show_screen("SelectionScreen")
        else:
            self.controller.current_set += 1
            self.controller.show_screen("TrainingScreen")
