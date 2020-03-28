import pyautogui as pg

pg.FAILSAFE = False

def move_mouse(x, y):
    pg.moveTo(x, y)

def left_click():
    pg.leftClick()

def right_click():
    pg.rightClick()

def scroll_up():
    pg.scroll(-2)
    
def scroll_down():
    pg.scroll(2)
