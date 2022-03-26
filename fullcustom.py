import cv2
import mediapipe as mp
import time
import math
import subprocess
import threading

def wait_1():
    global wait
    time.sleep(1)
    wait = False

def wait_m_finger():
    global m_finger
    time.sleep(1)
    if m_finger == True:
        subprocess.run(["notify-send", "middle_finger"])

wait_thread = threading.Thread(target=wait_1, name="Waiter")
finger_thread = threading.Thread(target=wait_m_finger, name="finger Waiter")

def dist(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2+(p1[2]-p2[2])**2)

wait = False
m_finger = False
#get capture device
try:
    cap = cv2.VideoCapture(0)
    success, img = cap.read()
    h, w, c = img.shape
    d = (h+w)/2
except:
    print("could not get a capture device, check if your webcam is plugged in")
    exit(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands(static_image_mode=False,
                      max_num_hands=2,
                      min_detection_confidence=0.5,
                      min_tracking_confidence=0.5)
mpDraw = mp.solutions.drawing_utils

ptime = 0
ctime = 0
pTime = 0
cTime = 0

handlist=[[1,1,0,0,1,{},[],0,0], [1,1,0,0,1,{},[],0,0]]

#success, img = cap.read()
#h, w, c = img.shape
#d = (h+w)/2

workspace = [0, 0]
pageup = [False, False]
pagedown = [False, False]
handopen = [0, 0]

while True:
    #print("begin====================")
    success, img = cap.read()
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    ctime = time.time()
    frametime = (ctime-ptime)
    #print(frametime)
    ptime = ctime
    #print(results.multi_hand_landmarks)
    #print("\n\n\n\n")
    i = 0
    o = 0
    for lis in handlist:
        lis[4] += 1
    #print(handlist)
    if results.multi_hand_landmarks:
        handdet = len(results.multi_hand_landmarks)
        if results.multi_handedness[i].classification[0].label == "Right":
            o = 1
        else:
            o = 0
        #print(results.multi_handedness[0].classification[0].label)
        for handLms in results.multi_hand_landmarks:
            #print(i)
            #handlist[i][4] += 1
            #good code
            if i<len(handlist):
                pos = [0, 0, 0, 0, handlist[o][4],{},[],0,0]
            else:
                break
            for id, lm in enumerate(handLms.landmark):
                #print(id,lm)
                cx, cy, cz = int(lm.x*w), int(lm.y*h), int(lm.z*d)
                pos[0] += cx
                pos[1] += cy
                if id == 0 or 4 or 5 or 8 or 12 or 13 or 16 or 20:
                    pos[5][id] = (cx, cy, cz)
                #print(str(cx) + " " + str(cy))
                #if id ==0:
                cv2.circle(img, (cx,cy), 3, (0,0,0), cv2.FILLED)
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
            pos[0] = pos[0]/21
            pos[1] = pos[1]/21
            #print("i: "+str(i)+" o: "+str(o))
            #print(pos[4])
            try:
                pos[2] = (handlist[o][0]-pos[0])/pos[4]
                pos[3] = (handlist[o][1]-pos[1])/pos[4]
            except:
                pos[2] = handlist[o][0]-pos[0]
                pos[3] = handlist[o][1]-pos[1]
            pos[4] = 0
            dis = dist(pos[5][0], pos[5][13])
            pos[6].append(dist(pos[5][5], pos[5][4]) < dist(pos[5][5], pos[5][13]) or dis*1.4 > dist(pos[5][0], pos[5][4]))
            for idx in (8,12,16,20):
                pos[6].append(dis*1.3 > dist(pos[5][0], pos[5][idx]))
            #print(pos[6])
            #nice code
            try:
                rel = (pos[5][0][1]-pos[5][4][1])/(pos[5][0][0]-pos[5][4][0])
                #rel = ((pos[5][0][1]-pos[5][4][1])/dist(pos[5][0], pos[5][4]))
            except:
                rel = 999
            #print(rel)
            prev = handlist[o][7]
            pos[7] = math.degrees(math.atan(rel))
            #print(pos[5][0][1]>pos[5][4][1])
            if pos[5][0][0]<pos[5][4][0]:
                if pos[5][0][1]>pos[5][4][1]:
                    pos[7] = 90+pos[7]+90
                else:
                    pos[7] = -(90-pos[7])-90
            try:
                pos[8] = (pos[7]-prev)/handlist[o][4]
            except:
                pos[8] = pos[7]-prev
            #print(pos[8])
            #print(pos[7])
            #if len(handlist)>i:
            handlist[o] = pos
            #templist.append(pos)
            #handlist[i] = pos
            i += 1
            #good job
        #handlist = templist
        #print(handlist)
    #print(handlist)
    #print()
    i = 0
    #print(wait)
    #print(wait_thread.is_alive())
    hand = handlist[1]
    if hand[4] < 4:
        if hand[6] == [False, True, True, True, True]:
            #print("audio")
            if -10 < hand[8] < -1:
                #print(hand[8])
                print("decrease")
                print(str(int(hand[8])))
                subprocess.run(["pamixer", "-d", str(int(abs(hand[8])))])

            if 10 > hand[8] > 1:
                #print(hand[8])
                print("increase")
                print(str(int(hand[8])))
                subprocess.run(["pamixer", "-i", str(int(hand[8]))])
        if hand[6] == [False, False, True, True, True] and wait == False:
            print("left right")
            if hand[8] > 10:
                print("right")
                subprocess.run(["sudo", "ydotool", "key", "-d", "5", "106:1", "106:0"])
                #subprocess.run(["notify-send", "helloo"])
                wait = True
                wait_thread = threading.Thread(target=wait_1, name="Waiter")
                wait_thread.start()
            if hand[8] < -10:
                print("left")
                subprocess.run(["sudo", "ydotool", "key", "-d", "5", "105:1", "105:0"])
                wait = True
                wait_thread = threading.Thread(target=wait_1, name="Waiter")
                wait_thread.start()
        if hand[6] == [False, True, False, True, True]:
            print("middle finger")
            m_finger = True
            if not finger_thread.is_alive():
                finger_thread = threading.Thread(target=wait_m_finger, name="finger Waiter")
                finger_thread.start()
        if not hand[6] == [False, True, False, True, True]:
            m_finger = False 
        

        """if hand[6] == [False, False, True, True, True]:
            if 16 > hand[8] > 1 or -1 > hand[8] > -16:
                workspace[i] += hand[8]
            #print()
            #print(i)
            #print(str(hand[8])+"   "+str(workspace[i]))
            #print(str(pageup[i])+" "+str(pagedown[i]))
            if workspace[i] > 35 and not pageup[i]:
                #print("up==============================================")
                workspace[i] = 0
                pageup[i] = True
            if workspace[i] < -35 and not pagedown[i]:
                #print("down============================================")
                workspace[i] = 0
                pagedown[i] = True
        if hand[6] == [False, False, False, False, False]:
            handopen[i] += 1
            #print("open")
            if handopen[i] > 5:
                #print("REsertttttttttttttttttttttttttttttttttt")
                workspace[i] = 0
                handopen[i] = 0
                pagedown[i] = False
                pageup[i] = False
    else:
        #print("resresresresresres"+str(i))
        #pagedown[i] = False
        #pageup[i] = False
        workspace[i] = 0
    """

    fps = (1/frametime)
    cv2.putText(img,str(int(fps)), (10,70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 1)
    #print(fps)
    cv2.imshow("Image", img)
    cv2.waitKey(1)
