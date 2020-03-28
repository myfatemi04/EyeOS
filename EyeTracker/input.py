import cv2
from eye_tracking import EyeTracker

tracker = EyeTracker()
cap = cv2.VideoCapture(0)

while True:
    _, frame = cap.read()
    tracker.refresh(frame)
    frame = tracker.annotated_frame()
    text = ""

    if tracker.is_blinking(): text = "Blinking"
    elif tracker.is_right(): text = "Looking right"
    elif tracker.is_left(): text = "Looking left"
    elif tracker.is_center(): text = "Looking center"

    left = tracker.pupil_left_coords()
    right = tracker.pupil_right_coords()

    f = open("cocksucckler.txt", "w")
    f.write(str(left) + "\t" + str(right) + "\t" + text + "\n")
    f.close()



    """Michael Do stuff here """



    if cv2.waitKey(1) & 0xFF == ord('q'): break
