import math
import random
import time

import cv2
import HandTrackingModule as htm


def randomMaze(cap):
    w, h = int(cap.get(3)), int(cap.get(4))

    lines = []

    lastPosition = 3

    endX = w - w // 11
    endY = int(h - h // 1.2) + int(h) // 8
    x2 = 0
    y2 = 0

    sumOfWidth = 0

    while sumOfWidth < w - 75:
        position = random.randint(1, 3)  # 1 up #2 down #3 left
        const_w = random.randint(10, 70)
        const_h = random.randint(15, 55)

        if lastPosition == 3:
            if abs(endY - h) > h - 80:
                position = 2
            elif abs(endY) < 80:
                position = 1
            else:
                position = random.randint(1, 3)
        elif lastPosition == 1 or 2:
            position = 3

        if position == 1:
            preX2 = endX
            preY2 = endY
            x2 = preX2
            y2 = preY2 - const_h
            lines.append((preX2, preY2, x2, y2))
        elif position == 2:
            preX2 = endX
            preY2 = endY
            x2 = preX2
            y2 = preY2 + const_h
            lines.append((preX2, preY2, x2, y2))
        elif position == 3:
            preX2 = endX
            preY2 = endY
            x2 = preX2 - const_w
            y2 = preY2
            lines.append((preX2, preY2, x2, y2))
            sumOfWidth += preX2 - x2

        endX = x2
        endY = y2

        lastPosition = position

    startPoint = []
    startPoint.append(lines[0])
    endPoint = []
    endPoint.append(lines[len(lines) - 1])
    return lines, startPoint, endPoint

def drawMaze(img, lines):
    for i, vector in enumerate(lines):
        x1, y1, x2, y2 = vector[0], vector[1], vector[2], vector[3]
        if i == 0:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 7, cv2.LINE_AA)
        elif i == len(lines) - 1:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 7, cv2.LINE_AA)
        else:
            cv2.line(img, (x1, y1), (x2, y2), (0, 0, 0), 7, cv2.LINE_AA)

class Point(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y

def collisonFinger(finger, lines):
    for i, vector in enumerate(lines):
        x1, y1, x2, y2 = vector[0], vector[1], vector[2], vector[3]
        x, y = finger
        horizontal = abs(x2 - x1)
        if horizontal != 0:
            # print("horizontal")
            if x1 > x2:
                left_x = x1
                right_x = x2
            else:
                left_x = x2
                right_x = x1
            if left_x + 10 > x > right_x - 10 and y1 - 16 < y < y1 + 16:
                return True
        else:
            # print("vertical")
            if y1 > y2:
                high_y = y1
                down_y = y2
            else:
                high_y = y2
                down_y = y1
            if down_y - 10 < y < high_y + 10 and x1 - 14 < x < x1 + 14:
                return True

    return False

def chooseFinger(img, detector, timer, finger_id, prev_finger):
    if timer <= 2:
        finger_id = detector.findFinger(img)
        if finger_id != prev_finger:
            prev_finger = finger_id
            timer = 0
        if finger_id == -1:
            timer = 0
            text(img, "Unidentified finger", (5, 56), 1.3)
        text(img, f"Raise only one finger you want for 2 seconds: {int(timer)}", (5, 35), 1.3)



    else:
        return finger_id, prev_finger, timer, img, True
    return finger_id, prev_finger, timer, img, False

def text(img, str, point, size):
    cv2.putText(img, str, point,
                cv2.FONT_HERSHEY_PLAIN, size, (0, 0, 0), 1, cv2.LINE_AA)

def main():
    # Camera settings:
    cap = cv2.VideoCapture(0)
    w = cap.get(3)
    h = cap.get(4)
    rat = 1
    cap.set(3, w * rat)
    cap.set(4, h * rat)

    prev_finger = -2
    finger_id = -1
    d_finger = htm.handDetector()
    time_sec = 0
    conditionStart = False
    onMaze = False
    doRandomMaze = True
    # linesToDraw = []
    timingForStart = 0
    finger = 0, 0
    timer = 0
    colorForStart = 0
    points = 0

    while True:
        start = time.time()

        success, img = cap.read()
        img = cv2.flip(img, 1)
        img = d_finger.findHands(img)
        cv2.rectangle(img, (0, 0), (int(w), int(h) // 8), (255, 255, 255), -1)

        if conditionStart is not True:
            finger_id, prev_finger, time_sec, img, conditionStart = chooseFinger(img, d_finger, time_sec, finger_id,
                                                                                 prev_finger)
        else:
            finger = d_finger.drawByID(img, finger_id)
            if ((doRandomMaze and int(time_sec) % 4 == 0)):
                timer += 1
                lines, startPoint, endPoint = randomMaze(cap)
                onMaze = True
                doRandomMaze = False
                time_sec = 0
            if onMaze:
                drawMaze(img, lines)
                if collisonFinger(finger, startPoint) is not True and colorForStart == 0:
                    text(img, "HOLD YOUR FINGER ON RIGHT PINK LINE UNTIL YOUR CIRCLE IS PINK - FOR START THE GAME",
                         (10, 50),
                         0.8)
                    doRandomMaze = True
                    timingForStart = 0
                    colorForStart = 0
                elif colorForStart < 255:
                    text(img, "Keep holding on", (10, 50), 1)
                    colorForStart += 4
                    time_sec = 0

                if collisonFinger(finger, lines) is not True:
                    colorForStart = 0
                    time_sec = 0

                elif colorForStart >= 255:
                    if points == 0:
                        text(img, "Follow the line", (10, 50), 1.2)
                    elif points == 1:
                        text(img, f"Follow the line, You have a {round(20 - time_sec, 2)} SECONDS", (10, 50), 1.3)
                        if time_sec >= 20:
                            colorForStart = 0
                            time_sec = 0
                    elif points == 2:
                        text(img, f"Follow the line, You have a {round(15 - time_sec, 2)} SECONDS", (10, 50), 1.3)
                        if time_sec >= 15:
                            colorForStart = 0
                            time_sec = 0
                    elif points == 3:
                        text(img, f"Follow the line, You have a {round(10 - time_sec, 2)} SECONDS", (10, 50), 1.3)
                        if time_sec >= 10:
                            colorForStart = 0
                            time_sec = 0
                    elif points == 4:
                        text(img, f"Follow the line, You have a {round(5 - time_sec, 2)} SECONDS", (10, 50), 1.3)
                        if time_sec >= 5:
                            colorForStart = 0
                            time_sec = 0

                    if collisonFinger(finger, endPoint):
                        print("pass the game")
                        colorForStart = 0
                        points += 1
                        doRandomMaze = True
            if points == 5:
                print("the game is ")

            text(img, str(f"timer: {int(time_sec)}"), (5, 15), 1)
            text(img, str(f"Points: {points}"), (5, 31), 1)

        cv2.circle(img, finger, 8, (255, 0, colorForStart), cv2.FILLED, cv2.LINE_AA)
        cv2.imshow("Image", img)

        cv2.waitKey(1)

        end = time.time()
        time_sec += end - start
        timer += end - start


if __name__ == "__main__":
    main()
