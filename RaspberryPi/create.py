import numpy as np

def create_camera_matrix(focal_x=1, focal_y=1, center_x=64, center_y=64):
    return np.array([
        [focal_x,      0, center_x],
        [0,      focal_y, center_y],
        [0,            0,        1]
    ])

# Given width and height, returns points of rectangle with that width/height
def create_target_points(width, height):
    return np.float32([[0, 0], [width, 0], [width, height], [0, height]])

def create_kernel(kernel_size, mode='vertical'):
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

    return kernel