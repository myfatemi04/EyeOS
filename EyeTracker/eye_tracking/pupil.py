import numpy as np
import cv2


class Pupil(object):
    def __init__(self, eye_frame, threshold):
        self.iris_frame = None
        self.threshold = threshold
        self.x = None
        self.y = None
        self.blinking = False

        self.detect_iris(eye_frame)

    @staticmethod
    def image_processing(eye_frame, threshold):
        kernel = np.ones((3, 3), np.uint8)
        new_frame = cv2.bilateralFilter(eye_frame, 10, 15, 15)
        new_frame = cv2.erode(new_frame, kernel, iterations=3)
        new_frame = cv2.threshold(new_frame, threshold, 255, cv2.THRESH_BINARY)[1]

        return new_frame

    def detect_iris(self, eye_frame):
        self.iris_frame = self.image_processing(eye_frame, self.threshold)
        cv2.imshow("Iris", self.iris_frame)

        contours, _ = cv2.findContours(self.iris_frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[-2:]
        contours = sorted(contours, key=cv2.contourArea)

        num_black = self.iris_frame.shape[0] * self.iris_frame.shape[1] - cv2.countNonZero(self.iris_frame)
        if num_black < 100:
            self.blinking = True
        else:
            self.blinking = False

        # print(num_black)

        try:
            moments = cv2.moments(contours[-2])
            self.x = int(moments['m10'] / moments['m00'])
            self.y = int(moments['m01'] / moments['m00'])
        except (IndexError, ZeroDivisionError):
            pass
