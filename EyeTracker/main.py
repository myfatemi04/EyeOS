import pyautogui as pg
import time
from threading import Thread
# import speech
import settings
from playsound import playsound
import sys

import cv2
from eye_tracking import FaceTracker

### Doesn't stop the program when you look at the corner
pg.FAILSAFE = False

# fits the given position to the screen based on the calibrated values
def transform_pos(pos, left, right, top, bottom, screen_left, screen_right, screen_bottom, screen_top):
	x, y = pos
	width = right - left
	screen_width = screen_right - screen_left
	height = bottom - top
	screen_height = screen_bottom - screen_top
	
	width_prop = (x - left)/width
	height_prop = (y - top)/height

	return width_prop * screen_width + screen_left, height_prop * screen_height + screen_top

def run_main():
	# eye calibrations
	left = right = bottom = top = None
	
	# used for eye calibration averages
	left_sum = right_sum = top_sum = bottom_sum = 0

	# groups cursor positions together to make the cursor more steady
	position_group = []

	# used to scale up calibrations
	screen_left, screen_top = (0, 0)
	screen_right, screen_bottom = pg.size()

	# used for nose calibrations
	nose_center_x = nose_center_y = None
	nose_x_move = nose_y_move = None
	nose_x_dists = []
	nose_y_dists = []

	# initialize the trackers
	face_tracker = FaceTracker()

	# load video footage
	cap = cv2.VideoCapture(0)

	# keep track of frame number
	frame_number = 0

	countdown_start = 0

	# infinite loop until "exit"
	while settings.tracker_active:
		frame_number += 1
		
		### load the trackers
		_, frame = cap.read()
		face_tracker.refresh(frame.copy())
		
		# draw on the frame
		frame = face_tracker.annotated_frame()
		cv2.imshow("EyeOS Tracker", frame)

		if True:
			if settings.mode == 'eye':  ### EYE TRACKING ###
				if frame_number % 100 == 0:
					face_tracker.calibration.recalibrate()

				if face_tracker.found_eyes():
					# find the offset of the pupils
					pos = face_tracker.get_average_eye_offset(mode=settings.eye_trace_mode)
				
					if settings.is_calibrated:
						if settings.movement_mode == "cursor":
							if settings.eye_pos_mode == "absolute":
								## absolute positioning
								## estimates where you're looking on screen
								tpos = transform_pos(
									pos,
									left,
									right,
									top,
									bottom,
									screen_left,
									screen_right,
									screen_bottom,
									screen_top
								)

								position_group.append(tpos)

								# stabilization
								if len(position_group) >= settings.mouse_stabilization:
									x_sum = 0
									y_sum = 0
									for x, y in position_group:
										x_sum += x
										y_sum += y
									x_avg = (x_sum/len(position_group))
									y_avg = (y_sum/len(position_group))

									pg.moveTo(x_avg, y_avg)

									position_group.clear()

							elif settings.eye_pos_mode == "relative":
								## relative positioning
								## moves in 45-px increments
								if pos[0] < left//2: pg.moveRel(-45, 0)
								elif pos[0] > right//2: pg.moveRel(45, 0)
								
								if pos[1] > top: pg.moveRel(0, -45)
								elif pos[1] < bottom: pg.moveRel(0, 45)
						elif settings.eye_pos_mode == "scroll":
							if pos[0] < left//2: pg.hscroll(-45)
							elif pos[0] > right//2: pg.hscroll(45)
							
							if pos[1] > top: pg.vscroll(-45)
							elif pos[1] < bottom: pg.vscroll(45)

				if not settings.is_calibrated:
					for corner in settings.has:
						if not settings.has[corner]:
							# tell the user what to do
							if not settings.msg[corner]:
								settings.msg[corner] = True
								print("Look at the", corner, "corner.")
								# playsound('sounds/countdown.mp3') # play a countdown sound
								countdown_start = time.perf_counter()
							elif time.perf_counter() - countdown_start > 5:
								pos_x, pos_y = pos

								if 'left' in corner:
									left_sum += pos_x
								elif 'right' in corner:
									right_sum += pos_x
								
								if 'top' in corner:
									top_sum += pos_y
								elif 'bottom' in corner:
									bottom_sum += pos_y

								settings.has[corner] = True

								# playsound('sounds/success.mp3')
							break
					if all(settings.has.values()):
						print("Finished calibrating")
						settings.is_calibrated = True
						left = left_sum/2
						right = right_sum/2
						top = top_sum/2
						bottom = bottom_sum/2

						# clear the variables for the next time
						left_sum = right_sum = top_sum = bottom_sum = 0
			
			elif settings.mode == "nose":  #### NOSE TRACKING ####
				if face_tracker.landmarks:
					nose_x, nose_y = face_tracker.find_nose()

					if settings.is_calibrated:
						nose_offset_x = nose_x - nose_center_x
						nose_offset_y = nose_y - nose_center_y

						if settings.movement_mode == 'cursor':
							# scale the nose position to the screen
							relative_pos = transform_pos(
								(nose_offset_x, nose_offset_y),
								nose_x_move,
								-nose_x_move,
								-nose_y_move,
								nose_y_move,
								screen_left,
								screen_right,
								screen_bottom,
								screen_top
							)

							position_group.append(relative_pos)

							# stabilization
							if len(position_group) >= settings.mouse_stabilization:
								x_sum = 0
								y_sum = 0
								for x, y in position_group:
									x_sum += x
									y_sum += y
								x_avg = x_sum / len(position_group)
								y_avg = y_sum / len(position_group)

								pg.moveTo(x_avg, y_avg)

								position_group.clear()

						elif settings.movement_mode == 'scroll':
							# scroll in the requested direction
							if abs(nose_offset_x) > 20:
								pg.hscroll(nose_offset_x)
							if abs(nose_offset_y) > 20:
								pg.vscroll(-nose_offset_y)

					else: # it's not calibrated
						if not settings.has_nose_center:
							# tell the user what to do
							if not settings.msg_nose_center:
								print("Center your nose on the screen.")

								settings.msg_nose_center = True
								playsound('sounds/countdown.mp3') # play a countdown sound
								countdown_start = time.perf_counter()

							elif time.perf_counter() - countdown_start > 5:
								nose_center_x, nose_center_y = nose_x, nose_y
								
								settings.said_ready = False
								settings.has_nose_center = True

								playsound('sounds/success.mp3')

						elif not settings.has_nose_move:
							# tell the user what to do
							if not settings.msg_nose_move:
								print("Move your nose around a little bit")
								settings.msg_nose_move = True

							# wait to collect sample data based on nose position
							if len(nose_x_dists) < 100 and len(nose_y_dists) < 100:
									nose_dist = 0
									if nose_center_x and nose_center_y:
										nose_dist = ((nose_x - nose_center_x) ** 2 + (nose_y - nose_center_y) ** 2) ** 0.5

									if nose_dist > 20:
										nose_x_dists.append(nose_center_x - nose_x)
										nose_y_dists.append(nose_center_y - nose_y)
							else:
								max_x_dist = max(nose_x_dists)
								nose_x_move = max_x_dist * 1.5

								max_y_dist = max(nose_y_dists)
								nose_y_move = max_y_dist * 1.5
								settings.has_nose_move = True

								print("Nose calibration fit to a", (nose_x_move * 2), "x", (nose_y_move * 2), "box")
								playsound('sounds/success.mp3')
						else:
							settings.is_calibrated = True

							# clear the storage for next time
							nose_x_dists = []
							nose_y_dists = []
						

		# option to exit by pressing Q
		if cv2.waitKey(1) & 0xFF == ord('q'):
			settings.tracker_active = False
			settings.sst_active = False
			break

	cap.release()

# these methods are for use by external applications
# mode = 'eye' or 'nose'
def start_tracker(mode):
	settings.tracker_active = True
	settings.recalibrate()
	settings.mode = mode
	settings.main_thread = Thread(target=run_main, name="Main tracker")
	settings.main_thread.start()

def stop_tracker():
	settings.tracker_active = False
	settings.main_thread.join()
	
def start_speech_to_text():
	# settings.sst_active = True
	# speech_thread = Thread(target=speech.speech_to_text, name="speech_to_text", daemon=False)
	# speech_thread.start()
	pass

if __name__ == "__main__":
	print("Booting EyeOS")

	if len(sys.argv) > 1:
		settings.typing_on = sys.argv[1] != "notyping"
		print("Typing: ", settings.typing_on)
	if len(sys.argv) > 2:
		settings.launcher_on = sys.argv[2] != "launcher"
		print("App launcher: ", settings.launcher_on)

	print("To turn on eye tracking or nose tracking, say \"eye mode\" or \"nose mode\".")
	
	# start_speech_to_text()
	start_tracker('eye')

