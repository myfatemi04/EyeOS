import cv2
import numpy as np
import time

from collections import namedtuple

Point2D = namedtuple("Point2D", ['x', 'y'])
Point3D = namedtuple("Point3D", ['x', 'y', 'z'])

goal_square = [[0, 0], [1, 0], [1, 1], [0, 1]]

sensor_width = 98
left_offset = -1
right_offset = 1
kernel = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])

marker_distance = 2

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

def get_3d_point(left_perspective_point, right_perspective_point, left_offset, right_offset, sensor_width):
    # y should not change between sensors, so we'll just take the mean
    # of the detected values
    y = (left_perspective_point[1] + right_perspective_point[1]) / 2

    # Here, we find the relative angle from the center of each sensor
    # TODO: Update based on datasheet data
    left_angle_tan = (left_perspective_point[0] - sensor_width / 2) / sensor_width
    right_angle_tan = (right_perspective_point[0] - sensor_width / 2) / sensor_width

    # Now, we solve for Z based on linear equations.
    # These are the starting equations (based on definition of tan)
    # X = left_offset + Z * left_angle_tan
    # X = right_offset + Z * right_angle_tan
    # left_offset + Z * left_angle_tan = right_offset + Z * right_angle_tan
    # left_offset - right_offset = Z * right_angle_tan - Z * left_angle_tan
    # left_offset - right_offset = Z * (right_angle_tan - left_angle_tan)
    # Z = (left_offset - right_offset) / (right_angle_tan - left_angle_tan)
    
    z = (left_offset - right_offset) / (right_angle_tan - left_angle_tan)
    x = left_offset + z * left_angle_tan

    return (x, y, z)

def get_homography_matrix(calibration_square):
    return cv2.findHomography(calibration_square, goal_square)

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