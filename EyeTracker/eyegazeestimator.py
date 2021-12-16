import cv2
import numpy as np
import pyautogui as pg

from eye_tracking.find_eyes import find_all_eyes, mid

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

class SmoothValue:
	def __init__(self, value=0, weight=0.5):
		self.value = value
		self.weight = weight

	@property
	def i(self):
		return int(self.value)

	def update(self, new_value):
		self.value = self.value * self.weight + new_value * (1 - self.weight)

def transform_gaze(left_offset, right_offset, calibrations: dict):
	average_offset = mid(left_offset, right_offset)
	x1, y1, x2, y2 = 1e100, 1e100, -1e100, -1e100
	for calibration_left_offset, calibration_right_offset in calibrations.values():
		calibration_average_offset = mid(calibration_left_offset, calibration_right_offset)
		x1 = min(x1, calibration_average_offset[0])
		y1 = min(y1, calibration_average_offset[1])
		x2 = max(x2, calibration_average_offset[0])
		y2 = max(y2, calibration_average_offset[1])

	bounding_box_width = x2 - x1
	bounding_box_height = y2 - y1

	# print("bounding box width & height:", bounding_box_width, bounding_box_height)
	
	horizontal_proportion = (average_offset[0] - x1) / bounding_box_width
	vertical_proportion = (average_offset[1] - y1) / bounding_box_height

	return horizontal_proportion, vertical_proportion

lix = SmoothValue()
liy = SmoothValue()
rix = SmoothValue()
riy = SmoothValue()

calibrations = {}
required_calibrations = [
	(0, 0), (1920, 1080)
]

adjustment_speed = 0.5

import time

prev_calibration_time = 0
next_calibration_time = time.time() + 5

pg.FAILSAFE = False

analytics_canvas = np.zeros((480, 640, 3), np.uint8)

frame_number = 0

cap = cv2.VideoCapture(0)
while True:
	ret, frame = cap.read()
	frame_number += 1

	all_eyes = find_all_eyes(frame, 50)
	for (left, right) in all_eyes:
		cv2.rectangle(frame, left.bounding_box[:2], left.bounding_box[2:], (0, 255, 0), 2)
		cv2.rectangle(frame, right.bounding_box[:2], right.bounding_box[2:], (0, 255, 0), 2)

		if left.iris is None or right.iris is None:
			continue

		lix.update(left.iris[0])
		liy.update(left.iris[1])
		cv2.circle(frame, left.iris, 2, (0, 0, 255), 2)

		rix.update(right.iris[0])
		riy.update(right.iris[1])
		cv2.circle(frame, right.iris, 2, (0, 0, 255), 2)

		cv2.circle(frame, left.center, 2, (0, 255, 0), 2)
		cv2.circle(frame, right.center, 2, (0, 255, 0), 2)

		left_offset = (left.center[0] - left.iris[0], left.points[1][1] - left.center[1])
		right_offset = (right.center[0] - right.iris[0], right.points[1][1] - right.center[1])

		""" If we're calibrated, then we can estimate the gaze """
		if len(calibrations) == len(required_calibrations):
			horizontal_proportion, vertical_proportion = transform_gaze(left_offset, right_offset, calibrations)

			dx = 2

			analytics_frame_idx = frame_number % (640 // dx)

			x = analytics_frame_idx * dx
			top_y = 360

			cv2.rectangle(analytics_canvas, (x, 0), (x + dx, 480), (0, 0, 0), -1)
			# draw horizontal position
			# draw vertical position
			cv2.rectangle(analytics_canvas, \
				(x, top_y - int(vertical_proportion * 240)),
				(x + dx, top_y - int(vertical_proportion * 240) - 5),
				(0, 0, 255),
			-1)
			
			cv2.rectangle(analytics_canvas, \
				(x, top_y - int(horizontal_proportion * 240)),
				(x + dx, top_y - int(horizontal_proportion * 240 - 5)),
				(255, 0, 0),
			-1)

			cv2.imshow("analytics", analytics_canvas)

			if vertical_proportion > 0.8:
				pg.scroll(int(-(vertical_proportion - 0.8) * 60))

			elif vertical_proportion < 0.2:
				pg.scroll(int((0.2 - vertical_proportion) * 120))

			# pg.moveTo(int(horizontal_proportion * 1920), int(vertical_proportion * 1080), 0.2, pg.easeInOutCubic)
		elif time.time() > next_calibration_time and prev_calibration_time != next_calibration_time:
			prev_calibration_time = next_calibration_time

			for calibration in required_calibrations:
				if calibration in calibrations:
					continue

				print('Calibrating', calibration)
				calibrations[calibration] = (left_offset, right_offset)
				break

			if len(calibrations) < len(required_calibrations):
				next_calibration_time = time.time() + 5

	cv2.imshow('frame', frame)
	
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
