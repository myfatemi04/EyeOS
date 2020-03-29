import pyautogui as pg
import time
from threading import Thread
import speech
import globals
from playsound import playsound

import cv2
from eye_tracking import EyeTracker, NoseTracker

pg.FAILSAFE = False

# initialize the Eye Tracker
eye_tracker = EyeTracker()
nose_tracker = NoseTracker()
cap = cv2.VideoCapture(0)

BLINK_WAIT = 2.5

def dist(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

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

nose_center_x = None
nose_center_y = None

nose_x_move = None
nose_y_move = None

def recalibrate():
    global top_left, bottom_right, msg_topleft, msg_bottomright, left, right, bottom, top, is_calibrated
    global nose_center_x, nose_center_y, nose_x_move, nose_y_move
    top_left = bottom_right = msg_topleft = msg_bottomright = left = right = bottom = top = None
    nose_center_x = nose_center_y = nose_x_move = nose_y_move = None
    globals.msg_center = False
    globals.msg_movenose = False
    globals.said_centered = False
    globals.should_calibrate = True

i = 0
start_nose_move = 0

if __name__ == "__main__":
    speech_thread = Thread(target=speech.speech_to_text, name="speech_to_text", daemon=True)
    speech_thread.start()
    
    print("Booting EyeOS")
    
    if not globals.mode:
        print("What mode do you want? Nose mode or eye mode?")
    while not globals.mode:
        time.sleep(0.5)

    last_x, last_y = pg.position()

    while not globals.should_stop:
        i += 1
        
        _, frame = cap.read()
        eye_tracker.refresh(frame.copy())
        if globals.mode == 'eye':  ### EYE TRACKING ###
            if i % 100 == 0:
                eye_tracker.calibration.recalibrate()
            frame = eye_tracker.annotated_frame()
            cv2.imshow("Eye tracker", frame)

            pos = eye_tracker.get_average_offset()
            
            is_blinking = eye_tracker.is_blinking()

            if is_blinking is None:
                frame_blinks.append(0)
            else:
                frame_blinks.append(int(is_blinking))

            if not globals.should_calibrate:
                if pos:
                    if globals.eye_pos_mode == "absolute":
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

                        int_pos = int(tpos[0]), int(tpos[1])
                        pg.moveTo(int_pos[0], int_pos[1])
                    else:
                        if pos[0] < left//2:
                            pg.moveRel(-45, 0)
                        elif pos[0] > right//2:
                            pg.moveRel(45, 0)
                        
                        if pos[1] > top:
                            pg.moveRel(0, -45)
                        elif pos[1] < bottom:
                            pg.moveRel(0, 45)
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

            if not pos:
                continue
            
            nose_dist = 0
            if nose_center_x:
                nose_dist = dist((nose_center_x, nose_center_y), pos)

            if globals.should_calibrate:
                if not globals.has_nose_center:
                    if not globals.msg_center:
                        print("Position your nose in the center of the screen and say \"centered\"")
                        globals.msg_center = True
                    if globals.said_centered:
                        nose_center_x, nose_center_y = nose_tracker.find_nose()
                        globals.said_centered = False
                        globals.has_nose_center = True
                        playsound('sounds/correct.mp3')
                elif not globals.has_nose_move:
                    if not globals.msg_movenose:
                        print("Move your nose around a little bit")
                        globals.msg_movenose = True
                        nose_x_dists = []
                        nose_y_dists = []
                    if len(nose_x_dists) < 100 and len(nose_y_dists) < 100:
                        if nose_dist > 20:
                            nose_x_dists.append(nose_center_x - pos[0])
                            nose_y_dists.append(pos[1] - nose_center_y)
                    else:
                        max_x_dist = max(nose_x_dists)
                        nose_x_move = max_x_dist * 1.5
                        max_y_dist = max(nose_y_dists)
                        nose_y_move = max_y_dist * 1.5
                        globals.has_nose_move = True

                        print("Nose movement min distance: ", nose_x_move, nose_y_move)
                        playsound('sounds/correct.mp3')
                else:
                    globals.should_calibrate = False
            else:
                relative_pos = transform_pos(
                    pos,
                    nose_center_x + nose_x_move,
                    nose_center_x - nose_x_move,
                    nose_center_y - nose_y_move,
                    nose_center_y + nose_y_move,
                    screen_left,
                    screen_right,
                    screen_bottom,
                    screen_top
                )

                pg.moveTo(*relative_pos)

        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()

