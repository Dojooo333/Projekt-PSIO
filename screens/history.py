import tkinter as tk
import os
import database

# Ekran przeglądania historii treningów z bazy danych
class HistoryScreen(tk.Frame):
    def __init__(self, parent, controller):
        # Tło panelu
        super().__init__(parent, bg="white")
        self.controller = controller

        # Nagłówek ekranu
        title_lbl = tk.Label(
            self,
            text="HISTORIA TRENINGÓW / PODSUMOWANIE",
            font=("Helvetica", 16, "bold"),
            fg="#111827",
            bg="white"
        )
        title_lbl.pack(pady=20)

        # Kontener na przewijaną listę
        list_container = tk.Frame(self, bg="white")
        list_container.pack(fill="both", expand=True, padx=20, pady=10)

        self.canvas = tk.Canvas(list_container, bg="white", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(list_container, orient="vertical", command=self.canvas.yview)

        # Ramka na wiersze bazy danych w płótnie
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Dopasowanie szerokości ramki
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind('<Configure>', lambda event: self.canvas.itemconfig(self.canvas_window, width=event.width))

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Przycisk powrotu do menu
        btn_back = self.controller.create_button(
            self,
            text="Powrót do MENU",
            command=lambda: controller.show_screen("SelectionScreen")
        )
        btn_back.pack(pady=25)

    # Pobiera dane z bazy SQLite i buduje siatkę wizualną
    def refresh_data(self):
        # Czyszczenie poprzednich wpisów
        for row in self.scrollable_frame.winfo_children():
            row.destroy()

        # Pobranie danych z bazy
        results = database.get_all_results()

        if not results:
            lbl_empty = tk.Label(
                self.scrollable_frame,
                text="Brak zapisanych sesji treningowych.",
                font=("Helvetica", 12),
                fg="grey",
                bg="white"
            )
            lbl_empty.pack(pady=30)
            return

        # Główna ramka tabeli
        table_frame = tk.Frame(
            self.scrollable_frame,
            bg="white"
        )
        table_frame.pack(fill="x", expand=True, padx=10)

        # Konfiguracja kolumn z danymi
        data_cols_count = 7
        for i in range(data_cols_count):
            table_frame.columnconfigure(i, weight=1, uniform="history_column")

        # Kolumna wideo się nie rozciąga pionowo
        table_frame.columnconfigure(data_cols_count, weight=0)

        # Pasek nagłówków tabeli
        columns = ["DATA", "ĆWICZENIE", "SERIA", "POPRAWNE", "BŁĘDNE", "CZAS", "SKUTECZNOŚĆ"]
        for col_idx, name in enumerate(columns):
            lbl = tk.Label(
                table_frame,
                text=name,
                font=("Helvetica", 10, "bold"),
                fg="#4B5563",
                bg="#F3F4F6",
                pady=10
            )
            lbl.grid(row=0, column=col_idx, sticky="nsew", padx=1, pady=(0, 10))

        # Puste pole nagłówka dla kolumny wideo
        tk.Label(table_frame, bg="#F3F4F6").grid(row=0, column=data_cols_count, sticky="nsew", pady=(0, 10))

        # Generowanie wierszy z historii
        for row_idx, entry in enumerate(results, start=1):
            # Elementy z rekordu
            _, date_val, exercise, set_num, correct, incorrect, time_spent, video_path = entry

            # Efekt zebry tła
            row_bg = "#F9FAFB" if row_idx % 2 == 0 else "#FFFFFF"

            total = correct + incorrect
            percent = round((correct / total * 100)) if total > 0 else 0

            # Dynamiczny dobór koloru skuteczności
            if percent >= 80:
                color_percent = "#16A34A"
            elif percent >= 50:
                color_percent = "#D97706"
            else:
                color_percent = "#DC2626"

            # Pozycjonowanie komórek
            tk.Label(
                table_frame,
                text=f"{date_val}",
                font=("Helvetica", 10),
                fg="#4B5563",
                bg=row_bg,
                pady=8
            ).grid(row=row_idx, column=0, sticky="nsew", pady=2)
            tk.Label(
                table_frame,
                text=f"{exercise.upper()}",
                font=("Helvetica", 10, "bold"),
                fg="#111827",
                bg=row_bg
            ).grid(row=row_idx, column=1, sticky="nsew", pady=2)
            tk.Label(
                table_frame,
                text=f"#{set_num}",
                font=("Helvetica", 12, "bold"),
                fg="#111827",
                bg=row_bg
            ).grid(row=row_idx, column=2, sticky="nsew", pady=2)
            tk.Label(
                table_frame,
                text=f"{correct}",
                font=("Helvetica", 12, "bold"),
                fg="#16A34A",
                bg=row_bg
            ).grid(row=row_idx, column=3, sticky="nsew", pady=2)
            tk.Label(
                table_frame,
                text=f"{incorrect}",
                font=("Helvetica", 12, "bold"),
                fg="#DC2626",
                bg=row_bg
            ).grid(row=row_idx, column=4, sticky="nsew", pady=2)
            tk.Label(
                table_frame,
                text=f"{time_spent}",
                font=("Helvetica", 12),
                fg="#4B5563",
                bg=row_bg
            ).grid(row=row_idx, column=5, sticky="nsew", pady=2)
            tk.Label(
                table_frame,
                text=f"{percent}%",
                font=("Helvetica", 12, "bold"),
                fg=color_percent,
                bg=row_bg
            ).grid(row=row_idx, column=6, sticky="nsew", pady=2)

            # Tło pod przyciskiem wideo
            bg_extra = tk.Label(table_frame, bg=row_bg)
            bg_extra.grid(row=row_idx, column=data_cols_count, sticky="nsew", pady=2)

            # Warunkowe tworzenie przycisku wideo
            if video_path and os.path.exists(video_path):
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
                    command=lambda p=video_path: self.play_video(p)
                )
                btn_play.grid(row=row_idx, column=data_cols_count, padx=10, pady=2, sticky="e")

                # Efekt najechania kursorem
                btn_play.bind("<Enter>", lambda e, b=btn_play: b.config(bg="#3B82F6", fg="white"))
                btn_play.bind("<Leave>", lambda e, b=btn_play: b.config(bg="#E5E7EB", fg="#111827"))

    # Uruchamia systemowy odtwarzacz wideo
    def play_video(self, path):
        # Otwarcie pliku na Windowsie
        abs_path = os.path.abspath(path)
        os.startfile(abs_path)
