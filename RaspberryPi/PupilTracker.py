import cv2
import numpy as np
import time

from collections import namedtuple

Point2D = namedtuple("Point2D", ['x', 'y'])
Point3D = namedtuple("Point3D", ['x', 'y', 'z'])

goal_square = [[0, 0], [1, 0], [1, 1], [0, 1]]

def get_perspective_transform(calibration_square):
    matrix = cv2.findHomography(calibration_square, goal_square)

# Reads markers found by sensor
def get_all_markers():
    pass

# Extracts the calibration square from a list of all markers found
def get_calibration_square_corners(markers):
    pass

# Extracts the screen corners from a list of all markers found
def get_screen_corners(markers):
    pass

def flatten_plane_and_intersection(plane, intersection):
    pass

# Finds the location within the plane of the eye
def get_plane_location(plane, plane_point):
    pass

# Calculates the intersection of a ray and a plane.
# In this case, the ray is the eye's gaze ray, and the plane is the
# computer screen.
def calculate_ray_plane_intersection(ray, plane):
    pass

def use_pi():
    from picamera.array import PiRGBArray
    from picamera import PiCamera

    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 90

    capture = PiRGBArray(camera, size=(640, 480))

    # Let the camera warm up
    time.sleep(0.1)

    # Capture frames in a stream
    for frame in camera.capture_continuous(capture, format="rgb", use_video_part=True):
        # Get the NumPy array
        image = frame.array
        process_image(image)

def use_video_capture():
    video_capture = cv2.VideoCapture(1)
    
    while True:
        _, frame = video_capture.read()

        process_image(frame)

        # option to exit by pressing Q
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

def process_image(image):
    annotated = image.copy()

    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # image = cv2.equalizeHist(image)
    image = cv2.GaussianBlur(image, (3, 3), 1)
    _, image = cv2.threshold(image, THRESHOLD_MIN, THRESHOLD_MAX, cv2.THRESH_BINARY_INV)

    # Reduce noise by eroding and dilating the parts that survived erosion
    image = cv2.erode(image, kernel, iterations=1)
    image = cv2.dilate(image, kernel, iterations=2)

    contours, _ = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    possible_eyes = []

    for contour in contours:
        area = cv2.contourArea(contour)
        rectangle = cv2.boundingRect(contour)

        rect_x, rect_y, rect_width, rect_height = rectangle
        rect_area = rect_width * rect_height

        if area / rect_area < MIN_BOUNDING_RECT_AREA:
            continue

        if area > MAX_AREA or area < MIN_AREA:
            continue
        
        aspect_ratio = (rect_width / rect_height)
        if aspect_ratio < MIN_ASPECT_RATIO or aspect_ratio > 1 / MIN_ASPECT_RATIO:
            continue

        M = cv2.moments(contour)

        if M["m00"] == 0:
            continue

        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])

        annotated = cv2.drawMarker(annotated, (cX, cY), (0, 255, 255))
        
        possible_eyes.append(contour)

    annotated = cv2.drawContours(annotated, possible_eyes, -1, (0, 255, 0), 3)
    
    cv2.imshow("Binary image", image)
    cv2.imshow(window_name, annotated)

def set_threshold_min(new_threshold_min):
    global THRESHOLD_MIN
    THRESHOLD_MIN = new_threshold_min

def set_threshold_max(new_threshold_max):
    global THRESHOLD_MAX
    THRESHOLD_MAX = new_threshold_max

def create_kernel(kernel_size, mode='vertical'):
    global kernel

    width = kernel_size // 2

    if mode == 'circle':
        kernel = np.array([
            [
                int(((x - width) ** 2 + (y - width) ** 2) ** 0.5 <= width)
                for x in range(kernel_size)
            ] for y in range(kernel_size)
        ]).astype(np.uint8)

    elif mode == 'cross':
        kernel = np.zeros((kernel_size, kernel_size), dtype=np.uint8)
        kernel[width, :] = 1
        kernel[:, width] = 1

    elif mode == 'vertical':
        kernel = np.zeros((kernel_size, kernel_size), dtype=np.uint8)
        kernel[:, width] = 1

    print(kernel)

window_name = "Circle detection testing"

THRESHOLD_MIN = 40
THRESHOLD_MAX = 255

MIN_AREA = 1000
MAX_AREA = 1000000

MIN_ASPECT_RATIO = 2 / 3 # less than 1
MIN_BOUNDING_RECT_AREA = 0.5 # must be approximately a circle within the rectangle

create_kernel(5)

cv2.namedWindow(window_name)
cv2.createTrackbar("Threshold Min", window_name, THRESHOLD_MIN, 255, set_threshold_min)
cv2.createTrackbar("Threshold Max", window_name, THRESHOLD_MAX, 255, set_threshold_max)
cv2.createTrackbar("Kernel size", window_name, 2, 5, lambda x: create_kernel(x * 2 + 1))

use_video_capture()