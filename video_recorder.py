import numpy as np
import threading
import time

try:
    import cv2
    import mss
except ImportError as e:
    print(f"Error importing required libraries: {e}")
    print("Please install the required libraries using:")
    print("pip install opencv-python mss")
    exit(1)

class VideoRecorder:
    def __init__(self, output_filename, fps=30):
        self.output_filename = output_filename
        self.fps = fps
        self.recording = False
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[0]  # Capture the primary monitor

    def start_recording(self):
        self.recording = True
        self.record_thread = threading.Thread(target=self._record)
        self.record_thread.start()

    def stop_recording(self):
        self.recording = False
        self.record_thread.join()

    def _record(self):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.output_filename, fourcc, self.fps, (self.monitor["width"], self.monitor["height"]))

        last_time = time.time()
        while self.recording:
            current_time = time.time()
            if (current_time - last_time) >= 1.0/self.fps:
                img = np.array(self.sct.grab(self.monitor))
                frame = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
                out.write(frame)
                last_time = current_time

        out.release()