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
    index=-2
    arr=[]
    i=10

    while i>0:
        cap=cv.VideoCapture(index)
        if cap.read()[0]:
            arr.append(index)
            cap.release()
        index+=1
        i-=1

    return arr

camacess=returcameraind()[0]

wcam, hcam = 800, 480

cv.namedWindow("preview")
cap = cv.VideoCapture(camacess)

if not (cap.isOpened()):
   print("Could not open video device")

ptime=0

detector=ht.handDetector()
while True:

    success, img = cap.read()

    img=imutils.resize(img, width=wcam,height=hcam)
    img=detector.findHands(img)
    fingerlist=list(detector.findPosition(img,draw=False))

    linewidth=0
    rec_len=0

    if len(fingerlist[0]) !=0:

       # print(fingerlist[0][4],fingerlist[0][8])

       x1, y1 = fingerlist[0][4][1], fingerlist[0][4][2]
       x2, y2 = fingerlist[0][8][1], fingerlist[0][8][2]
       cx,cy=(x1+x2)//2,(y1+y2)//2

       cv.circle(img, (x1, y1), 15, (255, 0, 255), cv.FILLED)
       cv.circle(img, (x2, y2), 15, (255, 0, 255), cv.FILLED)
       cv.circle(img, (cx, cy), 15, (255, 0, 255), cv.FILLED)

       cv.line(img,(x1,y1),(x2,y2),(255,0,255),3)

       linewidth=math.hypot(x2-x1,y2-y1)   #range 0 -->250
       print(linewidth)

       volum=np.interp(linewidth,[20,200],[-65,0])

       if fingerlist[0][16][2] < fingerlist[0][8][2]:
            volume.SetMasterVolumeLevel(volum,None)

       if(linewidth<30):
           # key = "space"
           # pyautogui.press(key)

           cv.circle(img, (cx, cy), 15, (0, 255, 0), cv.FILLED)


       rect_percent = np.interp(volum, [-65, 0], [0, 100])
       cv.putText(img, f"{int(rect_percent)}%", (40, 450), cv.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 1)

       rec_len=np.interp(rect_percent,[0,100],[400,150])

       cv.rectangle(img, (50, 150), (85, 400), (0, 255, 0))
       cv.rectangle(img,(50,int(rec_len)),(85,400),(0,255,0),cv.FILLED)



    ctime=time.time()
    fps=1/(ctime-ptime)
    ptime=ctime
    cv.putText(img,f"Fps :{int(fps)}",(40,70),cv.FONT_HERSHEY_PLAIN,3,(255,0,255),1)

    cv.imshow("Image",img)
    cv.waitKey(50)


