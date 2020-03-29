from __future__ import division
import os
import cv2
import dlib
import numpy as np
from .eye import Eye
from .calibration import Calibration

def _add_pos(a, b):
    return a[0] + b[0], a[1] + b[1]

def _midpoint(pa, pb):
    return (pa[0] + pb[0])/2, (pa[1] + pb[1])/2

def ints(p):
    return int(p[0]), int(p[1])

def pxy(p):
    return p.x, p.y

def point_dist(a, b):
    return((a.x-b.x)**2+(a.y-b.y)**2)**0.5

class NoseTracker:
    def __init__(self):
        self._face_detector = dlib.get_frontal_face_detector()
        cwd = os.path.abspath(os.path.dirname(__file__))
        model_path = os.path.abspath(os.path.join(cwd, "trained_models/shape_predictor_68_face_landmarks.dat"))
        self._predictor = dlib.shape_predictor(model_path)
        self.frame = None
        self.landmarks = None
    
    def refresh(self, frame):
        self.frame = frame
        self._analyze()

    def _analyze(self):
        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        faces = self._face_detector(frame)

        if len(faces) > 0:
            self.landmarks = self._predictor(frame, faces[0])
        else:
            self.landmarks = None

    def find_nose(self):
        nose_index = 33
        if self.landmarks:
            p = self.landmarks.part(nose_index)
            return p.x, p.y

    def get_points(self, indexes):
        a = []
        for index in indexes:
            p = self.landmarks.part(index)
            a.append((p.x, p.y))
        return np.array(a)

    def annotated_frame(self):
        frame = self.frame.copy()
        if self.landmarks:
            cv2.polylines(frame, [self.get_points([31, 32, 33, 34, 35])], True, (0, 255, 0))
            pts = self.landmarks.part(33)
            cv2.line(frame, (pts.x, pts.y), (pts.x, pts.y), (0, 255, 0))
        return frame

