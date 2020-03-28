import pyautogui as pg

pg.FAILSAFE = False

def move_mouse(x, y):
    pg.moveTo(x, y, 0.05, pg.easeInOutQuad)

def left_click():
    pg.leftClick()

def right_click():
    pg.rightClick()


