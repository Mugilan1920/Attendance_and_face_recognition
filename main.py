import cv2
import numpy as np
import face_recognition
import os
import sys
from datetime import datetime
import mysql.connector as m
pwd=input("Mysql Password:")
con = mc.connect(host = 'localhost', user = 'root', passwd = pwd,database='dss')
cur = con.cursor()
# from PIL import ImageGrab


path = 'C:\\Users\\M.Harini Vaishu\\Documents\\HARINI PADMA IT\\DSS\\IMAGESATTENDANCE'
images = []
classNames = []
myList = os.listdir(path)
print(myList)
count=0
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    print(count)
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
    count+=1
print(classNames)

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        #cv2.imshow('image',img)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList
 
def markAttendance(name):
    with open('Attendance.csv','r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            now = datetime.now()
            dtString = now.strftime('%H:%M:%S')
            f.writelines(f'\n{name},{dtString}')
 
#### FOR CAPTURING SCREEN RATHER THAN WEBCAM
# def captureScreen(bbox=(300,300,690+300,530+300)):
#     capScr = np.array(ImageGrab.grab(bbox))
#     capScr = cv2.cvtColor(capScr, cv2.COLOR_RGB2BGR)
#     return capScr
 
encodeListKnown = findEncodings(images)
print('Encoding Complete')
 
cap = cv2.VideoCapture(0)

def time_chk(timer):
    if(timer>='08:30:00' and timer<='09:20:00'):
        hour='I'
    elif(timer>'09:20:00' and timer<='10:10:00'):
        hour='II'
    elif (timer>'10:10:00' and timer<='11:00:00'):
        hour='III'
    elif (timer>='11:40:00' and timer<='12:30:00'):
        hour='IV'
    elif (timer>'12:30:00' and timer<='13:20:00'):
        hour='V'
    elif (timer>='13:35:00' and timer<='14:25:00'):
        hour='VI'
    elif (timer>'14:25:00' and timer<='15:15:00'):
        hour='VII'
    else:
        hour=0
        print("NO LOITTERING")
    return hour

def database(reg,hour):
    cur.execute("SELECT * FROM STUDENT WHERE Reg_No="+reg)
    data=[]
    table = cur.fetchall()
    for row in table:
        row = list(row)
        if(row!= []):
            data.append(row)
    cls=data[0][2]
    #print(data[0][0],data[0][1])
   # except:
        #sys.exit()
    yr=data[0][3]
    tt=str(cls)+'_'+str(yr)
    cur.execute("SELECT DAYOFWEEK(CURDATE());")
    day=cur.fetchall()[0][0]
    
    query="SELECT Reg_No,Name,Student.Year,Student.Class_and_Sec,"+hour+" from student,"+tt+" Where Student.Class_and_sec="+tt+".Class_and_sec and Student.Year="+tt+".Year and Day=%s and Reg_No=%s;"
    frmt=(2,reg)
    cur.execute(query,frmt)
    table = cur.fetchall()
    print(table)

while True:
    success, img = cap.read()
    #img = captureScreen()
    imgS = cv2.resize(img,(0,0),None,0.25,0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
 
    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS,facesCurFrame)
    for encodeFace,faceLoc in zip(encodesCurFrame,facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
        #print(faceDis)
        matchIndex = np.argmin(faceDis)
        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            reg=name
            now = datetime.now()
            timer = now.strftime('%H:%M:%S')
            hour=time_chk(timer)
            if(hour!=0):
                database(reg,hour)
            y1,x2,y2,x1 = faceLoc
            y1, x2, y2, x1 = y1*4,x2*4,y2*4,x1*4
            cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
            cv2.rectangle(img,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
            cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
            #now = datetime.now()
            #timer = now.strftime('%H:%M:%S')
            #hour=time_chk(timer)
            #database(reg,hour)'''
            #markAttendance(name)
    cv2.imshow('Webcam',img)
    cv2.waitKey(1)

        
