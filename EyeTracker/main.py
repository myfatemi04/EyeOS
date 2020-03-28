import controller
import time
from tracker import *
from threading import Thread

BLINK_WAIT = 1

def calibrate():
    print("Look at the upper-left corner")
    upper_left = get_pos()
    print("Look at the upper-right corner")
    upper_right = get_pos()
    print("Look at the bottom-right corner")
    bottom_right = get_pos()
    print("Look at the bottom-left corner")
    bottom_left = get_pos()
    return (upper_left, upper_right, bottom_right, bottom_left)

def run_tracker():
    last_blink_time = 0
    while True:
        untransformed = get_pos()
        transformed = get_transformed_pos(untransformed, None)
        controller.move_mouse(*transformed)
        
        blink = is_blinking()
        if blink:
            blink_time = time.perf_counter()
            if blink_time - last_blink_time < BLINK_WAIT:
                controller.left_click()
        
eyeos_thread = Thread(target=run_tracker, name="EyeOS")
eyeos_thread.start()
