print("[INFO] Ładowanie bibliotek...")
from ultralytics import YOLO
import config
from camera import ThreadedCamera
from ui import CyberTrenerApp
import database
print("[INFO] Biblioteki pomyślnie zostały załadowane.")

if __name__ == "__main__":
    print("[INFO] Inicjalizacja bazy danych...")
    database.init_db()

    print("[INFO] Model rozpoznawania obrazów uruchomiony na: " + config.DEVICE.upper())
    model = YOLO(config.MODEL_PATH)
    model.to(config.DEVICE)

    print("[INFO] Inicjalizacja wątków dla Kamery 1 oraz Kamery 2...")
    camera1 = ThreadedCamera(config.CAMERA_1_INDEX)
    camera2 = ThreadedCamera(config.CAMERA_2_INDEX)

    print("[INFO] Uruchamianie interfejsu graficznego...")
    # Przekazanie zainicjalizowanych obiektów do aplikacji Tkinter
    app = CyberTrenerApp(model=model, camera1=camera1, camera2=camera2)

    # Zwalnia wątki i zamyka aplikację
    def on_closing():
        print("[INFO] Zwalnianie wątków kamer i AI...")
        app.yolo_thread.stop()
        app.voice_listener.stop()
        camera1.release()
        camera2.release()
        app.destroy()
        print("[INFO] Program został zamknięty pomyślnie.")

    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()
