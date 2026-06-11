import threading
import time
import speech_recognition as sr

# Wątek odtwarzania mowy oparty na kolejce
class AudioEngine:

    def __init__(self):
        import queue
        self.queue = queue.Queue()
        # Uruchomienie wątku odtwarzacza w tle
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    # Dodaje tekst do kolejki syntezatora usuwając stare komunikaty
    def speak(self, text):
        import queue
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except queue.Empty:
                break
        self.queue.put(text)

    # Pętla odtwarzająca wiadomości z kolejki
    def _loop(self):
        import subprocess
        while True:
            # Oczekiwanie na tekst w kolejce
            text = self.queue.get()
            if text is None:
                break
            try:
                ps_script = '''
                Add-Type -AssemblyName System.Speech
                $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
                $synth.Rate = 2
                $synth.Speak($env:TTS_TEXT)
                '''
                
                import os
                env = os.environ.copy()
                env['TTS_TEXT'] = text
                
                subprocess.run(
                    ['powershell', '-Command', ps_script],
                    env=env,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            except Exception as e:
                print(f"[AUDIO] Błąd lektora: {e}")


# Wątek tłumaczący mowę na komendy interfejsu
class VoiceListener:

    def __init__(self, controller):
        self.controller = controller
        self.recognizer = sr.Recognizer()
        self.running = True

        # Uruchomienie wątku nasłuchującego
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    # Pętla nasłuchująca polecenia z mikrofonu
    def _loop(self):
        import speech_recognition as sr
        with sr.Microphone() as source:
            print("[VOICE] Kalibracja tła... Proszę o ciszę.")
            self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
            print("[VOICE] Gotowy do nasłuchiwania komend!")

            while self.running:
                # Tylko nasłuchujemy, jeśli jesteśmy w treningu
                if not hasattr(self.controller, 'is_training_active') or not self.controller.is_training_active:
                    time.sleep(0.5)
                    continue
                try:
                    # Nasłuchiwanie mowy
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=4)

                    # Asynchroniczne wysłanie audio do rozpoznania
                    threading.Thread(target=self._recognize_audio, args=(audio,), daemon=True).start()

                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    print(f"[VOICE ERROR] Nieoczekiwany błąd nasłuchu: {e}")

    def stop(self):
        self.running = False

    # Pobiera transkrypcję audio
    def _recognize_audio(self, audio):
        import speech_recognition as sr
        try:
            # Rozpoznawanie mowy
            text = self.recognizer.recognize_google(audio, language="pl-PL").lower()
            print(f"[VOICE] Rozpoznano: {text}")
            self._process_command(text)
        except sr.UnknownValueError:
            pass
        except Exception as e:
            pass

    # Interpretuje komendy głosowe i modyfikuje interfejs
    def _process_command(self, text):
        # Blokada poza ekranem treningu
        if not hasattr(self.controller, 'is_training_active') or not self.controller.is_training_active:
            return

        screen = self.controller.screens["TrainingScreen"]

        # Wznowienie lub start
        if any(k in text for k in ["start", "rozpocznij", "ruszamy", "wznów", "leć"]):
            self.controller.after(0, screen.voice_command_start)

        # Przerwanie ćwiczeń
        elif any(k in text for k in ["pauza", "stop", "zatrzymaj", "przerwij"]):
            self.controller.after(0, screen.voice_command_pause)

        # Zakończenie i wyjście do menu
        elif any(k in text for k in ["zakończ", "koniec", "wyjdź", "menu"]):
            self.controller.after(0, screen.voice_command_menu)
