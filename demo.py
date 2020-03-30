import tkinter as tk


def one():
    print("EyeOS is very innovative.")

def two():
    print("EyeOS is helpful to impaired individuals who cannot use a computer.")

def three():
    print("EyeOS makes me nut.")

def four():
    print("EyeOS is also extremely useful to those who do not want to use their hands on their computer.")

root = tk.Tk()
frame = tk.Frame(root)
frame.pack()

button = tk.Button(frame,
                   text="QUIT",
                   fg="red",
                   command=quit,
                   width=20,
                   height=20)
button.pack(side=tk.LEFT)


b1 = tk.Button(frame,
                   text="Button 1",
                   command=one,
                   width=20,
                   height=20,
                   fg="green")
b1.pack(side=tk.LEFT)

b2 = tk.Button(frame,
                   text="Button 2",
                   command=two,
                   width=20,
                   height=20,
                   fg="blue")
b2.pack(side=tk.LEFT)

b3 = tk.Button(frame,
                   text="Button 3 ;)",
                   command=three,
                   width=20,
                   height=20,
                   fg="yellow")
b3.pack(side=tk.LEFT)

b4 = tk.Button(frame,
                   text="Button 4",
                   command=four,
                   width=20,
                   height=20,
                   fg="cyan")
b4.pack(side=tk.LEFT)

root.mainloop()
