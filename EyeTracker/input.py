import controller
import time
from threading import Thread

import cv2
from eye_tracking import EyeTracker

# initialize the Eye Tracker
tracker = EyeTracker()
cap = cv2.VideoCapture(0)

BLINK_WAIT = 1

def transform_pos(pos):
    return pos

def main_thread():
    last_blink_time = 0
    last_frame_blinking = False
    is_calibrated = False
    top_left = None
    bottom_right = None
    last_valid_pos = None
    while True:
        _, frame = cap.read()
        tracker.refresh(frame)
        frame = tracker.annotated_frame()
        cv2.imshow("Tracker", frame)

        is_blinking = tracker.is_blinking()
        pos = tracker.get_average_offset()

        if is_calibrated:
            if is_blinking:
                blink_time = time.perf_counter()
                if not last_frame_blinking and blink_time - last_blink_time < BLINK_WAIT:
                    controller.left_click()
                last_blink_time = blink_time
            
            last_frame_blinking = is_blinking
            
            if pos:
                print(transform_pos(pos))
        else:
            ## Calibrate here
            if not top_left:
                print("Look at the top left and blink")
                if is_blinking:
                    top_left = last_valid_pos
                    print("Saved pos at ", top_left)
            elif not bottom_right:
                print("Look at the bottom right and blink")
                if is_blinking:
                    bottom_right = last_valid_pos
                    print("Saved pos at ", bottom_right)
            else:
                is_calibrated = True

        if pos:            
            last_valid_pos = pos

        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()

eyeos_thread = Thread(target=main_thread, name="EyeOS")
eyeos_thread.start()