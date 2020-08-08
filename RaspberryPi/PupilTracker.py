import cv2
import numpy as np

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
    video_capture = cv2.VideoCapture(0)
    
    while True:
        _, frame = video_capture.read()

        process_image(frame)

        # option to exit by pressing Q
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

def process_image(image):
    original = image.copy()

    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # image = cv2.equalizeHist(image)
    # image = cv2.GaussianBlur(image, (3, 3), 1)
    _, image = cv2.threshold(image, threshold_min, threshold_max, cv2.THRESH_BINARY_INV)

    # Reduce noise by eroding and dilating the parts that survived erosion
    image = cv2.erode(image, kernel, iterations=1)
    image = cv2.dilate(image, kernel, iterations=2)

    contours, _ = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contours_stats = [(contour, cv2.contourArea(contour), cv2.boundingRect(contour)) for contour in contours]
    
    possible_eyes = []

    for contour, area, rectangle in contours_stats:
        rect_x, rect_y, rect_width, rect_height = rectangle
        if 100 < area < 600:
            if (5/4) > (rect_width / rect_height) > (4/5):
                possible_eyes.append(contour)

    annotated = cv2.drawContours(original, possible_eyes, -1, (0, 255, 0), 3)
    
    cv2.imshow("Binary image", image)
    cv2.imshow(window_name, annotated)

def set_threshold_min(new_threshold_min):
    global threshold_min
    threshold_min = new_threshold_min

def set_threshold_max(new_threshold_max):
    global threshold_max
    threshold_max = new_threshold_max

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

threshold_min = 40
threshold_max = 255

create_kernel(5)

cv2.namedWindow(window_name)
cv2.createTrackbar("Threshold Min", window_name, threshold_min, 255, set_threshold_min)
cv2.createTrackbar("Threshold Max", window_name, threshold_max, 255, set_threshold_max)
cv2.createTrackbar("Kernel size", window_name, 2, 5, lambda x: create_kernel(x * 2 + 1))

use_video_capture()