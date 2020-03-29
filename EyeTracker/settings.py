is_calibrated = False

msg_bottomright = False
has_bottomright = False

has_topleft = False
msg_topleft = False

msg_nose_center = False
has_nose_center = False

msg_nose_move = False
has_nose_move = False

mode = "eye"
eye_pos_mode = "absolute"
eye_trace_mode = "eyelid"

said_ready = False
said_centered = False
said_moved = False

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
