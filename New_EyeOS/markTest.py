import cv2
from eye_tracker import EyeTracker

eyetracker = EyeTracker()
webcam = cv2.VideoCapture(0)

print("Press [esc] to exit")

while True:
    ret, frame = webcam.read()

    if ret:
        eyetracker.refresh(frame)

        frame = eyetracker.annotated_frame()
        text = ""

        cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

        left_pupil = eyetracker.pupil_left_coords()
        right_pupil = eyetracker.pupil_right_coords()

    cv2.imshow("BruhFuckThis", frame)

    if cv2.waitKey(1) == 27:
        break
