import pyautogui as pg
import time
from threading import Thread
import speech
import globals
from playsound import playsound

import cv2
from eye_tracking import EyeTracker, NoseTracker

# initialize the Eye Tracker
eye_tracker = EyeTracker()
nose_tracker = NoseTracker()
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
screen_right, screen_bottom = pg.size()

last_valid_pos = None

blink_min_len = 1
frame_blinks = [0 for x in range(blink_min_len)]

last_left_blink = False
last_right_blink = False

center_x = None
center_y = None

def recalibrate():
    global top_left, bottom_right, msg_topleft, msg_bottomright, left, right, bottom, top, is_calibrated
    global center_x, center_y
    top_left = bottom_right = msg_topleft = msg_bottomright = left = right = bottom = top = None
    center_x = center_y = None
    globals.should_calibrate = True

i = 0

if __name__ == "__main__":
    speech_thread = Thread(target=speech.speech_to_text, name="speech_to_text", daemon=True)
    speech_thread.start()
    
    print("Booting EyeOS")

    last_x, last_y = pg.position()

    while not globals.should_stop:
        i += 1
        if i % 100 == 0 and globals.mode == 'eye':
            eye_tracker.calibration.recalibrate()
        
        _, frame = cap.read()
        if globals.mode == 'eye':  ### EYE TRACKING ###
            eye_tracker.refresh(frame)
            frame = eye_tracker.annotated_frame()
            cv2.imshow("Eye tracker", frame)

            pos = eye_tracker.get_average_offset()
            
            is_blinking = False

            if is_blinking is None:
                frame_blinks.append(0)
            else:
                frame_blinks.append(int(is_blinking))

            if not globals.should_calibrate:
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

                    if pos[0] < left:
                        pg.moveRel(-45, 0)
                    elif pos[0] > right:
                        pg.moveRel(45, 0)
                    
                    if pos[1] < top:
                        pg.moveRel(0, 45)
                    elif pos[1] > bottom:
                        pg.moveRel(0, -45)
            else:
                if not globals.has_topleft:
                    if not globals.msg_topleft:
                        print("Look at the top left and say \"done\".")
                        globals.msg_topleft = True
                    if globals.said_done:# or (left_blink and not last_left_blink):
                        left, top = last_valid_pos
                        print("Saved Top Left at ", left, top)
                        playsound('sounds/correct.mp3')
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
                        playsound('sounds/correct.mp3')
                        globals.should_calibrate = False
                        globals.said_done = False
            if pos:
                last_valid_pos = pos
        elif globals.mode == "nose":  #### NOSE TRACKING ####
            nose_tracker.refresh(frame)
            frame = nose_tracker.annotated_frame()
            cv2.imshow("Nose tracker", frame)
            pos = nose_tracker.find_nose()
            print(pos)

        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()

