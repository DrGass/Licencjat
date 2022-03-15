import time

import PySimpleGUI as sg
import cv2
import numpy as np
import PoseModule as pm


def main():
    sg.theme("Green")

    # Define the window layout
    layout = [
        [sg.Text("OpenCV Demo", size=(60, 1), justification="center")],
        [sg.Image(filename="", key="-IMAGE-")],
        [sg.Radio("None", "Radio", True, size=(10, 1))],
        [sg.Radio("Biceps", "Radio", size=(10, 1), key="-BICEP-"),
         sg.Button("Restart", size=(10,1))],
        [sg.Radio("Skłony", "Radio", size=(10, 1), key="-BOW-")],
        [sg.Button("Exit", size=(10, 1))]
    ]

    # Create the window and show it without the plot
    window = sg.Window("OpenCV Integration", layout, location=(800, 400))

    cap = cv2.VideoCapture(1)
    pTime = 0
    detector = pm.poseDetector()

    while True:
        event, values = window.read(timeout=20)
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        elif event == "Restart":
            detector.curlRestart()

        successCam, camImg = cap.read()
        camImg = detector.findPose(camImg, draw=True)
        # side = "no person"

        lmList = detector.findPosition(camImg, draw=True)
        if len(lmList) != 0:
            # angle = detector.findAngle(camImg, 12, 14, 16)
            if values["-BOW-"]:
                percentage = detector.checkBow(camImg)
            elif values["-BICEP-"]:
                bicepsCounter = detector.checkCurl(camImg)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        fpsShow = cv2.putText(camImg, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                              (255, 0, 0), 3)

        imgbytes = cv2.imencode(".png", camImg)[1].tobytes()
        window["-IMAGE-"].update(data=imgbytes)

    window.close()


if __name__ == "__main__":
    main()