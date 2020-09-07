import cv2
import numpy as np
import time

from collections import namedtuple

from .functions import find_pupils
from .create import create_kernel, create_camera_matrix

window_name = "Gaze Tracker"

THRESHOLD_MIN = 40

MIN_AREA = 1000
MAX_AREA = 1000000

MIN_ASPECT_RATIO = 2 / 3 # less than 1
MIN_BOUNDING_RECT_AREA = 0.5 # must be approximately a circle within the rectangle

sensor_width = 128
left_offset = -1
right_offset = 1

kernel = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])

center_x = center_y = 64
focal_x = focal_y = 1

camera_matrix = create_camera_matrix(focal_x, focal_y, center_x, center_y)

marker_distance = 2

### REFERENCES
# https://docs.opencv.org/2.4/modules/calib3d/doc/camera_calibration_and_3d_reconstruction.html?highlight=findhomography
#

def estimate_gaze_vector(eye_img):
    pass

def dist(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

# Returns the width and height
def get_screen_dimensions(top_left, top_left_marker_right, top_left_marker_bottom, bottom_left, top_right):
    left_pixel_length = dist(top_left, bottom_left)
    top_pixel_length = dist(top_left, top_right)
    top_marker_pixel_dist = dist(top_left, top_left_marker_right)
    left_marker_pixel_dist = dist(top_left, top_left_marker_bottom)

    # pixel distance of markers / real life distance = pixel length of side / real life length of side
    top_length = top_pixel_length / (top_marker_pixel_dist / marker_distance)
    left_length = left_pixel_length / (left_marker_pixel_dist / marker_distance)

    return top_length, left_length

def flatten_plane_and_intersection(plane, intersection):
    pass

# Finds the location within the plane of the eye
def get_eye_location_in_plane(plane, point):
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
        find_pupils(image, THRESHOLD_MIN, kernel, MIN_BOUNDING_RECT_AREA, MIN_AREA, MAX_AREA, MIN_ASPECT_RATIO)

def use_video_capture():
    video_capture = cv2.VideoCapture(1)
    
    while True:
        _, frame = video_capture.read()

        find_pupils(frame)

        # option to exit by pressing Q
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

def set_threshold_min(new_threshold_min):
    global THRESHOLD_MIN
    THRESHOLD_MIN = new_threshold_min

def set_kernel_size(n):
    global kernel
    kernal = create_kernel(n)

def main():
    set_kernel_size(5)

    cv2.namedWindow(window_name)
    cv2.createTrackbar("Threshold Min", window_name, THRESHOLD_MIN, 255, set_threshold_min)
    cv2.createTrackbar("Kernel size", window_name, 2, 5, lambda x: set_kernel_size(x * 2 + 1))

    use_video_capture()
