import random
from builtins import int

import cv2
import mediapipe as mp
import time

import numpy as np


class handDetector:
    def __init__(self, mode=False, maxHands=1, complexity=1, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.complexity = complexity
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.complexity,
                                        self.detectionCon, self.trackCon, )
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=False):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)

        return img

    def findFinger(self, img):
        min_x = 0
        min_y = 0
        min_id = -1
        h, w, c = img.shape
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                arr_fingers = []

                for id, lm in enumerate(handLms.landmark):

                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    if id in range(4, 21, 4):
                        arr_fingers.append([cy, cx, id])

            min_x = min(arr_fingers)[1]
            min_y = min(arr_fingers)[0]
            min_id = min(arr_fingers)[2]

        cv2.circle(img, (min_x, min_y), 7, (255, 255, 42), cv2.FILLED)

        return min_id




    def drawByID(self, img, fingID):
        cx = -50
        cy = -50

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                for id, lm in enumerate(handLms.landmark):
                    if id == fingID:
                        h, w, c = img.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)


        return cx, cy


def main():
    pTime = 0
    cTime = 0
    timer = 0
    cap = cv2.VideoCapture(0)
    w = cap.get(3)
    h = cap.get(4)
    rat = 1
    cap.set(3, w*rat)
    cap.set(4, h*rat)

    detector = handDetector()
    prev_finger = -2

    while True:
        success, img = cap.read()
        img = detector.findHands(img)

        if timer <= 3:
            finger_id = detector.findFinger(img)
            if finger_id != -1:
                timer += 0.03
            if finger_id != prev_finger:
                prev_finger = finger_id
                timer = 0
            cv2.putText(img, str(f"Raise the finger you want for 3 seconds: {int(timer)}"), (5, 35),
                        cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 1)
        else:
            detector.drawByID(img, finger_id)


        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (5, 15), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)

        img = cv2.flip(img, 1)
        cv2.imshow("Image", img)

        cv2.waitKey(1)


if __name__ == "__main__":
    main()
