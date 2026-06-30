# CyberTrener (Projekt PSIO)

Wirtualny asystent treningowy wykorzystujący wizję komputerową (YOLO Pose) do analizy postawy i techniki ćwiczeń w czasie rzeczywistym. Aplikacja zlicza poprawne powtórzenia, weryfikuje ułożenie ciała z użyciem dwóch kamer (przód oraz bok), generuje komunikaty głosowe o błędach technicznych oraz zapisuje historię treningów.

## Przygotowanie programu (Instalacja)

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

3. **Model YOLO:**
   Gotowy, wytrenowany model sieci (np. `yolo26m-pose.pt`) znajduje się już w plikach. Po zainstalowaniu bibliotek aplikacja jest gotowa do startu.

4. **Edycja pliku config.py**
   W tym pliku znajdują się najważniejsze parametry do sterowania programem.

   - CAMERA_1_INDEX i CAMERA_2_INDEX - określają indeksy kamer widoczynych w systemie, np. 1, 2, 3, itd

   - CAMERA_1_MODE i CAMERA_2_MODE - określają one, czy kamera jest umieszczona poziomo (16:9) lub pionowo (9:16)

   - CAMERA_1_ROTATION i CAMERA_2_ROTATION - określają, czy program powinien obrócić kamerę o 90 stopni w prawo (True), lub nie (False)

   - MODEL_PATH - nazwa pliku modelu YOLO - w przypadku pracy na CPU, można zmienić na mniejszy model taki jak np. yolo26n-post.pt (czyli model nano)

## Uruchomienie

Aby uruchomić główny interfejs graficzny aplikacji, wpisz w terminalu:
```bash
python main.py
```
