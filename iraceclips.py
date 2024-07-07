import irsdk
import time
from video_recorder import VideoRecorder

class RaceMonitor:
    def __init__(self):
        self.ir = irsdk.IRSDK()
        self.last_car_positions = {}
        self.events = []
        self.last_fastest_lap = None
        self.video_recorder = VideoRecorder("race_recording.mp4")

    def connect(self):
        if self.ir.startup():
            print("Connected to iRacing")
            self.video_recorder.start_recording()
            return True
        return False

    def disconnect(self):
        self.ir.shutdown()
        self.video_recorder.stop_recording()
        print("Disconnected from iRacing")

    def monitor_race(self):
        while True:
            if self.ir.is_connected:
                self.ir.freeze_var_buffer_latest()
                
                self.check_overtakes()
                self.check_incidents()
                self.check_close_battles()
                self.check_fastest_lap()
                
                time.sleep(0.1)  # Poll every 100ms
            else:
                print("iRacing is not running")
                time.sleep(1)

    def check_overtakes(self):
        positions = {car.CarIdx: car.CarIdxPosition for car in self.ir['CarIdxPosition']}
        
        for idx, pos in positions.items():
            if idx in self.last_car_positions:
                if pos < self.last_car_positions[idx]:
                    overtaken_idx = next((i for i, p in self.last_car_positions.items() if p == pos), None)
                    if overtaken_idx is not None:
                        self.log_event("Overtake", f"Car {idx} overtook Car {overtaken_idx}")
        
        self.last_car_positions = positions

    def check_incidents(self):
        for car_idx, car_info in enumerate(self.ir['CarIdxTrackSurface']):
            if car_info == 0:  # 0 indicates the car is off-track
                self.log_event("Incident", f"Car {car_idx} went off-track")

    def check_close_battles(self):
        positions = self.ir['CarIdxLapDistPct']
        for i in range(len(positions) - 1):
            if abs(positions[i] - positions[i+1]) < 0.01:  # Within 1% of track distance
                self.log_event("Close Battle", f"Close battle between Car {i} and Car {i+1}")

    def check_fastest_lap(self):
        fastest_lap = self.ir['SessionBestLapTime']
        if fastest_lap != self.last_fastest_lap:
            self.log_event("Fastest Lap", f"New fastest lap: {fastest_lap:.3f}")
            self.last_fastest_lap = fastest_lap

    def log_event(self, event_type, description):
        timestamp = self.ir['SessionTime']
        self.events.append((timestamp, event_type, description))
        print(f"Event logged: {event_type} at {timestamp:.2f}s - {description}")

if __name__ == "__main__":
    monitor = RaceMonitor()
    if monitor.connect():
        try:
            monitor.monitor_race()
        finally:
            monitor.disconnect()