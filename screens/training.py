import tkinter as tk
import time
import cv2
import numpy as np
from PIL import Image, ImageTk
import os
import datetime
import config
import database
from exercises import ExerciseState, JumpingJacksState, analyze_jumping_jacks, LungesState, analyze_lunges, SkipAState, analyze_skip_a
from video_utils import VideoRecorder

EXERCISE_ANALYZERS = {
    "jumping_jacks": analyze_jumping_jacks,
    "lunges": analyze_lunges,
    "high_knees": analyze_skip_a,
}

# Główny ekran treningu (obraz z kamer, liczniki, AI)
class TrainingScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        self.is_running = False
        self.is_paused = False
        self.is_counting_down = False
        self.video_writer = None
        self.video_path = None
        self.last_audio_msg = ""
        self.last_audio_msg_time = 0

        # Zmienne do synchronizacji czasu wideo
        self.target_fps = 20.0
        self.saved_frames = 0
        self.accumulated_time = 0.0
        self.last_frame_time = 0.0

        self.info_lbl = tk.Label(self, text="", font=("Helvetica", 20, "bold"), fg="#333333", bg="white")
        self.info_lbl.pack(pady=(20, 5))

        self.counter_lbl = tk.Label(self, text="POPRAWNE: 0 / 0", font=("Helvetica", 24, "bold"), fg="#00aa44", bg="white")
        self.counter_lbl.pack(pady=5)

        self.live_stats_lbl = tk.Label(self, text="CZAS: 00:00  |  TEMPO: -- powt./min", font=("Helvetica", 16, "bold"), fg="#555555", bg="white")
        self.live_stats_lbl.pack(pady=5)

        self.msg_lbl = tk.Label(self, text="Inicjalizacja...", font=("Helvetica", 16, "bold"), fg="#ff9900", bg="white")
        self.msg_lbl.pack(pady=(5, 15))

        self.cameras_frame = tk.Frame(self, bg="white")
        self.cameras_frame.pack(pady=10, fill="both", expand=True)

        self.front_container = tk.Frame(self.cameras_frame, bg="white")
        self.front_container.pack(side="left", expand=True, padx=20)

        tk.Label(self.front_container, text="PRZÓD", font=("Helvetica", 16, "bold"), fg="#333333", bg="white").pack(pady=(0, 10))
        self.video_front = tk.Label(self.front_container, bg="#f0f0f0", bd=0)
        self.video_front.pack()

        self.side_container = tk.Frame(self.cameras_frame, bg="white")
        self.side_container.pack(side="left", expand=True, padx=20)

        tk.Label(self.side_container, text="BOK", font=("Helvetica", 16, "bold"), fg="#333333", bg="white").pack(pady=(0, 10))
        self.video_side = tk.Label(self.side_container, bg="#f0f0f0", bd=0)
        self.video_side.pack()

        self.buttons_frame = tk.Frame(self, bg="white")
        self.buttons_frame.pack(pady=30)

        self.btn_pause = self.controller.create_button(self.buttons_frame, "START", self.toggle_pause, width=18, font=("Helvetica", 14, "bold"), pady=10)
        self.btn_pause.grid(row=0, column=0, padx=10)

        self.btn_stop = self.controller.create_button(self.buttons_frame, "PRZERWIJ SERIĘ", self.stop_training, width=18, font=("Helvetica", 14, "bold"), pady=10)
        self.btn_stop.grid(row=0, column=1, padx=10)

        self.btn_menu = self.controller.create_button(self.buttons_frame, "WYJŚCIE DO MENU", self.go_to_menu, width=18, font=("Helvetica", 14, "bold"), pady=10)
        self.btn_menu.grid(row=0, column=2, padx=10)

    # Ustawia interfejs przed startem serii
    def refresh_data(self):
        self.target_exercise = self.controller.exercise_mapping[self.controller.selected_exercise]
        if self.target_exercise == "jumping_jacks":
            self.exercise_state = JumpingJacksState()
        elif self.target_exercise == "lunges":
            self.exercise_state = LungesState()
        elif self.target_exercise == "high_knees":
            self.exercise_state = SkipAState()
        else:
            self.exercise_state = ExerciseState(self.target_exercise)

        self.w1 = 853 if config.CAMERA_1_MODE == "16:9" else 270
        self.w2 = 853 if config.CAMERA_2_MODE == "16:9" else 270
        self.video_writer = None
        self.video_path = None

        self.correct_reps = 0
        self.incorrect_reps = 0
        self.is_running = True
        self.is_paused = True
        self.is_counting_down = False

        self.btn_pause.config(text="START", state="normal")
        self.msg_lbl.config(text="USTAW SIĘ PRZED KAMERĄ I KLIKNIJ START", fg="#ff9900")

        self.info_lbl.config(text=f"SERIA {self.controller.current_set} z {self.controller.total_sets} ({self.controller.selected_exercise.upper()})")
        self.counter_lbl.config(text=f"POPRAWNE: 0 / {self.controller.total_reps}")
        self.live_stats_lbl.config(text="CZAS: 00:00  |  TEMPO: -- powt./min")

        self.update_frame_loop()

    # Przełącza pauzę i startuje odliczanie
    def toggle_pause(self):
        if self.is_counting_down:
            return

        if self.is_paused:
            self.start_countdown(3)
        else:
            self.is_paused = True
            self.btn_pause.config(text="WZNÓW")
            self.msg_lbl.config(text="TRENING WSTRZYMANY", fg="#ff9900")

    # Rekurencyjne odliczanie przed startem serii
    def start_countdown(self, seconds):
        if not self.is_running:
            return

        self.is_counting_down = True
        self.btn_pause.config(text="ODLICZANIE...", state="disabled")

        if seconds > 0:
            self.msg_lbl.config(text=f"START ZA: {seconds}...", fg="#ff5500")
            self.after(1000, lambda: self.start_countdown(seconds - 1))
        else:
            self.msg_lbl.config(text="START!", fg="#00aa44")
            self.is_paused = False
            self.is_counting_down = False
            self.start_time = time.time()
            self.btn_pause.config(text="PAUZA", state="normal")

            self.last_frame_time = time.time()
            self.accumulated_time = 0.0

            self.video_writer = VideoRecorder(
                base_path="nagrania_treningow",
                exercise_name=self.controller.selected_exercise,
                current_set=self.controller.current_set,
                w1=self.w1,
                w2=self.w2,
                target_fps=self.target_fps
            )
            self.video_path = self.video_writer.video_path

    # Wraca do menu głównego
    def go_to_menu(self):
        self.is_running = False
        self.is_paused = False
        self.is_counting_down = False
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
        self.controller.training_history = []
        self.controller.show_screen("SelectionScreen")

    # Usuwa polskie znaki z tekstu
    def _remove_diacritics(self, text):
        mapping = {'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
                   'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N', 'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'}
        return "".join(mapping.get(c, c) for c in text)

    # Główna pętla renderująca interfejs i oceniająca ruch
    def update_frame_loop(self):
        if not self.is_running:
            return

        # Pobieranie danych z wątku AI
        yolo_data = self.controller.yolo_thread.get_data()

        if yolo_data is None:
            # Ponowienie po 15ms.
            self.after(15, self.update_frame_loop)
            return

        # Rozpakowanie danych i klatek
        frame_id, frame_front, frame_side, results = yolo_data

        # Obliczanie czasu nagrania
        now = time.time()
        if self.last_frame_time == 0.0:
            self.last_frame_time = now
        delta_time = now - self.last_frame_time
        self.last_frame_time = now

        if not self.is_paused and not self.is_counting_down:
            self.accumulated_time += delta_time

            if self.target_exercise in EXERCISE_ANALYZERS:
                if (results[0].keypoints is not None and len(results[0].keypoints.xy) > 0) and \
                        (results[1].keypoints is not None and len(results[1].keypoints.xy) > 0):

                    kp_f = results[0].keypoints.xy[0].cpu().numpy()
                    conf_f = results[0].keypoints.conf[0].cpu().numpy()
                    kp_s = results[1].keypoints.xy[0].cpu().numpy()
                    conf_s = results[1].keypoints.conf[0].cpu().numpy()

                    # Aktualizacja stanu ćwiczenia
                    analyze_fn = EXERCISE_ANALYZERS[self.target_exercise]
                    self.exercise_state, rep_completed, rep_correct, _, message = \
                        analyze_fn(kp_f, conf_f, kp_s, conf_s, self.exercise_state)

                    # Wywołanie komunikatów głosowych.
                    if message != "":
                        is_error = message.startswith("BŁĄD:")

                        if is_error:
                            text_color = "#ff3333"
                            
                            is_new_error = (message != self.last_audio_msg)
                            time_passed = (time.time() - self.last_audio_msg_time > 5.0)

                            if rep_completed or is_new_error or time_passed:
                                audio_msg = message.replace("BŁĄD: ", "")
                                self.controller.audio.speak(audio_msg)
                                self.last_audio_msg = message
                                self.last_audio_msg_time = time.time()
                        else:
                            text_color = "#00ff66"

                        self.msg_lbl.config(text=message, fg=text_color)
                    else:
                        if self.msg_lbl.cget("text") == "BŁĄD: Sylwetka niewidoczna w obu kamerach":
                            self.msg_lbl.config(text="ĆWICZ...", fg="#00ff66")

                    if rep_completed:
                        if rep_correct:
                            self.correct_reps += 1
                        else:
                            self.incorrect_reps += 1

                        self.counter_lbl.config(
                            text=f"POPRAWNE: {self.correct_reps} / {self.controller.total_reps} (Błędne: {self.incorrect_reps})")

                else:
                    self.msg_lbl.config(text="BŁĄD: Sylwetka niewidoczna w obu kamerach", fg="#ff3333")
            else:
                self.msg_lbl.config(text=f"Logika dla {self.controller.selected_exercise} w budowie...", fg="#555555")

        # Statystyki bieżące
        minutes = int(self.accumulated_time) // 60
        seconds = int(self.accumulated_time) % 60
        time_str = f"{minutes:02d}:{seconds:02d}"

        total_reps = self.correct_reps + self.incorrect_reps
        if self.accumulated_time > 3.0:
            tempo_rpm = (total_reps / self.accumulated_time) * 60.0
            tempo_str = f"{tempo_rpm:.1f} powt./min"
        else:
            tempo_str = "-- powt./min"

        if not self.is_paused and not self.is_counting_down:
            self.live_stats_lbl.config(text=f"CZAS: {time_str}  |  TEMPO: {tempo_str}")

        # Generowanie klatki do pliku wideo
        combined_images = np.hstack([frame_front, frame_side])
        hud_h = 80
        comp_h = 480 + hud_h
        comp_w = self.w1 + self.w2

        composite_frame = np.zeros((comp_h, comp_w, 3), dtype=np.uint8)
        composite_frame[0:480, 0:comp_w] = combined_images

        text_line1 = f"Seria {self.controller.current_set} | Poprawne: {self.correct_reps}/{self.controller.total_reps} | Bledne: {self.incorrect_reps}"
        text_line2 = f"Czas serii: {time_str} | Tempo: {tempo_str}"
        msg_clean = self._remove_diacritics(self.msg_lbl.cget("text"))

        cv2.putText(composite_frame, text_line1, (15, 505), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(composite_frame, text_line2, (15, 525), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(composite_frame, f"Status: {msg_clean}", (15, 545), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)

        # Zapisz zsynchronizowaną klatkę wideo
        if self.is_running and not self.is_paused and not self.is_counting_down:
            if self.video_writer is not None:
                self.video_writer.record_time_based(composite_frame, self.accumulated_time)

        # Aktualizacja wizualna Tkinter
        rgb_f = cv2.cvtColor(frame_front, cv2.COLOR_BGR2RGB)
        img_f = Image.fromarray(rgb_f)
        img_tk_f = ImageTk.PhotoImage(image=img_f)
        self.video_front.img_tk = img_tk_f
        self.video_front.config(image=img_tk_f)

        rgb_s = cv2.cvtColor(frame_side, cv2.COLOR_BGR2RGB)
        img_s = Image.fromarray(rgb_s)
        img_tk_s = ImageTk.PhotoImage(image=img_s)
        self.video_side.img_tk = img_tk_s
        self.video_side.config(image=img_tk_s)

        if self.correct_reps >= self.controller.total_reps:
            self.stop_training()
            return

        self.after(15, self.update_frame_loop)

    # Wznów po komendzie głosowej
    def voice_command_start(self):
        if self.is_paused and not self.is_counting_down:
            self.toggle_pause()

    # Zatrzymaj po komendzie głosowej
    def voice_command_pause(self):
        if not self.is_paused and not self.is_counting_down:
            self.toggle_pause()

    # Wyjdź do menu po komendzie głosowej
    def voice_command_menu(self):
        self.go_to_menu()

    # Zakończenie serii ćwiczeń
    def stop_training(self):
        self.is_running = False
        self.is_paused = False
        self.is_counting_down = False
        duration = round(self.accumulated_time, 1)

        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None

        set_summary = {
            "set": self.controller.current_set,
            "correct": self.correct_reps,
            "incorrect": self.incorrect_reps,
            "time": f"{duration}s",
            "video_path": self.video_path
        }
        self.controller.training_history.append(set_summary)

        # Zapis do bazy danych
        database.save_set_result(
            exercise=self.controller.selected_exercise,
            set_number=self.controller.current_set,
            correct=self.correct_reps,
            incorrect=self.incorrect_reps,
            time_spent=f"{duration}s",
            video_path=self.video_path
        )

        self.controller.show_screen("SummaryScreen")
