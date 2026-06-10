import cv2
import threading
import time

# Obsługa kamery w osobnym wątku
class ThreadedCamera:
    def __init__(self, src):
        self.src = src
        self.cap = None
        self.frame = None
        self.ret = False
        self.running = True
        self.lock = threading.Lock()

        # Uruchomienie pętli w tle
        self.thread = threading.Thread(target=self.grab_frames, daemon=True)
        self.thread.start()

    # Pętla pobierająca klatki z kamery
    def grab_frames(self):
        # Otwarcie kamery przez DirectShow
        self.cap = cv2.VideoCapture(self.src, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            # Awaryjne otwarcie kamery
            self.cap = cv2.VideoCapture(self.src)

        while self.running:
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    with self.lock:
                        self.ret = ret
                        self.frame = frame
                else:
                    time.sleep(0.01)
            else:
                time.sleep(0.2)

    # Zwraca najnowszą klatkę z bufora
    def read(self):
        with self.lock:
            if self.frame is not None:
                return self.ret, self.frame.copy()
            return False, None

    # Sprawdza działanie strumienia kamery
    def is_opened(self):
        return self.cap is not None and self.cap.isOpened()

    # Kończy pętlę i zwalnia zasoby systemowe
    def release(self):
        self.running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
