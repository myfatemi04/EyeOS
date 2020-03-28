import controller
import time
from threading import Thread

import cv2
from eye_tracking import EyeTracker

# initialize the Eye Tracker
tracker = EyeTracker()
cap = cv2.VideoCapture(0)

BLINK_WAIT = 1.5

def transform_pos(pos, left, right, top, bottom, screen_left, screen_right, screen_bottom, screen_top):
    x, y = pos
    width = right - left
    screen_width = screen_right - screen_left
    height = bottom - top
    screen_height = screen_bottom - screen_top
    
    width_prop = (x - left)/width
    height_prop = (y - top)/height

    return width_prop * screen_width + screen_left, height_prop * screen_height + screen_top

def main_thread():
    last_blink_time = 0
    last_frame_blinking = False
    is_calibrated = False
    top_left = None
    bottom_right = None
    msg_topleft = False
    msg_bottomright = False

    left = None
    right = None
    bottom = None
    top = None

    screen_left = 0
    screen_top = 0
    screen_right, screen_bottom = controller.pg.size()

    last_valid_pos = None

    blink_min_len = 1
    frame_blinks = [0 for x in range(blink_min_len)]
    while True:
        _, frame = cap.read()
        tracker.refresh(frame)
        frame = tracker.annotated_frame()
        cv2.imshow("Tracker", frame)

        is_blinking = tracker.is_blinking()
        pos = tracker.get_average_offset()

        # print("LEFT OPENNESS: ", tracker.left_openness(), "BLINKING: ", is_blinking)
        if is_blinking:
            print("BLINK")

        if is_blinking is None:
            frame_blinks.append(0)
        else:
            frame_blinks.append(int(is_blinking))

        if is_calibrated:
            if is_blinking:
                blink_time = time.perf_counter()
                if blink_time - last_blink_time < BLINK_WAIT:
                    controller.left_click()

                last_blink_time = blink_time
                
            if pos:
                tpos = transform_pos(
                    pos,
                    left,
                    right,
                    top,
                    bottom,
                    screen_left,
                    screen_right,
                    screen_bottom,
                    screen_top
                )
                print(f"{tpos[0]:.2f} {tpos[1]:.2f}", f"{pos[0] * 100:.2f} {pos[1] * 100:.2f}")
                int_x = int(tpos[0])
                int_y = int(tpos[1])
                controller.move_mouse(int_x, int_y)
        else:
            ## Calibrate here
            if not top_left:
                if not msg_topleft:
                    print("Look at the top left and blink")
                    msg_topleft = True
                if last_valid_pos and is_blinking and not last_frame_blinking:
                    top_left = last_valid_pos
                    print("Saved pos at ", top_left)
                    left, top = top_left
            elif not bottom_right:
                if not msg_bottomright:
                    print("Look at the bottom right and blink")
                    msg_bottomright = True
                if last_valid_pos and is_blinking and not last_frame_blinking:
                    bottom_right = last_valid_pos
                    print("Saved pos at ", bottom_right)
                    right, bottom = bottom_right
            else:
                is_calibrated = True

        if pos:            
            last_valid_pos = pos

        last_frame_blinking = is_blinking
            
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()

eyeos_thread = Thread(target=main_thread, name="EyeOS")
eyeos_thread.start()