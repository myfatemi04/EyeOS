import controller
import time
from threading import Thread

import cv2
from eye_tracking import EyeTracker

# initialize the Eye Tracker
tracker = EyeTracker()
cap = cv2.VideoCapture(0)

def main_thread():
    while True:
        _, frame = cap.read()
        tracker.refresh(frame)
        frame = tracker.annotated_frame()
        text = ""

        if tracker.is_blinking(): text = "Blinking"
        elif tracker.is_right(): text = "Looking right"
        elif tracker.is_left(): text = "Looking left"
        elif tracker.is_center(): text = "Looking center"

        left = tracker.pupil_left_coords()
        right = tracker.pupil_right_coords()

        if cv2.waitKey(1) & 0xFF == ord('q'): break

eyeos_thread = Thread(target=main_thread, name="EyeOS")
eyeos_thread.start()