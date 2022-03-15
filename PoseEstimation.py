import cv2
import time
import PoseModule as pm


def main():
    wCam, hCam = 1280, 720
    ###############################
    # Dance Video
    # cap = cv2.VideoCapture("Roy Purdy.mp4")

    # Camera
    cap2 = cv2.VideoCapture(0)
    ###############################

    # print(cap.get(3))
    # print(cap.get(4))
    #
    cap2.set(cv2.CAP_PROP_FRAME_WIDTH, wCam)
    cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, hCam)

    pTime = 0
    detector = pm.poseDetector()

    while True:
        # success, img = cap.read()

        # resizing
        # img = cv2.resize(img,(1280,720),interpolation=cv2.INTER_AREA)
        # img = detector.findPose(img)

        successCam, camImg = cap2.read()
        camImg = detector.findPose(camImg, draw=True)
        # side = "no person"

        lmList = detector.findPosition(camImg, draw=True)
        if len(lmList) != 0:
            # angle = detector.findAngle(camImg, 12, 14, 16)

            # percentage = detector.checkBow(camImg)

            bicepsCounter = detector.checkCurl(camImg)

            # for lm in lmList:
            #

            # print(lmList[14])
            # cv2.circle(img, (lmList[14][1], lmList[14][2]), 15, (0, 0, 255), cv2.FILLED)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(camImg, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 0), 3)

        # cv2.imshow("Image", img)
        cv2.imshow("Camera", camImg)
        cv2.waitKey(1)

        # cv2.destroyWindow(img)


if __name__ == "__main__":
    main()
