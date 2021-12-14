import cv2
import numpy as np

from eye_tracking.find_eyes import find_all_eyes

"""
The process is simple.
 (1) Calibrate the gaze tracker to the screen.
 (2) Start estimating locations.
"""

class EyeGazeEstimator:
	def __init__(self):
		self.mode = 'eye'
		pass

	def add_calibration_frames(self, frame: np.ndarray):
		pass

	def estimate_gaze(self, frame: np.ndarray):
		pass

lix = 0
liy = 0
rix = 0
riy = 0

adjustment_speed = 0.5

cap = cv2.VideoCapture(0)
while True:
	ret, frame = cap.read()

	all_eyes = find_all_eyes(frame, 50)
	for (left, right) in all_eyes:
		cv2.rectangle(frame, left.bounding_box[:2], left.bounding_box[2:], (0, 255, 0), 2)
		cv2.rectangle(frame, right.bounding_box[:2], right.bounding_box[2:], (0, 255, 0), 2)

		# print(left.iris[0] - left.bounding_box[0], left.iris[1] - left.bounding_box[1], left.bounding_box[:2], left.bounding_box[2] - left.bounding_box[0], left.bounding_box[3] - left.bounding_box[1])

		if left.iris is not None:
			lix = lix * (1 - adjustment_speed) + left.iris[0] * adjustment_speed
			liy = liy * (1 - adjustment_speed) + left.iris[1] * adjustment_speed
			cv2.circle(frame, (int(lix), int(liy)), 2, (0, 0, 255), 2)

		if right.iris is not None:
			rix = rix * (1 - adjustment_speed) + right.iris[0] * adjustment_speed
			riy = riy * (1 - adjustment_speed) + right.iris[1] * adjustment_speed
			cv2.circle(frame, (int(rix), int(riy)), 2, (0, 0, 255), 2)

	cv2.imshow('frame', frame)
	
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
