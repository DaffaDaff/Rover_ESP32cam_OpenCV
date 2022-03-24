#KODE FP M. TAUFIQUL HUDA#
#Perlu install 'pip install opencv-contrib-python numpy urllib3 tensorflow mediapipe'. Run di terminal#

import cv2
import numpy as np
import urllib.request
from kalmanfilter import KalmanFilter
from handDetector import HandDetector

def nothing(x):
    pass

cap = cv2.VideoCapture(0)
hd = HandDetector(min_detection_confidence=0.5)
url= 'http://192.168.4.131/low.jpg'
url1= 'http://192.168.4.1'
scale_percent = 200
human = cv2.CascadeClassifier('tubuh.xml')
wajah = cv2.CascadeClassifier('wajah.xml')
kf = KalmanFilter()
font = cv2.FONT_HERSHEY_COMPLEX
Kernal = np.ones((3, 3), np.uint8)
prev_lingkaran = None
dist = lambda x1,y1,x2,y2: (x1-x2)**2*(y1-y2)**2

#mode kontrol
cv2.namedWindow("Mode Kontrol")
cv2.createTrackbar("0:kontrol gestur, 1:kontrol manual", "Mode Kontrol", 0, 1, nothing)

#range warna
cv2.namedWindow("Tracking warna bola")
cv2.createTrackbar("Low H", "Tracking warna bola", 0, 255, nothing)
cv2.createTrackbar("Low S", "Tracking warna bola", 31, 255, nothing)
cv2.createTrackbar("Low V", "Tracking warna bola", 146, 255, nothing)
cv2.createTrackbar("Up H", "Tracking warna bola", 45, 255, nothing)
cv2.createTrackbar("Up S", "Tracking warna bola", 123, 255, nothing)
cv2.createTrackbar("Up V", "Tracking warna bola", 255, 255, nothing)

cv2.namedWindow("Tracking warna objek lain")
cv2.createTrackbar("Low H", "Tracking warna objek lain", 0, 255, nothing)
cv2.createTrackbar("Low S", "Tracking warna objek lain", 54, 255, nothing)
cv2.createTrackbar("Low V", "Tracking warna objek lain", 149, 255, nothing)
cv2.createTrackbar("Up H", "Tracking warna objek lain", 42, 255, nothing)
cv2.createTrackbar("Up S", "Tracking warna objek lain", 163, 255, nothing)
cv2.createTrackbar("Up V", "Tracking warna objek lain", 255, 255, nothing)

#tunning kotak
cv2.namedWindow("Tunning kotak")
cv2.createTrackbar("luas", "Tunning kotak", 100, 1000, nothing)

