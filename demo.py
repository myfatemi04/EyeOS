import tkinter as tk
import time
from threading import Thread

picked_button = None
def one():
	global picked_button
	picked_button = 1

def two():
	global picked_button
	picked_button = 2
	
def three():
	global picked_button
	picked_button = 3
	
def four():
	global picked_button
	picked_button = 4
	
root = tk.Tk()
root.geometry("1280x720")
root.title("EyeOS Demo")

demo_label = tk.Label(root, text="Demo", font=("Courier", 20))
demo_label.pack(side='top')

frame = tk.Frame(root)
frame.pack(side='top')

button = tk.Button(frame,
				   text="QUIT",
				   fg="red",
				   command=quit,
				   width=15,
				   height=20)
button.config(font=("Courier", 20))
button.pack(side='left')

b1 = tk.Button(frame,
				   text="Button 1",
				   command=one,
				   width=15,
				   height=20,
				   fg="green")
b1.config(font=("Courier", 20))
b1.pack(side='left')

b2 = tk.Button(frame,
				   text="Button 2",
				   command=two,
				   width=15,
				   height=20,
				   fg="blue")
b2.config(font=("Courier", 20))
b2.pack(side='left')

b3 = tk.Button(frame,
				   text="Button 3 ;)",
				   command=three,
				   width=15,
				   height=20,
				   fg="black")
b3.config(font=("Courier", 20))
b3.pack(side='left')

b4 = tk.Button(frame,
					text="Button 4",
					command=four,
					width=15,
					height=20,
					fg="purple")
b4.config(font=("Courier", 20))
b4.pack(side='left')

bottom_frame = tk.Frame(root)
label = tk.Label(bottom_frame, text="Hello")
label.config(font=("Courier", 44))
label.pack(side='top')
bottom_frame.pack(side='bottom')

current_button = 1

def logic_loop():
	global current_button, picked_button
	while True:
		current_button += 1
		label.config(text=f"Click button {current_button % 4 + 1}")
		
		while not picked_button:
			time.sleep(0.5)
			
		if picked_button == current_button % 4 + 1:
			label.config(text="You clicked the right button!")
		else:
			label.config(text="Incorrect button")
		
		picked_button = None
		
		time.sleep(3)
			
logic_thread = Thread(target=logic_loop, daemon=True)
logic_thread.start()

root.mainloop()
