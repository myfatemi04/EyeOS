import cv2
import math
import numpy as np
import time

from collections import namedtuple

from functions import find_pupils
from create import create_kernel, create_camera_matrix

window_name = "Gaze Tracker"

THRESHOLD_MIN = 40

MIN_AREA = 1000
MAX_AREA = 1000000

MIN_ASPECT_RATIO = 2 / 3 # less than 1
MIN_BOUNDING_RECT_AREA = 0.5 # must be approximately a circle within the rectangle

sensor_width = 128
left_offset = -1
right_offset = 1

kernel = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=np.uint8)

center_x = center_y = 64
focal_x = focal_y = 1

image_size = (640, 480)

camera_matrix = create_camera_matrix(focal_x, focal_y, center_x, center_y)

marker_distance = 2

def get_relative_vector(eye_to_camera, eye_radius, angle_from_camera):
    """Gets a gaze vector based on the angle between the pupil, camera, and center of the eye.
    Gaze vector is such that the line from the eye origin to the camera is the X axis.
    The eye origin is the origin of the vector.

    Args:
        eye_to_camera (float): Distance from eye to camera (2D center of eye)
        eye_radius (float): Radius of eye
        angle_from_camera (float): Angle CVP, where C = center of eye, V = camera, P = pupil

    Note: by "center" of eye, we mean the point of intersection between the line connecting
          the origin of the eye sphere and the camera, and the eye sphere.

    Returns:
        [type]: [description]
    """

    eye_origin_to_camera = eye_to_camera + eye_radius

    camera_to_right = eye_origin_to_camera * math.cos(angle_from_camera)
    eye_origin_to_right = eye_origin_to_camera * math.sin(angle_from_camera)

    pupil_to_right = (eye_radius ** 2 - eye_origin_to_right ** 2) ** 0.5
    camera_to_pupil = camera_to_right - pupil_to_right

    x = eye_origin_to_camera - camera_to_pupil * math.cos(angle_from_camera)
    y = camera_to_pupil * math.sin(angle_from_camera)

    return (x,  y)

### REFERENCES
# https://docs.opencv.org/2.4/modules/calib3d/doc/camera_calibration_and_3d_reconstruction.html?highlight=findhomography
#

def estimate_gaze_vector(eye_img, eye_center=(image_size[0] // 2, image_size[1]//2)):
    pupil_contours = find_pupils(eye_img, THRESHOLD_MIN, kernel, MIN_BOUNDING_RECT_AREA, MIN_AREA, MAX_AREA, MIN_ASPECT_RATIO)

    if len(pupil_contours) == 0:
        return None

    pupil_contour = pupil_contours[0]
    moments = cv2.moments(pupil_contour)

    if moments['m00'] == 0:
        # No possible centroid found
        return None

    # Pupil centroid
    # Reference: https://www.learnopencv.com/find-center-of-blob-centroid-using-opencv-cpp-python/
    pupil_image_x = moments['m10'] / moments['m00']
    pupil_image_y = moments['m01'] / moments['m00']

    eye_center_x, eye_center_y = eye_center

    image_offset_x = pupil_image_x - eye_center_x
    image_offset_y = pupil_image_y - eye_center_y

    pupil_distance = ((image_offset_x ** 2) + (image_offset_y ** 2)) ** 0.5
    
    # http://www.kumantech.com/kuman-5mp-1080p-hd-camera-module-for-raspberry-pi-for-raspberry-pi-3-model-b-b-a-rpi-2-1-sc15_p0063.htm
    field_of_view_degrees = 72.4
    field_of_view_radians = 1.263618378443895 # (math.pi * field_of_view_degrees / 180)
    field_of_view_pixels = 2202.9071700823 # (1080 ** 2 + 1920 ** 2) ** 0.5
    
    angle_from_camera = get_angle_from_camera(pupil_distance, field_of_view_radians, field_of_view_pixels)
    rotation_angle = math.atan(image_offset_y / image_offset_x)
    
    # these are in cm
    eye_to_camera = 4
    eye_radius = 3.75
    
    rx, ry = get_relative_vector(eye_to_camera, eye_radius, angle_from_camera)
    
    # looking at the eye head-on, x = depth, y = side to side, z = up down
    relative_vector_flat = (rx, ry, 0)
    
    # the 2D projection of this is (y, 0)
    # we rotate this by rotation_angle to get (ycostheta, ysintheta)
    relative_vector = (rx, ry * math.cos(rotation_angle), ry * math.sin(rotation_angle)) 
    
    return {'relative_vector': relative_vector, 'pupil_location': (pupil_image_x, pupil_image_y),
            'angle_from_camera': angle_from_camera}
    
def get_2d_rotation_matrix(angle):
    # linear transformation = X(i) + Y(j) = X * ix + X * iy + Y * jx + Y * jy
    # usually, ix = 1, iy = 0; jx = 0, jy = 1. However, by changing
    # the basis vectors, we can make a rotation
    
    ix = math.cos(angle)
    iy = math.sin(angle)
    
    jx = -math.sin(angle)
    jy = math.cos(angle)
    
    return np.array([
        [ix, jx],
        [iy, jy]
    ])

def get_angle_from_camera(distance_pixels, field_of_view_radians, field_of_view_pixels):
    return (distance_pixels / field_of_view_pixels) * field_of_view_radians

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
    from imutils.video import VideoStream
    
    stream = VideoStream(usePiCamera=True, resolution=image_size).start()

    # Let the camera warm up
    time.sleep(2.0)
    
    # Capture frames in a stream
    while True:
        image = stream.read()
        
        gaze_info = estimate_gaze_vector(image)
        
        if gaze_info is not None:
            relative_vector = gaze_info['relative_vector']
            eye_x, eye_y = gaze_info['pupil_location']
            eye_x = int(eye_x)
            eye_y = int(eye_y)
            
            image = cv2.drawMarker(image, (eye_x, eye_y), (255, 255, 255))
            
            # print(relative_vector)
            
            visualization = np.zeros((500, 500, 3), np.uint8)
            vis_eye_location = (250, 250)
            vis_gaze_target = (250 + int(relative_vector[0] * 20), 250 + int(relative_vector[1] * 20))
            
            # Draw "eye"
            visualization = cv2.circle(visualization, vis_eye_location, 50, (255, 255, 255), -1)
            
            # Gaze line
            visualization = cv2.line(visualization, vis_eye_location, vis_gaze_target, (0, 255, 0), 10)
            
            cv2.imshow("Top-down gaze visualization", visualization)
            # find_pupils(image, THRESHOLD_MIN, kernel, MIN_BOUNDING_RECT_AREA, MIN_AREA, MAX_AREA, MIN_ASPECT_RATIO)
        
        cv2.imshow("Video stream", image)
        
        if cv2.waitKey(1) & 0xFF == 'q':
            break

def use_video_capture():
    video_capture = cv2.VideoCapture(1)
    
    while True:
        _, image = video_capture.read()

        find_pupils(image, THRESHOLD_MIN, kernel, MIN_BOUNDING_RECT_AREA, MIN_AREA, MAX_AREA, MIN_ASPECT_RATIO)

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
    
    '''
    cv2.namedWindow(window_name)
    cv2.createTrackbar("Threshold Min", window_name, THRESHOLD_MIN, 255, set_threshold_min)
    cv2.createTrackbar("Kernel size", window_name, 2, 5, lambda x: set_kernel_size(x * 2 + 1))
    '''
    
    use_pi()
    
main()