while True:
    #atur tunning untuk warna yang dihendaki (default : kuning)
    l_h = cv2.getTrackbarPos("Low H", "Tracking warna bola")
    l_s = cv2.getTrackbarPos("Low S", "Tracking warna bola")
    l_v = cv2.getTrackbarPos("Low V", "Tracking warna bola")
 
    u_h = cv2.getTrackbarPos("Up H", "Tracking warna bola")
    u_s = cv2.getTrackbarPos("Up S", "Tracking warna bola")
    u_v = cv2.getTrackbarPos("Up V", "Tracking warna bola")

    l_h1 = cv2.getTrackbarPos("Low H", "Tracking warna objek lain")
    l_s1 = cv2.getTrackbarPos("Low S", "Tracking warna objek lain")
    l_v1 = cv2.getTrackbarPos("Low V", "Tracking warna objek lain")
 
    u_h1 = cv2.getTrackbarPos("Up H", "Tracking warna objek lain")
    u_s1 = cv2.getTrackbarPos("Up S", "Tracking warna objek lain")
    u_v1 = cv2.getTrackbarPos("Up V", "Tracking warna objek lain")
 
    lb = np.array([l_h, l_s, l_v])
    ub = np.array([u_h, u_s, u_v])

    lb1 = np.array([l_h1, l_s1, l_v1])
    ub1 = np.array([u_h1, u_s1, u_v1])

    n = cv2.getTrackbarPos("0:kontrol gestur, 1:kontrol manual", "Mode Kontrol")

    #ambil foto di ESPcam
    img_resp=urllib.request.urlopen(url)
    imgnp=np.array(bytearray(img_resp.read()),dtype=np.uint8)
    frm=cv2.imdecode(imgnp,-1)
    width = int(frm.shape[1] * scale_percent / 100)
    height = int(frm.shape[0] * scale_percent / 100)
    dim = (width, height)
    frame = cv2.resize(frm, dim, interpolation = cv2.INTER_AREA)

    #mengubah ke HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    #mengubah ke gray
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #object detection(orang dan wajah)
    orang = human.detectMultiScale(gray, 1.1, 3)
    for (x, y, w, h) in orang:
        cv2.putText(frame, "orang", (x, y-5), font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 225, 0), 2)
    face = wajah.detectMultiScale(gray, 1.1, 3)
    for (x, y, w, h) in face:
        cv2.putText(frame, "wajah", (x, y-5), font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 225, 0), 2)
    
    #seleksi warna
    blur = cv2.GaussianBlur(hsv, (11,11), 0)
    layer = cv2.inRange(blur, lb, ub)

    #deteksi jarak (basis warna dan kontur)
    mask = cv2.inRange(hsv, lb, ub)
    opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, Kernal)
    seleksi = cv2.bitwise_and(frame, frame, mask=opening)
    contours, hierarchy = cv2.findContours(opening, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    if len(contours) != 0:
        cnt = contours[0]
        area = cv2.contourArea(cnt)
        M = cv2.moments(cnt)
        Cx = int(M['m10']/M['m00'])
        Cy = int(M['m01'] / M['m00'])

        #kalibrasi titik (0,0) ditengah
        if Cx > 320:
            cx1 = Cx-320
        elif Cx < 320:
            cx1 = (-1)*(320-Cx)
        elif Cx==320:
            cx1 = 0
        
        if Cy < 240:
            cy1 = 240-Cy
        elif Cy > 240:
            cy1 = (-1)*(Cy-240)
        elif Cy==240:
            cy1 = 0
        
        T = 'Lokasi objek :' + '(' + str(cx1) + ',' + str(cy1) + ')'
        cv2.putText(frame, T, (5, 10), font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
        distance = 76.02629852767143 - 0.006148410795131351*area + 2.3767261945558e-07*area**2 - 2.99573127e-12*area**3   #formula jarak
        S = 'Jarak objek : ' + str(distance)
        cv2.putText(frame, S, (5, 25), font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
        cv2.drawContours(frame, cnt, -1, (0, 255, 0), 3)
    
    #deteksi bola basis Hough Circles (hasil modifikasi gabungan metode basis warna dan kontur)
    blur_lingkaran = cv2.GaussianBlur(layer, (11,11), 0)
    lingkaran = cv2.HoughCircles(blur_lingkaran, cv2.HOUGH_GRADIENT, 1.2, 100,
                                param1=100, param2=30, minRadius=0, maxRadius=300)
    if lingkaran is None:
        urllib.request.urlopen(url1+'/?State=OFF')
    if lingkaran is not None:
        urllib.request.urlopen(url1+'/?State=ON')
        lingkaran = np.uint16(np.around(lingkaran))
        target = None
        for i in lingkaran[0, :]:
            if target is None: target = i
            if prev_lingkaran is not None:
                if dist(target[0], target[1], prev_lingkaran[0], prev_lingkaran[1]) <= dist(i[0], i[1], prev_lingkaran[0], prev_lingkaran[1]):
                    target = i
        cv2.line(frame, (320,240), (target[0], target[1]), (71,100,255), 3)
        cv2.circle(frame, (target[0], target[1]), 1, (0,0,255), 3)
        cv2.circle(frame, (target[0], target[1]), target[2], (255, 0, 0), 3)
        
        #trajektori bola dengan kalman filter
        predicted = kf.predict(target[0], target[1])
        cv2.circle(frame, (predicted[0], predicted[1]), 3, (0, 255, 0), 3)
        predicted = kf.predict(predicted[0], predicted[1])
        cv2.circle(frame, (predicted[0], predicted[1]), 3, (0, 255, 0), 3)
        predicted = kf.predict(predicted[0], predicted[1])
        cv2.circle(frame, (predicted[0], predicted[1]), 3, (255, 255, 0), 3)
        cv2.line(frame, (target[0], target[1]), (predicted[0], predicted[1]), (10,50,100), 3)
        area1 = 3.14*target[2]**2
        distance1 = 76.02629852767143 - 0.006148410795131351*area1 + 2.3767261945558e-07*area1**2 - 2.99573127e-12*area1**3
        
        #kalibrasi titik (0,0) ditengah
        if target[0] > 320:
            x_1 = target[0]-320
        elif target[0] < 320:
            x_1 = (-1)*(320-target[0])
        elif target[0]==320:
            x_1 = 0
        
        if target[1] < 240:
            y_1 = 240-target[1]
        elif target[1] > 240:
            y_1 = (-1)*(target[1]-240)
        elif target[1]==240:
            y_1 = 0
        
        U = 'Posisi bola : '+'('+str(x_1)+','+str(y_1)+')'+' dan Luas bola : '+str(area1)
        cv2.putText(frame, U, (5, 40), font, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
        D = 'Jarak dari kamera : '+str(distance1)+' cm'
        cv2.putText(frame, D, (5, 55), font, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
        prev_lingkaran = target
    
    #kontrol pakai gesture tangan
        # 5 = maju
        # 4 = mundur
        # 1 = kanan
        # 2 = kiri
    if n==0:
        ret, img = cap.read()
        hl = hd.findHandLandMarks(image=img, draw=True)
        total = 0
        if(len(hl) != 0):
            if hl[4][3] == "Right" and hl[4][1] > hl[3][1]:
                total = total+1
            elif hl[4][3] == "Left" and hl[4][1] < hl[3][1]:
                total = total+1
            if hl[8][2] < hl[6][2]:
                total = total+1
            if hl[12][2] < hl[10][2]:
                total = total+1
            if hl[16][2] < hl[14][2]:
                total = total+1
            if hl[20][2] < hl[18][2]:
                total = total+1
        if (total==0):
            urllib.request.urlopen(url1+'/?State=S')
            cv2.putText(img, "Setop", (45, 375), font, 1, (255, 0, 0), 5)
        elif (total==1):
            urllib.request.urlopen(url1+'/?State=R')
            cv2.putText(img, "kanan", (45, 375), font, 1, (255, 0, 0), 5)
        elif (total==2):
            urllib.request.urlopen(url1+'/?State=L')
            cv2.putText(img, "kiri", (45, 375), font, 1, (255, 0, 0), 5)
        elif (total==4):
            urllib.request.urlopen(url1+'/?State=B')
            cv2.putText(img, "mundur", (45, 375), font, 1, (255, 0, 0), 5)
        elif (total==5):
            urllib.request.urlopen(url1+'/?State=F')
            cv2.putText(img, "maju", (45, 375), font, 1, (255, 0, 0), 5)

    #deteksi warna dan membuat kontur kedua (untuk deteksi bentuk, default : kuning)
    mask1 = cv2.inRange(frame, lb1, ub1)
    opening1 = cv2.morphologyEx(mask1, cv2.MORPH_OPEN, Kernal)
    contours1, hierarchy1 = cv2.findContours(opening1, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    if len(contours1) != 0:
        cnt1 = contours1[0]
        cv2.drawContours(frame, cnt1, -1, (255, 255, 0), 3)
    
    #deteksi bentuk kotak dan persegi panjang
    imgr = cv2.inRange(hsv, lb1, ub1)
    contours, _ = cv2.findContours(imgr, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.01* cv2.arcLength(contour, True), True)
        cv2.drawContours(frame, [approx], -1, (0, 0, 0), 1)
        x = approx.ravel()[0]
        y = approx.ravel()[1] - 5
        area2 = cv2.contourArea(contour)
        luas = cv2.getTrackbarPos("luas", "Tunning kotak")
        if len(approx) == 4 and area2 > luas:
            x1 ,y1, w, h = cv2.boundingRect(approx)
            aspectRatio = float(w)/h
            if aspectRatio >= 0.95 and aspectRatio <= 1.05:
                cv2.putText(frame, "square", (x, y), font, 0.5, (0, 0, 0))
            else:
                cv2.putText(frame, "rectangle", (x, y), font, 0.5, (0, 0, 0))
    
    #targeting
    cv2.line(frame, (0,240), (640,240), (100,0,225), 1)
    cv2.line(frame, (320,0), (320,480), (100,0,225), 1)
    cv2.circle(frame, (320,240), 10, (0,0,255), 5)
    
    #menampilkan gambar dan window
    cv2.imshow("selektor warna bola", layer)
    cv2.imshow("selektor warna objek lain", mask1)
    cv2.imshow("masking bola", seleksi)
    cv2.imshow("kontrol gestur", img)
    cv2.imshow("Stream", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break
cap.release()
cv2.destroyWindow()