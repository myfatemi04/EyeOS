is_calibrated = False

msg_bottomright = False
has_bottomright = False

has_topleft = False
msg_topleft = False

msg_nose_center = False
has_nose_center = False

msg_nose_move = False
has_nose_move = False

mode = "nose"
eye_pos_mode = "absolute"
eye_trace_mode = "eyelid"

movement_mode = "cursor"

said_ready = False

tracker_active = False

def recalibrate():
    global is_calibrated
    global has_bottomright, has_topleft, has_nose_center, has_nose_move
    global msg_bottomright, msg_topleft, msg_nose_center, msg_nose_move
    is_calibrated = False
    has_bottomright = False
    has_topleft = False
    msg_bottomright = False
    msg_topleft = False
    has_nose_center = False
    has_nose_move = False
    msg_nose_center = False
    msg_nose_move = False

main_thread = None
