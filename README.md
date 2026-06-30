# Trener Personalny AI (PSIO)

Wirtualny asystent treningowy wykorzystujący wizję komputerową (YOLO Pose) do analizy postawy i techniki ćwiczeń w czasie rzeczywistym. Aplikacja zlicza poprawne powtórzenia, weryfikuje ułożenie ciała z użyciem dwóch kamer (front i profil), generuje komunikaty głosowe o błędach technicznych oraz zapisuje historię treningów.

## ⚙️ Przygotowanie programu (Instalacja)

1. **Wymagania:**
   - Środowisko Python (zalecana wersja 3.9 - 3.11).
   - Dwie kamery internetowe (jedna ustawiona frontem do użytkownika, druga z boku - z profilu).

2. **Instalacja bibliotek:**
   Otwórz terminal w głównym folderze projektu. 
   
   **Wersja podstawowa (CPU):**
   ```bash
   pip install ultralytics opencv-python Pillow SpeechRecognition PyAudio numpy customtkinter torch torchvision torchaudio
   ```
   **Wersja wspierająca akcelerację karty graficznej (NVIDIA CUDA):**
   *(Zalecane dla płynnego działania YOLO w czasie rzeczywistym)*
   ```bash
   pip install ultralytics opencv-python Pillow SpeechRecognition PyAudio numpy customtkinter
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

3. **Wyjaśnienie użytych bibliotek (pełna lista importów z plików `.py`):**
   Poniżej znajduje się absolutnie pełna lista modułów, które występują w kodzie (np. `import os`, `from tkinter import...`):
   
   *Wymagające instalacji przez pip (zewnętrzne):*
   `ultralytics`, `cv2` (opencv-python), `PIL` (Pillow), `speech_recognition`, `pyaudio`, `numpy`, `customtkinter`, `torch`, `torchvision`, `torchaudio`.

   *Wbudowane w instalację Pythona (nie wymagają pip'a!):*
   `tkinter` (interfejs), `sqlite3` (baza danych), `os`, `sys`, `time`, `datetime`, `threading`, `subprocess`, `math`, `platform`, `queue`, `enum`.

4. **Model AI:**
   Gotowy, wytrenowany model sieci (np. `yolo26n-pose.pt`) znajduje się już w plikach projektu na GitHubie, więc nie musisz niczego dodatkowo pobierać. Po zainstalowaniu bibliotek aplikacja jest gotowa do startu.

## 🚀 Uruchomienie

Aby uruchomić główny interfejs graficzny aplikacji, wpisz w terminalu:
```bash
python main.py
```
*(Z poziomu interfejsu możesz następnie wybrać odpowiednie kamery, przypisać do nich rolę front/profil oraz rozpocząć trening).*

---
