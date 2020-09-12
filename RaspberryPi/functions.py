import cv2
import numpy as np

def get_3d_point(left_perspective_point, right_perspective_point, left_offset, right_offset, sensor_width):
    # y should not change between sensors, so we'll just take the mean
    # of the detected values
    y = (left_perspective_point[1] + right_perspective_point[1]) / 2

    # Here, we find the relative angle from the center of each sensor
    # TODO: Update based on datasheet data
    left_angle_tan = (left_perspective_point[0] - sensor_width / 2) / sensor_width
    right_angle_tan = (right_perspective_point[0] - sensor_width / 2) / sensor_width

    """
    Now, we solve for Z based on linear equations.
    These are the starting equations (based on definition of tan)
    X = left_offset + Z * left_angle_tan
    X = right_offset + Z * right_angle_tan
    left_offset + Z * left_angle_tan = right_offset + Z * right_angle_tan
    left_offset - right_offset = Z * right_angle_tan - Z * left_angle_tan
    left_offset - right_offset = Z * (right_angle_tan - left_angle_tan)
    Z = (left_offset - right_offset) / (right_angle_tan - left_angle_tan)
    """
    
    z = (left_offset - right_offset) / (right_angle_tan - left_angle_tan)
    x = left_offset + z * left_angle_tan

    return (x, y, z)

def in_range(x, a, b):
    return a < x < b

def find_pupils(image, threshold_min, kernel, min_bounding_rect_area, min_area, max_area, min_aspect_ratio):
    """Finds the contours for potential pupils in an image.

    Args:
        image (numpy array): Input image, BGR format
        threshold_min (int): Minimum pixel value to be considered a possible pupil
        kernel (numpy array): An NxN matrix which is used to filter out points with .erode() and .dilate()
        min_bounding_rect_area (float): Minimum amount that the contour must fill its bounding rectangle
        min_area (float): Minimum area of pupil in pixels
        max_area (float): Maximum area of pupil in pixels
        min_aspect_ratio (float): Minimum value of Width/Height -- eccentricity.

    Returns:
        list of numpy array: Contours
    """

    max_aspect_ratio = 1 / min_aspect_ratio

    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # Blur image to make detection of blobs more accurate
    image = cv2.GaussianBlur(image, (3, 3), 1)

    # Pass through a threshold because the pupil will be bright
    _, image = cv2.threshold(image, threshold_min, 255, cv2.THRESH_BINARY_INV)

    # Reduce noise by eroding and dilating the parts that survived erosion
    image = cv2.erode(image, kernel, iterations=1)
    image = cv2.dilate(image, kernel, iterations=2)

    ret, contours, _ = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    possible_eyes = []
    for contour in contours:
        area = cv2.contourArea(contour)
        rectangle = cv2.boundingRect(contour)

        rect_x, rect_y, rect_width, rect_height = rectangle
        rect_area = rect_width * rect_height

        if area / rect_area < min_bounding_rect_area:
            continue

        if not in_range(area, min_area, max_area):
            continue
        
        aspect_ratio = (rect_width / rect_height)
        if not in_range(aspect_ratio, min_aspect_ratio, max_aspect_ratio):
            continue

        M = cv2.moments(contour)

        if M["m00"] == 0:
            continue

        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])

        possible_eyes.append(contour)

    return possible_eyes
