import pyautogui as pg
import time
from threading import Thread
import speech
import settings
from playsound import playsound

import cv2
from eye_tracking import FaceTracker

### Doesn't stop the program when you look at the corner
pg.FAILSAFE = False

# fits the given position to the screen based on the calibrated values
def transform_pos(pos, left, right, top, bottom, screen_left, screen_right, screen_bottom, screen_top):
    x, y = pos
    width = right - left
    screen_width = screen_right - screen_left
    height = bottom - top
    screen_height = screen_bottom - screen_top
    
    width_prop = (x - left)/width
    height_prop = (y - top)/height

    return width_prop * screen_width + screen_left, height_prop * screen_height + screen_top

def run_main():
    # eye calibrations
    left = right = bottom = top = None
    last_valid_pos = (None, None)

    # used to scale up calibrations
    screen_left, screen_top = (0, 0)
    screen_right, screen_bottom = pg.size()
    

    # used for nose calibrations
    nose_center_x = nose_center_y = None
    nose_x_move = nose_y_move = None
    nose_x_dists = []
    nose_y_dists = []

    # initialize the trackers
    face_tracker = FaceTracker()

    # load video footage
    cap = cv2.VideoCapture(0)

    # keep track of frame number
    i = 0

    print("Booting EyeOS")
    
    # require a mode to be set
    if not settings.mode:
        print("What mode do you want? Nose mode or eye mode?")
    while not settings.mode:
        time.sleep(0.1)

    # infinite loop until "exit"
    while settings.tracker_active:
        i += 1
        
        ### load the trackers
        _, frame = cap.read()
        face_tracker.refresh(frame.copy())
        
        # draw on the frame
        frame = face_tracker.annotated_frame()
        cv2.imshow("EyeOS Tracker", frame)

        if face_tracker.found_face():
            if settings.mode == 'eye':  ### EYE TRACKING ###
                if i % 100 == 0:
                    face_tracker.calibration.recalibrate()

                # find the offset of the pupils
                pos = face_tracker.get_average_eye_offset(mode=settings.eye_trace_mode)
                
                if settings.is_calibrated:
                    last_valid_pos = pos
                    if settings.movement_mode == "cursor":
                        if settings.eye_pos_mode == "absolute":
                            ## absolute positioning
                            ## estimates where you're looking on screen
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
                        elif settings.eye_pos_mode == "relative":
                            ## relative positioning
                            ## moves in 45-px increments
                            if pos[0] < left//2: pg.moveRel(-45, 0)
                            elif pos[0] > right//2: pg.moveRel(45, 0)
                            
                            if pos[1] > top: pg.moveRel(0, -45)
                            elif pos[1] < bottom: pg.moveRel(0, 45)
                    elif settings.eye_pos_mode == "scroll":
                        if pos[0] < left//2: pg.hscroll(-45)
                        elif pos[0] > right//2: pg.hscroll(45)
                        
                        if pos[1] > top: pg.vscroll(-45)
                        elif pos[1] < bottom: pg.vscroll(45)
                else:
                    if not settings.has_topleft:
                        # tell the user what to do
                        if not settings.msg_topleft:
                            settings.msg_topleft = True

                            print("Look at the top left and say \"ready\".")
                        
                        # wait for them to say they're ready
                        if settings.said_ready:
                            left, top = last_valid_pos
                            settings.has_topleft = True
                            settings.said_ready = False

                            print("Saved Top Left at ", left, top)
                            playsound('sounds/correct.mp3')
                        
                    elif not settings.has_bottomright:
                        # tell the user what to do
                        if not settings.msg_bottomright:
                            settings.msg_bottomright = True

                            print("Look at the bottom right and say \"ready\".")
                        
                        # wait for them to say they're ready
                        if settings.said_ready:
                            right, bottom = last_valid_pos
                            settings.has_bottomright = True
                            settings.said_ready = False

                            print("Saved Bottom Right at ", right, bottom)
                            playsound('sounds/correct.mp3')

                    else:
                        settings.is_calibrated = True
            elif settings.mode == "nose":  #### NOSE TRACKING ####
                pos = face_tracker.find_nose()

                nose_x, nose_y = pos

                if not settings.is_calibrated:
                    if not settings.has_nose_center:
                        # tell the user what to do
                        if not settings.msg_nose_center:
                            print("Position your nose in the center of the screen and say \"ready\"")
                            settings.msg_nose_center = True
                        
                        # wait for the use to say that they're ready
                        if settings.said_ready:
                            nose_center_x, nose_center_y = pos
                            
                            settings.said_ready = False
                            settings.has_nose_center = True

                            playsound('sounds/correct.mp3')

                    elif not settings.has_nose_move:
                        # tell the user what to do
                        if not settings.msg_nose_move:
                            print("Move your nose around a little bit")
                            settings.msg_nose_move = True

                        # wait to collect sample data based on nose position
                        if len(nose_x_dists) < 100 and len(nose_y_dists) < 100:
                                nose_dist = 0
                                if nose_center_x and nose_center_y:
                                    nose_dist = ((nose_x - nose_center_x) ** 2 + (nose_y - nose_center_y) ** 2) ** 0.5
                                if nose_dist > 20:
                                    nose_x_dists.append(nose_center_x - pos[0])
                                    nose_y_dists.append(nose_center_y - pos[1])
                        else:
                            max_x_dist = max(nose_x_dists)
                            nose_x_move = max_x_dist * 1.5

                            max_y_dist = max(nose_y_dists)
                            nose_y_move = max_y_dist * 1.5
                            settings.has_nose_move = True

                            print("Nose calibration fit to a", (nose_x_move * 2), "x", (nose_y_move * 2), "box")
                            playsound('sounds/correct.mp3')
                    else:
                        settings.is_calibrated = True
                else: # it's calibrated
                    nose_offset_x = nose_x - nose_center_x
                    nose_offset_y = nose_y - nose_center_y

                    if settings.movement_mode == 'cursor':
                        # scale the nose position to the screen
                        relative_pos = transform_pos(
                            (nose_offset_x, nose_offset_y),
                            nose_x_move,
                            -nose_x_move,
                            -nose_y_move,
                            nose_y_move,
                            screen_left,
                            screen_right,
                            screen_bottom,
                            screen_top
                        )

                        pg.moveTo(*relative_pos)
                    elif settings.movement_mode == 'scroll':
                        # scroll in the requested direction
                        if abs(nose_offset_x) > 20:
                            pg.hscroll(nose_offset_x)
                        if abs(nose_offset_y) > 20:
                            pg.vscroll(-nose_offset_y)

        # option to exit by pressing Q
        if cv2.waitKey(1) & 0xFF == ord('q'):
            settings.tracker_active = False
            break

    cap.release()

# these methods are for use by external applications
# mode = 'eye' or 'nose'
def start_tracker(mode):
    settings.tracker_active = True
    settings.recalibrate()
    settings.mode = mode
    settings.main_thread = Thread(target=run_main, name="Main tracker")
    settings.main_thread.start()

def stop_tracker():
    settings.tracker_active = False
    settings.main_thread.join()
    
def start_speech_to_text():
    speech_thread = Thread(target=speech.speech_to_text, name="speech_to_text", daemon=True)
    speech_thread.start()

if __name__ == "__main__":
    start_tracker("nose")
    start_speech_to_text()
