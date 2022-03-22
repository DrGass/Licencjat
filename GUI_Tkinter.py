import numpy as np
import cv2
import tkinter as tk
from PIL import Image
from PIL import ImageTk
import PoseModule as pm
import time

# Set up GUI
window = tk.Tk()  # Makes main window
window.wm_title("Pomocnik fizjoterapeuty")
window.config(background="#FFFFFF")

# Graphics window
imageFrame = tk.Frame(window, width=600, height=500)
imageFrame.grid(row=1, column=0, padx=10, pady=2)

# Capture video frames
lmain = tk.Label(imageFrame)
lmain.grid(row=1, column=0)
cap = cv2.VideoCapture(0)
pTime = 0

detector = pm.poseDetector()

selected_option = tk.StringVar()
options = (("Neutral", "Neutral"),
           ("Knee Flex", "Knee Flex"),
           ("Bow", "Bow"),
           ("Bicep", "Bicep")
           )
# Warning grid
warning = tk.Label(text="",font=("Courier Bold",20),fg="red")
warning.grid(row=0, column=0, padx=0, pady=2)

# text grid
excInfo = tk.Label(text="Choose Your Excercise",font=("Courier Bold",15))
excInfo.grid(row=2, column=0, padx=0, pady=2)

# creating radio buttons
count = 3
for excercise in options:
    r = tk.Radiobutton(
        window,
        text=excercise[0],
        value=excercise[1],
        variable=selected_option,
    )
    r.grid(row=count, column=0, padx=0, pady=2)
    if count == 3:
        r.invoke()
    count += 1


# choosing button
button = tk.Button(
    window,
    text="Bicep counter reset",
    command=detector.curlRestart)
button.grid(row=count, column=0, padx=50, pady=2)


def show_frame():
    successCam, camImg = cap.read()
    camImg = detector.findPose(camImg, draw=False)
    lmList = detector.findPosition(camImg, draw=False)

    if len(lmList) != 0:
        warning.configure(text="You're doing " + str(selected_option.get()))
        if selected_option.get() == "Bow":
            percentage = detector.checkBow(camImg, draw=True)
            detector.counter = 0
        elif selected_option.get() == "Bicep":
            bicepsCounter = detector.checkCurl(camImg, draw=True)
        elif selected_option.get() == "Knee Flex":
            detector.checkKnee(camImg)
        elif selected_option.get() == "Neutral":
            detector.counter = 0

    cv2image = cv2.cvtColor(camImg, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(1, show_frame)


# Slider window (slider controls stage position)
# sliderFrame = tk.Frame(window, width=600, height=100)
# sliderFrame.grid(row=600, column=0, padx=10, pady=2)

show_frame()  # Display 2
window.mainloop()  # Starts GUI
