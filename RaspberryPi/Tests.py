import cv2
import numpy as np

from .create import create_target_points, create_camera_matrix

def test_homography():
    points = create_target_points(100, 100)
    camera_matrix = create_camera_matrix(1, 1, 64, 64)

    homo, mask = cv2.findHomography(points, create_target_points(10, 10))

    print("Homography Matrix")
    print(homo)
    print()

    num, rotations, translations, norms = cv2.decomposeHomographyMat(homo, camera_matrix)
    
    print("First rotation possibility")
    print(rotations[0])
    print()
    
    print("First translation possibility")
    print(translations[0])
    print()
    
    print("First normalization possibility")
    print(norms[0])
    print()

    # For some reason, requires a contiguous array
    # And also requires that the points are given as tuples
    board = np.zeros((480, 640, 3), np.uint8)
    board = np.ascontiguousarray(board)
    board = cv2.rectangle(board, tuple(points[0]), tuple(points[2]), (255, 0, 0), 1)

    cv2.imshow("Visualization", board)
    cv2.waitKey(0)

def test_solvepnp():
    camera_matrix = create_camera_matrix(1, 1, 64, 64)
    
    # Data type must be float64
    object_points = np.array([[0, 0, 0], [0, 10, 0], [0, 100, 0], [100, 100, 0], [100, 0, 0]], dtype=np.float64)

    image_points = np.array([[0, 0], [0, 1], [0, 10], [10, 10], [10, 0]], dtype=np.float64)
    image_points += np.array([[64, 64]])

    dist_coeffs = np.zeros((5,))

    ret, rotation, translation = cv2.solvePnP(object_points, image_points, camera_matrix, dist_coeffs)
    print(f"""Rotation
{rotation}

Translation
{translation}""")