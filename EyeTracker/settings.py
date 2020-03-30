is_calibrated = False

has = {
    'top left': False,
    'top right': False,
    'bottom right': False,
    'bottom left': False
}

msg = {
    'top left': False,
    'top right': False,
    'bottom right': False,
    'bottom left': False
}

msg_nose_center = False
has_nose_center = False

msg_nose_move = False
has_nose_move = False

mode = "nose"
eye_pos_mode = "absolute"
eye_trace_mode = "eyelid"

movement_mode = "cursor"

tracker_active = False
sst_active = False

typing_on = True
launcher_on = True

mouse_stabilization = 4

def recalibrate():
    global is_calibrated
    global has_bottomright, has_topleft, has_nose_center, has_nose_move
    global msg_bottomright, msg_topleft, msg_nose_center, msg_nose_move

    is_calibrated = False

    has_bottomright = False
    has_topleft = False
    has_nose_center = False
    has_nose_move = False

    msg_bottomright = False
    msg_topleft = False
    msg_nose_center = False
    msg_nose_move = False

main_thread = None
