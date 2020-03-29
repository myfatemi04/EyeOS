import controller
import time
from threading import Thread
import speech
import globals

import cv2
from eye_tracking import EyeTracker

# initialize the Eye Tracker
tracker = EyeTracker()
cap = cv2.VideoCapture(0)

BLINK_WAIT = 2.5

def transform_pos(pos, left, right, top, bottom, screen_left, screen_right, screen_bottom, screen_top):
    x, y = pos
    width = right - left
    screen_width = screen_right - screen_left
    height = bottom - top
    screen_height = screen_bottom - screen_top
    
    width_prop = (x - left)/width
    height_prop = (y - top)/height

    return width_prop * screen_width + screen_left, height_prop * screen_height + screen_top

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

last_left_blink = False
last_right_blink = False

def recalibrate():
    global top_left, bottom_right, msg_topleft, msg_bottomright, left, right, bottom, top, is_calibrated
    top_left = bottom_right = msg_topleft = msg_bottomright = left = right = bottom = top = None
    globals.should_calibrate = True

i = 0

if __name__ == "__main__":
    speech_thread = Thread(target=speech.speech_to_text, name="speech_to_text", daemon=True)
    speech_thread.start()
    
    print("Booting EyeOS")

    last_x, last_y = controller.pg.position()

    while not globals.should_stop:
        i += 1
        if i % 100 == 0:
            tracker.calibration.recalibrate()
        
        _, frame = cap.read()
        tracker.refresh(frame)
        frame = tracker.annotated_frame()
        # cv2.imshow("Tracker", frame)

        is_blinking = tracker.is_blinking()
        left_blink = tracker.left_blinking()
        right_blink = tracker.right_blinking()
        if is_blinking and not last_frame_blinking:
            print("Blink")
        else:
            if left_blink and not last_left_blink:
                print("Left blink")
            if right_blink and not last_right_blink:
                print("Right blink")

        pos = tracker.get_average_offset()
        
        if is_blinking is None:
            frame_blinks.append(0)
        else:
            frame_blinks.append(int(is_blinking))
        if not globals.should_calibrate:
            # if not is_blinking:
            #     if left_blink and not last_left_blink:
            #         controller.right_click()
            #     elif right_blink and not last_right_blink:
            #         controller.left_click()

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

                last_x = int_x = int(tpos[0])
                last_y = int_y = int(tpos[1])

                controller.move_mouse(int_x, int_y)
        else:
            ## Calibrate here
            if not globals.has_topleft:
                if not globals.msg_topleft:
                    print("Look at the top left and say \"done\".")
                    globals.msg_topleft = True
                if globals.said_done:# or (left_blink and not last_left_blink):
                    left, top = last_valid_pos
                    print("Saved Top Left at ", left, top)
                    globals.has_topleft = True
                    globals.said_done = False
            elif not globals.has_bottomright:
                if not globals.msg_bottomright:
                    print("Look at the bottom right and say \"done\".")
                    globals.msg_bottomright = True
                if globals.said_done:# or (left_blink and not last_left_blink):
                    right, bottom = last_valid_pos
                    globals.has_bottomright = True
                    print("Saved Bottom Right at ", right, bottom)
                    globals.should_calibrate = False
                    globals.said_done = False

        if pos:
            last_valid_pos = pos

        last_frame_blinking = is_blinking
        last_left_blink = left_blink
        last_right_blink = right_blink

        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()

