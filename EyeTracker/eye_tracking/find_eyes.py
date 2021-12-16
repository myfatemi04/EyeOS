from typing import List, Tuple

import cv2
import dlib
import numpy as np

find_faces = dlib.get_frontal_face_detector()
find_landmarks = dlib.shape_predictor('eye_tracking/trained_models/shape_predictor_68_face_landmarks.dat')

def mid(a, b):
	return (a[0] + b[0]) / 2, (a[1] + b[1]) / 2

class EyeDetection:
	def __init__(self, frame: np.ndarray, points: list, iris_threshold__old: int):
		min_x = min(points, key=lambda p: p[0])[0]
		max_x = max(points, key=lambda p: p[0])[0]
		min_y = min(points, key=lambda p: p[1])[1]
		max_y = max(points, key=lambda p: p[1])[1]

		margin = 5

		self.points = points
		self.bounding_box = (min_x, min_y, max_x, max_y)
		self.original_frame = frame
		self.eye_frame_gray = cv2.cvtColor(frame[min_y - margin:max_y + margin, min_x - margin:max_x + margin], cv2.COLOR_BGR2GRAY)

		iris = find_iris(self.eye_frame_gray)
		if iris is not None:
			self.iris = iris[0] + min_x - margin, iris[1] + min_y - margin
		else:
			self.iris = None
	
	@property
	def center(self):
		x, y = mid(self.points[0], self.points[3])
		return int(x), int(y)

def find_best_iris_threshold(eye_frame_gray: np.ndarray):
	average_iris_size = 0.48
	best_threshold = 0
	best_score = 2

	for threshold in range(5, 100, 5):
		iris = find_iris(eye_frame_gray, threshold)
		if iris is None:
			continue
			
		_, _, num_black, num_pixels = iris
		iris_size = num_black / num_pixels
		score = abs(iris_size - average_iris_size)
		if score < best_score:
			best_threshold = threshold
			best_score = score
	
	return best_threshold

def find_iris(eye_frame_gray: np.ndarray, threshold: int = 50):
	kernel = np.ones((3, 3), np.uint8)
	iris_frame = cv2.bilateralFilter(eye_frame_gray, 10, 15, 15)
	# iris_frame = cv2.erode(iris_frame, kernel, iterations=3)
	iris_frame = cv2.equalizeHist(iris_frame)

	iris_frame = 255 - cv2.threshold(iris_frame, threshold, 255, cv2.THRESH_BINARY)[1]

	contours, _ = cv2.findContours(iris_frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	contours = sorted(contours, key=cv2.contourArea)

	num_pixels = iris_frame.shape[0] * iris_frame.shape[1]
	num_black = num_pixels - cv2.countNonZero(iris_frame)

	try:
		moments = cv2.moments(contours[-1])
		x = int(moments['m10'] / moments['m00'])
		y = int(moments['m01'] / moments['m00'])
		cv2.circle(iris_frame, (x, y), 2, (0, 0, 255), -1)
	except (IndexError, ZeroDivisionError):
		return None
		
	cv2.imshow('iris', iris_frame)

	return (x, y, num_black, num_pixels)

def find_eyes(frame, landmarks, iris_threshold) -> list:
	select_landmarks = lambda selection: [np.array([landmarks[i].x, landmarks[i].y]) for i in selection]

	left = EyeDetection(frame, select_landmarks([36, 37, 38, 39, 40, 41]), iris_threshold)
	right = EyeDetection(frame, select_landmarks([42, 43, 44, 45, 46, 47]), iris_threshold)

	return (left, right)

def find_all_eyes(frame, iris_threshold) -> List[Tuple[EyeDetection, EyeDetection]]:
	faces = find_faces(frame)
	eyes = []

	for face in faces:
		landmarks = find_landmarks(frame, face)
		landmarks = landmarks.parts()

		left, right = find_eyes(frame, landmarks, iris_threshold)

		eyes.append((left, right))

	return eyes


