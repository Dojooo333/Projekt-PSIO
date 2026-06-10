import cv2
import datetime
import os

# Narzędzie nagrywające treningi wideo
class VideoRecorder:
    def __init__(self, base_path, exercise_name, current_set, w1, w2, target_fps=20.0):
        self.target_fps = target_fps
        self.base_path = base_path
        self.video_path = None
        self.video_writer = None
        self.saved_frames = 0
        self.w1 = w1
        self.w2 = w2

        self._init_file(exercise_name, current_set)

    # Inicjuje plik i wideo
    def _init_file(self, exercise_name, current_set):
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

        timestamp = datetime.datetime.now().strftime("%Y.%m.%d_%H.%M.%S")
        exercise_safe_name = exercise_name.replace(" ", "_")
        self.video_path = f"{self.base_path}/{exercise_safe_name}_{timestamp}_seria{current_set}.mp4"

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        comp_w = self.w1 + self.w2
        self.video_writer = cv2.VideoWriter(self.video_path, fourcc, self.target_fps, (comp_w, 560))

    # Zapisuje klatkę wyrównując do docelowego klatkażu
    def record_time_based(self, frame, cumulative_time):
        if self.video_writer is not None:
            expected_frames = int(cumulative_time * self.target_fps)
            while self.saved_frames < expected_frames:
                self.video_writer.write(frame)
                self.saved_frames += 1

    # Zamyka plik wideo po nagraniu
    def release(self):
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
