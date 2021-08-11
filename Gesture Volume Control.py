import time
import imutils as imutils
import numpy as np
import cv2 as cv
import math

import pyautogui

import HandTrackingModule as ht
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))


# volume.GetMute()
# volume.GetMasterVolumeLevel()

# volume.GetVolumeRange()
# volume.SetMasterVolumeLevel(-20.0, None)

def returcameraind():
    index = -2
    arr = []
    i = 10

    while i > 0:
        cap = cv.VideoCapture(index)
        if cap.read()[0]:
            arr.append(index)
            cap.release()
        index += 1
        i -= 1

    return arr


camacess = returcameraind()[0]

wcam, hcam = 800, 480

cv.namedWindow("preview")
cap = cv.VideoCapture(camacess)

if not (cap.isOpened()):
    print("Could not open video device")

ptime = 0

detector = ht.handDetector()
while True:

    success, img = cap.read()

    img = imutils.resize(img, width=wcam, height=hcam)
    img = detector.findHands(img)
    fingerlist, bbox = list(detector.findPosition(img, draw=True))

    rec_len = 0

    if len(fingerlist) != 0:
        # print(bbox)
        aree = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) // 100
        # print(aree)
        # print(fingerlist[0][4],fingerlist[0][8])

        if 250 < aree < 1000:
            # Find distance
            length, img, lineinfo = detector.findDistance(4, 8, img)
            print(length)
            #  convert volume

            volpercent = np.interp(length, [50, 300], [0, 100])

            #  reduce resultion to make bar smoother

            smoothe=5
            volpercent=smoothe * round(volpercent/smoothe)

            if fingerlist[16][2] > fingerlist[10][2]:
                volume.SetMasterVolumeLevelScalar(volpercent / 100, None)
                cv.circle(img, (lineinfo[4], lineinfo[5]), 15, (0, 255, 0), cv.FILLED)

            if (length < 60):
                # key = "space"
                # pyautogui.press(key)
                cv.circle(img, (lineinfo[4], lineinfo[5]), 15, (0, 255, 0), cv.FILLED)

            cv.putText(img, f"{int(volpercent)}%", (40, 450), cv.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 1)

            rec_len = np.interp(length, [50, 300], [400, 150])

            cv.rectangle(img, (50, 150), (85, 400), (0, 255, 0))
            cv.rectangle(img, (50, int(rec_len)), (85, 400), (0, 255, 0), cv.FILLED)

            actualvolume=int(volume.GetMasterVolumeLevelScalar()*100)
            if actualvolume%smoothe!=0:
                actualvolume+=1

            cv.putText(img, f"actualvolume: {actualvolume} %", (440,70), cv.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 1)

    ctime = time.time()
    fps = 1 / (ctime - ptime)
    ptime = ctime
    cv.putText(img, f"Fps :{int(fps)}", (40, 70), cv.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 1)

    cv.imshow("Image", img)
    cv.waitKey(1)
