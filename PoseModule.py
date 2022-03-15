import cv2
import mediapipe as mp
import time
import math


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
        self.counter = 0
        self.stage = "up"

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
                # print(id, lm)
                cx, cy, cz = int(lm.x * w), int(lm.y * h), round((lm.z * c), 3)
                self.lmList.append([id, cx, cy, cz])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        return self.lmList

    def findAngle(self, img, p1, p2, p3, draw=True):

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

        # Draw
        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 3)
            cv2.line(img, (x3, y3), (x2, y2), (255, 255, 255), 3)
            cv2.circle(img, (x1, y1), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x1, y1), 15, (0, 0, 255), 2)
            cv2.circle(img, (x2, y2), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (0, 0, 255), 2)
            cv2.circle(img, (x3, y3), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x3, y3), 15, (0, 0, 255), 2)
            cv2.putText(img, str(int(angle)), (x2 - 50, y2 + 50),
                        cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
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

        percentage = round(1-((y1-y2) / (y3-y2)), 2) * 100
        print(percentage)
        if draw is True and percentage >= 50:
            cv2.putText(img, f"{str(percentage)}%", (x1 - 50, y1 + 50),
                        cv2.FONT_HERSHEY_PLAIN, 5, (0, 0, 255), 2)

            return percentage

    def checkCurl(self, img, draw=True, side="right"):

        if self.lmList[11][3] > self.lmList[12][3]:
            side = "right"
            angle = self.findAngle(img, 12, 14, 16)

        else:
            side = "left"
            # coordinates of wrist and foot
            angle = self.findAngle(img, 11, 13, 15)

        # start
        if self.counter == 0 and self.stage == "up":
            cv2.putText(img, "Please straighten your arm", (100, 250),
                        cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

        # check curl

        if angle > 160:
            self.stage = "down"
        if angle < 50 and self.stage == "down":
            self.stage = "up"
            self.counter += 1
        print(angle, self.stage)

        if draw:
            cv2.putText(img, str(self.counter), (350, 100),
                        cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 2)
        return self.counter

    def curlRestart(self):
        self.counter = 0


def main():
    cap = cv2.VideoCapture(0)
    pTime = 0
    detector = poseDetector()
    while True:
        success, img = cap.read()
        img = detector.findPose(img)
        lmList = detector.findPosition(img, draw=False)
        if len(lmList) != 0:
            print(lmList[14])
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
