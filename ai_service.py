import threading
import time
import config
from vision_utils import scale_image_to_height, draw_skeleton

# Wątek asynchronicznie przetwarzający klatki modelem YOLO
class YoloThread:
    def __init__(self, model, camera1, camera2):
        self.model = model
        self.camera1 = camera1
        self.camera2 = camera2
        self.running = True
        self.lock = threading.Lock()

        # Ostatnio przetworzone klatki ze szkieletem
        self.new_results = None
        self.last_id = 0

        # Uruchomienie wątku obliczeniowego w tle
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    # Pętla wątku przetwarzająca klatki i nakładająca szkielet
    def _loop(self):
        frame_id = 0
        while self.running:
            # Pobieranie najnowszych klatek z kamer
            ret1, frame1 = self.camera1.read()
            ret2, frame2 = self.camera2.read()

            # Oczekiwanie na klatki z obu kamer
            if frame1 is None or frame2 is None:
                time.sleep(0.01)
                continue

            # Skalowanie obrazu
            k1 = scale_image_to_height(frame1, camera_idx=1, target_h=480)
            k2 = scale_image_to_height(frame2, camera_idx=2, target_h=480)

            # Przetwarzanie klatek przez model YOLO
            results = self.model.predict([k1, k2], verbose=False, device=config.DEVICE, imgsz=640)

            # Nanoszenie szkieletów na klatki
            frame_front = draw_skeleton(k1, results[0])
            frame_side = draw_skeleton(k2, results[1])

            frame_id += 1

            # Zapisanie wyników dla głównego wątku (GUI)
            with self.lock:
                self.new_results = (frame_id, frame_front, frame_side, results)

    # Pobiera najnowszą paczkę wyników przez GUI
    def get_data(self):
        with self.lock:
            if self.new_results and self.new_results[0] > self.last_id:
                self.last_id = self.new_results[0]
                return self.new_results
            return None
