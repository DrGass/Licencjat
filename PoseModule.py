import cv2
import mediapipe as mp
import time
import math
import winsound
frequency = 2500  # Set Frequency To 2500 Hertz
duration = 1000  # Set Duration To 1000 ms == 1 second


class poseDetector():

    def __init__(self, mode=False, modelComplex=1, smooth=True,
                 segment=False, smoothSegment=True, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.modelComplex = modelComplex
        self.smooth = smooth
        self.segment = segment
        self.smoothSegment = smoothSegment
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.bicepCounter = 0
        self.flexCounter = 0
        self.bicepStage = "up"
        self.flexStage = "down"
        self.start = False

        self.restartList = [0] * 50
        self.startList = [300] * 50
        self.timeList = []
        self.imgCounter = 0
        self.signal = False

        now = time.localtime(time.time())
        self.createTime = str(now.tm_mday) + "." + str(now.tm_mon) + "." + str(now.tm_year)

        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(self.mode, self.modelComplex, self.smooth,
                                     self.segment, self.smoothSegment, self.detectionCon, self.trackCon)

    def findPose(self, img, draw=False):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)
        if self.results.pose_landmarks:
            if draw:
                self.mpDraw.draw_landmarks(img, self.results.pose_landmarks,
                                           self.mpPose.POSE_CONNECTIONS)
        return img

    def findPosition(self, img, draw=True):
        self.lmList = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                cx, cy, cz = int(lm.x * w), int(lm.y * h), round((lm.z * c), 3)
                self.lmList.append([id, cx, cy, cz])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        return self.lmList

    def findAngle(self, img, p1, p2, p3, draw=True, c1=0, c2=0, c3=255):

        # Get the landmarks
        x1, y1 = self.lmList[p1][1:3]
        x2, y2 = self.lmList[p2][1:3]
        x3, y3 = self.lmList[p3][1:3]

        # Calculate the Angle
        angle = math.degrees(math.atan2(y3 - y2, x3 - x2) -
                             math.atan2(y1 - y2, x1 - x2))
        if angle < 0:
            angle += 360

        if angle > 180:
            angle = 360 - angle

        # print(angle)
        # print (x1,y1, x2,y2, x3,y3)

        # Draw
        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 3)
            cv2.line(img, (x3, y3), (x2, y2), (255, 255, 255), 3)
            cv2.circle(img, (x1, y1), 10, (c1, c2, c3), cv2.FILLED)
            cv2.circle(img, (x1, y1), 15, (c1, c2, c3), 2)
            cv2.circle(img, (x2, y2), 10, (c1, c2, c3), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (c1, c2, c3), 2)
            cv2.circle(img, (x3, y3), 10, (c1, c2, c3), cv2.FILLED)
            cv2.circle(img, (x3, y3), 15, (c1, c2, c3), 2)
            cv2.putText(img, str(int(angle)), (x2 - 50, y2 + 50),
                        cv2.FONT_HERSHEY_PLAIN, 2, (c1, c2, c3), 2)
        return angle

    def checkBow(self, img, draw=True):

        if self.lmList[11][3] >= self.lmList[12][3]:
            side = "right"
            # coordinates of wrist and foot
            x1, y1 = self.lmList[15][1:3]
            x2, y2 = self.lmList[31][1:3]
            x3, y3 = self.lmList[23][1:3]


        else:
            side = "left"
            # coordinates of wrist and foot
            x1, y1 = self.lmList[14][1:3]
            x2, y2 = self.lmList[32][1:3]
            x3, y3 = self.lmList[24][1:3]

        percentage = round(1 - ((y1 - y2) / (y3 - y2)), 2) * 100
        # print(percentage)
        if draw is True and percentage >= 50:
            cv2.putText(img, f"{str(percentage)}%", (x1 - 50, y1 + 50),
                        cv2.FONT_HERSHEY_PLAIN, 5, (0, 0, 255), 2)

            return percentage

    def checkCurl(self, img, draw=True, side="right"):

        if self.lmList[11][3] > self.lmList[12][3]:
            side = "right"
            # coordinates of wrist and foot
            angle = self.findAngle(img, 12, 14, 16)

        else:
            side = "left"
            # coordinates of wrist and foot
            angle = self.findAngle(img, 11, 13, 15)

        # start
        if self.bicepCounter == 0 and self.bicepStage == "up":
            cv2.putText(img, "Please straighten your arm", (100, 360),
                        cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

        # check curl
        if angle > 160 and self.signal:
            self.bicepStage = "down"
            self.signal = False
        if angle < 50 and self.bicepStage == "down" and self.signal:
            self.signal = False
            self.bicepStage = "up"
            self.bicepCounter += 1

        if draw:
            cv2.putText(img, str(self.bicepCounter), (10, 40),
                        cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 2)

        return angle

    def curlRestart(self):
        self.bicepCounter = 0

    def checkKnee(self, img, draw=True):
        if self.lmList[11][3] < self.lmList[12][3]:

            side = "right"
            pelvisAngle = self.findAngle(img, 11, 23, 25)
            if 94 > pelvisAngle > 84:
                pelvisAngle = self.findAngle(img, 11, 23, 25, c1=0, c2=255, c3=0)

            kneeAngle = self.findAngle(img, 23, 25, 27)
            if 94 > kneeAngle > 84:
                kneeAngle = self.findAngle(img, 23, 25, 27, c1=0, c2=255, c3=0)
        else:
            side = "left"
            pelvisAngle = self.findAngle(img, 12, 24, 26)
            if 94 > pelvisAngle > 84:
                pelvisAngle = self.findAngle(img, 12, 24, 26, c1=0, c2=255, c3=0)

            kneeAngle = self.findAngle(img, 24, 26, 28)
            if 94 > kneeAngle > 84:
                kneeAngle = self.findAngle(img, 24, 26, 28, c1=0, c2=255, c3=0)

        if self.signal and kneeAngle > 140 and self.flexCounter != 0 and self.signal:
            self.flexStage = "down"
            self.signal = False

        if self.signal and kneeAngle < 110 and self.flexStage == "down" and self.signal:
            self.flexStage = "up"
            self.flexCounter += 1
            self.signal = False

        if draw:
            cv2.putText(img, str(self.flexCounter), (10, 40),
                        cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 2)

        return pelvisAngle, kneeAngle

    def restartMove(self):
        if (self.restartList[48] - self.restartList[0]) > 300:
            self.bicepCounter = 0
            self.flexCounter = 0
        if len(self.restartList) == 50:
            del self.restartList[0]
        self.restartList.append(self.lmList[16][1])

    def startMove(self):
        if len(self.startList) == 50:
            if (self.startList[48] - self.startList[0]) > 300:
                self.start = True
            del self.startList[0]
        self.startList.append(self.lmList[15][1])

    def timeCheck(self, angle, img, excercise):
        self.timeList.append([angle, time.time()])
        if time.time() - self.timeList[0][1] > 2.0 \
                and angle + 4 > self.timeList[0][0] > angle - 4 \
                and self.signal == False:
            cv2.imwrite(excercise + "/" + self.createTime + "/" + excercise + str(self.imgCounter) + ".png", img)
            print("added screen")
            self.timeList.clear()
            self.timeList.append([angle, time.time()])
            self.imgCounter += 1
            if cv2.getWindowProperty('image', cv2.WND_PROP_VISIBLE) > 1:
                cv2.destroyWindow("image")
            self.signal = True

        if len(self.timeList) > 60:
            del self.timeList[0]


def main():
    cap = cv2.VideoCapture(0)
    pTime = 0
    detector = poseDetector()
    while True:
        success, img = cap.read()
        img = detector.findPose(img)
        lmList = detector.findPosition(img, draw=False)
        if len(lmList) != 0:
            # print(lmList[14])
            cv2.circle(img, (lmList[14][1], lmList[14][2]), 15, (0, 0, 255), cv2.FILLED)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 0), 3)

        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