class EyeTracker(object):
    def __init__(self):
        self.landmarks = None
        self.frame = None
        self.eye_left = None
        self.eye_right = None
        self.calibration = Calibration()
        self._face_detector = dlib.get_frontal_face_detector()
        cwd = os.path.abspath(os.path.dirname(__file__))
        model_path = os.path.abspath(os.path.join(cwd, "trained_models/shape_predictor_68_face_landmarks.dat"))
        self._predictor = dlib.shape_predictor(model_path)

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
        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        faces = self._face_detector(frame)

        try:
            landmarks = self._predictor(frame, faces[0])
            self.landmarks = landmarks
            self.eye_left = Eye(self.frame, landmarks, 0, self.calibration)
            self.eye_right = Eye(self.frame, landmarks, 1, self.calibration)

        except IndexError:
            self.eye_left = None
            self.eye_right = None

    def refresh(self, frame):
        self.frame = frame
        # self.frame = cv2.bilateralFilter(self.frame, 15, 75, 75)
        self._analyze()

    def pupil_left_coords(self):
        if self.pupils_located:
            x = self.eye_left.origin[0] + self.eye_left.pupil.x
            y = self.eye_left.origin[1] + self.eye_left.pupil.y
            return (x, y)

    def pupil_right_coords(self):
        if self.pupils_located:
            x = self.eye_right.origin[0] + self.eye_right.pupil.x
            y = self.eye_right.origin[1] + self.eye_right.pupil.y
            return (x, y)

    def horizontal_ratio(self):
        if self.pupils_located:
            pupil_left = self.eye_left.pupil.x / (self.eye_left.center[0] * 2 - 10)
            pupil_right = self.eye_right.pupil.x / (self.eye_right.center[0] * 2 - 10)
            return (pupil_left + pupil_right) / 2

    def vertical_ratio(self):
        if self.pupils_located:
            pupil_left = self.eye_left.pupil.y / (self.eye_left.center[1] * 2 - 10)
            pupil_right = self.eye_right.pupil.y / (self.eye_right.center[1] * 2 - 10)
            return (pupil_left + pupil_right) / 2

    def is_right(self):
        if self.pupils_located:
            return self.horizontal_ratio() <= 0.35

    def is_left(self):
        if self.pupils_located:
            return self.horizontal_ratio() >= 0.65

    def is_center(self):
        if self.pupils_located:
            return self.is_right() is not True and self.is_left() is not True

    def is_blinking(self):
        if self.eye_left and self.eye_right:
            return self.left_blinking() and self.right_blinking()
        return False

    def left_blinking(self):
        if self.eye_left:
            return self.eye_left.pupil.blinking

    def right_blinking(self):
        if self.eye_right:
            return self.eye_right.pupil.blinking

    def get_left_center_offset_bad(self):
        return int(self.eye_left.center[0]), int(self.eye_left.center[1])

    def get_right_center_offset_bad(self):
        return int(self.eye_right.center[0]), int(self.eye_right.center[1])
    
    def get_left_center_offset(self):
        left_point = self.landmarks.part(36)
        right_point = self.landmarks.part(39)
        return (right_point.x - left_point.x) / 2, (right_point.y - left_point.y) / 2

    def get_right_center_offset(self):
        left_point = self.landmarks.part(42)
        right_point = self.landmarks.part(45)
        return (right_point.x - left_point.x) / 2, (right_point.y - left_point.y) / 2

    def left_center(self):
        return _midpoint(pxy(self.landmarks.part(36)), pxy(self.landmarks.part(39)))

    def right_center(self):
        return _midpoint(pxy(self.landmarks.part(42)), pxy(self.landmarks.part(45)))

    def get_left_pupil_offset(self):
        if self.eye_left and self.pupils_located:
            pupil_exact = self.pupil_left_coords()
            center_exact = self.left_center()
            return center_exact[0] - pupil_exact[0], center_exact[1] - pupil_exact[1]

    def get_right_pupil_offset(self):
        if self.eye_right and self.pupils_located:
            pupil_exact = self.pupil_right_coords()
            center_exact = self.right_center()
            return center_exact[0] - pupil_exact[0], center_exact[1] - pupil_exact[1]
        
    def get_average_offset(self):
        left = self.get_left_pupil_offset()
        right = self.get_right_pupil_offset()
        if left and right:
            eye_dist = self.get_eye_dist()
            return (left[0] + right[0])/(2 * eye_dist), (left[1] + right[1])/(2 * eye_dist)

    def get_eye_dist(self):
        if self.eye_left and self.eye_right:
            dx = self.eye_left.origin[0] - self.eye_right.origin[0]
            dy = self.eye_left.origin[1] - self.eye_right.origin[1]
            return (dx ** 2 + dy ** 2) ** 0.5

    def draw_x(self, frame, x, y, color, w=5):
        cv2.line(frame, (x - w, y), (x + w, y), color)
        cv2.line(frame, (x, y - w), (x, y + w), color)

    def eye_aspect_ratio(self, points):
        numer = point_dist(self.landmarks.part(points[1]), self.landmarks.part(points[5])) + point_dist(self.landmarks.part(points[2]), self.landmarks.part(points[4]))
        denom = 2 * point_dist(self.landmarks.part(points[0]), self.landmarks.part(points[3]))
        return numer/denom

    def left_openness(self):
        return self.eye_aspect_ratio(Eye.LEFT_EYE_POINTS)
        # if self.eye_left and self.eye_right:
        #     pointa = self.landmarks.part(37)
        #     pointb = self.landmarks.part(41)
        #     return ((pointa.x - pointb.x) ** 2 + (pointa.y - pointb.y) ** 2) ** 0.5 / self.get_eye_dist()

    def right_openness(self):
        return self.eye_aspect_ratio(Eye.RIGHT_EYE_POINTS)
        # if self.eye_left and self.eye_right:
        #     pointa = self.landmarks.part(43)
        #     pointb = self.landmarks.part(47)
        #     return ((pointa.x - pointb.x) ** 2 + (pointa.y - pointb.y) ** 2) ** 0.5 / self.get_eye_dist()

    def annotated_frame(self):
        frame = self.frame.copy()

        if self.pupils_located:
            color = (0, 255, 0)
            x_left, y_left = self.pupil_left_coords()
            x_right, y_right = self.pupil_right_coords()
            self.draw_x(frame, x_left, y_left, color)
            self.draw_x(frame, x_right, y_right, color)

            color = (255, 255, 255)
            real_left_center = self.left_center()
            real_right_center = self.right_center()
            self.draw_x(frame, *ints(real_left_center), color)
            self.draw_x(frame, *ints(real_right_center), color)

            color = (0, 120, 255)
            for pa, pb in [(37, 38), (40, 41), (43, 44), (46, 47)]:
                a = self.landmarks.part(pa)
                b = self.landmarks.part(pb)
                cv2.line(frame, (a.x, a.y), (b.x, b.y), color)
                # self.draw_x(frame, p.x, p.y, color)

        return frame
