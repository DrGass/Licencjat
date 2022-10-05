import cv2
import tkinter as tk
from PIL import Image
from PIL import ImageTk
import PoseModule as pm
import time
import dirCreator as dc

dc.dirCreator()

# Set up GUI
window = tk.Tk()  # Makes main window
window.wm_title("Pomocnik Fizjoterapeuty")
window.config(background="#4287f5")

VShift = "+" + str(window.winfo_screenheight() // 2 - 690 // 2)
HShift = "+" + str(window.winfo_screenwidth() // 2 - 665 // 2)
windowShift = HShift + VShift
window.geometry(f"665x690{windowShift}")

print((window.winfo_screenheight()) // 2 - 665 // 2)
print((window.winfo_screenwidth()) // 2 - 690 // 2)

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
           ("Knee", "Knee"),
           ("Bow", "Bow"),
           ("Bicep", "Bicep")
           )
# Warning label
warning = tk.Label(text="", font=("Courier Bold", 20), fg="red", width=40)
warning.grid(row=0, column=0, padx=0, pady=2)

# Choosing label
excInfo = tk.Label(text="Choose Your Excercise", font=("Courier Bold", 15))
excInfo.grid(row=2, column=0, padx=10, pady=2, sticky="W")

# counter label
excCounter = tk.Label(text="Reps: ", font=("Courier Bold", 12), width=8)
excCounter.grid(row=3, column=0, padx=223, pady=3, sticky="W")

# excercise counter labels
kneeLabel = tk.Label(text=detector.flexCounter, font=("Courier Bold", 12), width=10)
kneeLabel.grid(row=4, column=0, padx=223, pady=3, sticky="W")

BowLabel = tk.Label(text="0", font=("Courier Bold", 12), width=10)
BowLabel.grid(row=5, column=0, padx=223, pady=3, sticky="W")

bicepLabel = tk.Label(text=detector.bicepCounter, font=("Courier Bold", 12), width=10)
bicepLabel.grid(row=6, column=0, padx=223, pady=3, sticky="W")
excImg = ""
# creating radio buttons
count = 3
for excercise in options:
    r = tk.Radiobutton(
        window,
        text=excercise[0],
        value=excercise[1],
        variable=selected_option,
        width=26
    )
    r.grid(row=count, column=0, padx=10, pady=2, sticky="W")

    # neutral as default
    if count == 3:
        r.invoke()
    count += 1


# choosing button
# button = tk.Button(
#     window,
#     text="Bicep bicepCounter reset",
#     command=detector.curlRestart)
# button.grid(row=count, column=0, padx=50, pady=2)

def showImage(excImg):
    img = cv2.imread(excImg)
    cv2.imshow("image", img)
    cv2.moveWindow("image", int(HShift) + 665, int(VShift))


def show_frame():
    successCam, camImg = cap.read()
    camImg = detector.findPose(camImg, draw=True)
    lmList = detector.findPosition(camImg, draw=True)

    if len(lmList) != 0:
        detector.startMove()
        # print(detector.start, detector.startList)
        if detector.start:
            if selected_option.get() == "Bow":
                percentage = detector.checkBow(camImg, draw=True)
                warning.configure(text="Wykonaj skłon prosty")
                if cv2.getWindowProperty('image', cv2.WND_PROP_VISIBLE) >= 1:
                    cv2.destroyWindow("image")

            elif selected_option.get() == "Bicep":
                bAngle = detector.checkCurl(camImg, draw=True)
                detector.timeCheck(bAngle, camImg, selected_option.get())

                bicepLabel.configure(text=detector.bicepCounter)
                if detector.bicepStage == "up":
                    excImg = "images/biceps_curl_down.jpg"
                    showImage(excImg)
                    warning.configure(text="Wyprostuj rękę")
                else:
                    excImg = "images/biceps_curl_up.jpg"
                    showImage(excImg)
                    warning.configure(text="Zegnij rękę")

            elif selected_option.get() == "Knee":
                pAngle, kAngle = detector.checkKnee(camImg)
                kneeLabel.configure(text=detector.flexCounter)
                detector.timeCheck(kAngle, camImg, selected_option.get())

                warning.configure(text="Opuść nogę w dół")

                if detector.flexStage == "up":
                    excImg = "images/Knee_flexion.jpg"
                    showImage(excImg)
                    warning.configure(text="Opuść nogę w dół")
                else:
                    excImg = "images/Knee_flexion_up.jpg"
                    showImage(excImg)
                    warning.configure(text="Unieś nogę do góry")
                # print(detector.signal)

            elif selected_option.get() == "Neutral":
                if cv2.getWindowProperty('image', cv2.WND_PROP_VISIBLE) >= 1:
                    cv2.destroyWindow("image")
                warning.configure(text="Przed startem zasłoń źródła światła")
                # print(lmList[16][1])
        else:
            warning.configure(text="Aby zacząć przesuń lewą rękę z prawej do lewej")

        detector.restartMove()

    cv2image = cv2.cvtColor(camImg, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(1, show_frame)


show_frame()  # Display 2
window.mainloop()  # Starts GUI
# menu.mainloop()
