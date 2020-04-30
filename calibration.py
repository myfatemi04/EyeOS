class Calibrator:
    def __init__(self, left, right, top, bottom, screen_left, screen_right, screen_bottom, screen_top):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom
        self.width = right - left
        self.height = bottom - top

        self.screen_left = screen_left
        self.screen_right = screen_right
        self.screen_bottom = screen_bottom
        self.screen_top = screen_top
        self.screen_width = screen_right - screen_left
        self.screen_height = screen_bottom - screen_top

    # fits the given position to the screen based on the calibrated values
    def transform(self, x, y):
        width_prop = (x - self.left)/self.width
        height_prop = (y - self.top)/self.height

        return width_prop * self.screen_width + self.screen_left, height_prop * self.screen_height + self.screen_top

