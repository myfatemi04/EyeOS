from calibration import Calibrator
from threading import Thread
from playsound import playsound
import track
import time, os, pyautogui as pg

calibrator = Calibrator()
trackThread = Thread(target=track.loop)

trackThread.start()

while not track.thresholdCalibrated:
    pass

print("Remembering minX and minY in 5 seconds")
time.sleep(2)
playsound("success.mp3")
minX = track.eyeX
minY = track.eyeY

print("Remembering maxX and maxY in 5 seconds")
time.sleep(2)
playsound("success.mp3")
maxX = track.eyeX
maxY = track.eyeY

print(minX, minY, maxX, maxY)

calibrator.calibrate(minX, maxX, minY, maxY)

while True:
    print(calibrator.transform(track.eyeX, track.eyeY), (track.eyeX, track.eyeY))
