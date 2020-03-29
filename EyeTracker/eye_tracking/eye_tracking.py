from __future__ import division
import os
import cv2
import dlib
import numpy as np
from .eye import Eye
from .calibration import Calibration

# used to find the center of the eye
def _midpoint(pa, pb):
    return (pa[0] + pb[0])/2, (pa[1] + pb[1])/2

# used for drawing on the cv2 frame
def ints(p):
    return int(p[0]), int(p[1])

# helper function
def pxy(p):
    return p.x, p.y

class FaceTracker(object):
    def __init__(self):
        # load dlib face detector
        self._face_detector = dlib.get_frontal_face_detector()

        # model is '68_face_landmarks.dat'
        cwd = os.path.abspath(os.path.dirname(__file__))
        model_path = os.path.abspath(os.path.join(cwd, "trained_models/shape_predictor_68_face_landmarks.dat"))
        
        # initialize the predictor
        self._predictor = dlib.shape_predictor(model_path)

        # allocate vars
        self.frame = None
        self.landmarks = None
        self.eye_left = None
        self.eye_right = None

        # calibration for irises
        self.calibration = Calibration()

    @property
    def pupils_located(self):
        try:
            int(self.eye_left.pupil.x)
            int(self.eye_left.pupil.y)
            int(self.eye_right.pupil.x)
            int(self.eye_right.pupil.y)
            return True
        except Exception:
            return False

    def _analyze(self):
        # image to grayscale
        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        faces = self._face_detector(frame)

        if len(faces) > 0:
            # find landmarks with trained model
            self.landmarks = self._predictor(frame, faces[0])
            self.eye_left = Eye(self.frame, self.landmarks, 0, self.calibration)
            self.eye_right = Eye(self.frame, self.landmarks, 1, self.calibration)
        else:
            self.landmarks = None
            self.eye_left = None
            self.eye_right = None

    # helper function
    def get_points(self, indexes):
        a = []
        for index in indexes:
            p = self.landmarks.part(index)
            a.append((p.x, p.y))
        return np.array(a)
    
    ## analyzes the most recent frame
    def refresh(self, frame):
        self.frame = frame
        self._analyze()

    ## finds pupil locations
    def left_pupil(self):
        if self.pupils_located:
            x = self.eye_left.origin[0] + self.eye_left.pupil.x
            y = self.eye_left.origin[1] + self.eye_left.pupil.y
            return (x, y)

    def right_pupil(self):
        if self.pupils_located:
            x = self.eye_right.origin[0] + self.eye_right.pupil.x
            y = self.eye_right.origin[1] + self.eye_right.pupil.y
            return (x, y)

    ## uses X-value from pupils and Y-value from eyelids
    def left_trace(self):
        if self.pupils_located:
            x = self.eye_left.origin[0] + self.eye_left.pupil.x
            y = self.landmarks.part(37).y
            return x, y
    
    def right_trace(self):
        if self.pupils_located:
            x = self.eye_right.origin[0] + self.eye_right.pupil.x
            y = self.landmarks.part(44).y
            return x, y

    ## determines blink if both eyes are blinking
    def is_blinking(self):
        if self.eye_left and self.eye_right:
            return self.left_blinking() and self.right_blinking()
        return False
    
    ## counts number of black pixels in iris
    def left_blinking(self):
        if self.eye_left:
            return self.eye_left.pupil.blinking

    def right_blinking(self):
        if self.eye_right:
            return self.eye_right.pupil.blinking

    ## center between two important landmarks (creases around the eyes)
    def left_center(self):
        return _midpoint(pxy(self.landmarks.part(36)), pxy(self.landmarks.part(39)))

    def right_center(self):
        return _midpoint(pxy(self.landmarks.part(42)), pxy(self.landmarks.part(45)))

    ## uses pupil tracing
    def get_left_pupil_offset(self):
        if self.eye_left and self.pupils_located:
            pupil_exact = self.left_pupil()
            center_exact = self.left_center()
            return center_exact[0] - pupil_exact[0], center_exact[1] - pupil_exact[1]

    def get_right_pupil_offset(self):
        if self.eye_right and self.pupils_located:
            pupil_exact = self.right_pupil()
            center_exact = self.right_center()
            return center_exact[0] - pupil_exact[0], center_exact[1] - pupil_exact[1]
    
    ## uses eyelid tracing
    def get_left_offset(self):
        if self.eye_left and self.pupils_located:
            left_trace = self.left_trace()
            left_center = self.left_center()
            return left_center[0] - left_trace[0], left_center[1] - left_trace[1]

    def get_right_offset(self):
        if self.eye_right and self.pupils_located:
            right_trace = self.right_trace()
            right_center = self.right_center()
            return right_center[0] - right_trace[0], right_center[1] - right_trace[1]
    
    ## finds how far off the tracepoint is from the center of the eye
    def get_average_eye_offset(self, mode='eyelid'):
        if mode == 'eyelid':
            left = self.get_left_offset()
            right = self.get_right_offset()
        elif mode == 'pupil':
            left = self.get_left_pupil_offset()
            right = self.get_right_pupil_offset()
        if left and right:
            eye_dist = self.get_eye_dist()
            return (left[0] + right[0])/(2 * eye_dist), (left[1] + right[1])/(2 * eye_dist)

    ## used for proportions
    def get_eye_dist(self):
        if self.eye_left and self.eye_right:
            dx = self.eye_left.origin[0] - self.eye_right.origin[0]
            dy = self.eye_left.origin[1] - self.eye_right.origin[1]
            return (dx ** 2 + dy ** 2) ** 0.5

    ## draws a crosshair on the CV2 frame
    def draw_x(self, frame, x, y, color, w=5):
        cv2.line(frame, (x - w, y), (x + w, y), color)
        cv2.line(frame, (x, y - w), (x, y + w), color)

    def find_nose(self):
        nose_index = 33
        if self.landmarks:
            p = self.landmarks.part(nose_index)
            return p.x, p.y

    ## draw on the frame
    def annotated_frame(self):
        frame = self.frame.copy()

        if self.pupils_located:
            color = (0, 255, 0)

            ## show points we use to trace the eyes
            x_left, y_left = self.left_trace()
            x_right, y_right = self.right_trace()
            self.draw_x(frame, x_left, y_left, color)
            self.draw_x(frame, x_right, y_right, color)

            ## show the centers of the eyes (relatively)
            color = (255, 255, 255)
            real_left_center = self.left_center()
            real_right_center = self.right_center()
            self.draw_x(frame, *ints(real_left_center), color)
            self.draw_x(frame, *ints(real_right_center), color)

            ## show the important lankmarks around the eyes
            color = (0, 120, 255)
            for pa, pb in [(37, 38), (40, 41), (43, 44), (46, 47)]:
                a = self.landmarks.part(pa)
                b = self.landmarks.part(pb)
                cv2.line(frame, (a.x, a.y), (b.x, b.y), color)
            
            # self.landmarks.part(33) is the nose
            if self.landmarks:
                cv2.polylines(frame, [self.get_points([31, 32, 33, 34, 35])], True, (0, 255, 0))
                pts = self.landmarks.part(33)
                cv2.line(frame, (pts.x, pts.y), (pts.x, pts.y), (0, 255, 0))

        return frame
