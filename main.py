import controller
import time
from tracker import *
from threading import Thread

BLINK_WAIT = 1

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
