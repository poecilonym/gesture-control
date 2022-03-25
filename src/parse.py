import cv2
import mediapipe as mp
import time
import math

def dist(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2+(p1[2]-p2[2])**2)



mpHands = mp.solutions.hands
hands = mpHands.Hands(static_image_mode=False,
                      max_num_hands=2,
                      min_detection_confidence=0.5,
                      min_tracking_confidence=0.5)
mpDraw = mp.solutions.drawing_utils

handlist=[[1,1,0,0,1,{},[],0,0], [1,1,0,0,1,{},[],0,0]]


workspace = [0, 0]
pageup = [False, False]
pagedown = [False, False]
handopen = [0, 0]

def parse(img, handlist):
    #print("begin====================")
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
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
