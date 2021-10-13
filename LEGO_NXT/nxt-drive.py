#!/usr/bin/env python3
import socket
import threading
import nxt
import sys
import tty, termios
import nxt.locator
import time
import gy271compass as GY271
from nxt.sensor import *
from nxt.motor import *

# 서버의 주소입니다. hostname 또는 ip address를 사용할 수 있습니다.
HOST = '192.168.145.214'
# 서버에서 지정해 놓은 포트 번호입니다.
PORT = 9999

class BRICK():
    name = 'brick1'
    x = None  # 현재 x 좌표
    y = None  # 현재 y 좌표
    state = False   #False : 멈춤, True : 이동 중
    client_socket = None

    def __init__(self):
        """ 브릭 검색과 동시에 모터와 센서 활성화"""
        self.brick = nxt.locator.find_one_brick(silent=False, strict=True,
                                           method=nxt.locator.Method(bluetooth=False, usb=True))
        self.right = nxt.Motor(self.brick, PORT_A)
        self.left = nxt.Motor(self.brick, PORT_B)
        self.both = nxt.SynchronizedMotors(self.left, self.right, 0)
        self.leftboth = nxt.SynchronizedMotors(self.left, self.right, 100)
        self.rightboth = nxt.SynchronizedMotors(self.right, self.left, 100)
        self.Ultrasonic1 = Ultrasonic(self.brick, PORT_1)  # .get_sample()
        self.Ultrasonic2 = Ultrasonic(self.brick, PORT_2)  # .get_sample()
        self.sensor = GY271.compass()

    def moveToDestination(self, Dx, Dy):
        """목표 좌표를 인자로 받아 해당 좌표로 움직인 후 결과를 전송"""
        print("start moveToDes", Dx, Dy)
        res = False # or True  도착 or 경로 없음
        while self.x == None or self.y == None:
            print("self.x or self.y == None")
            time.sleep(0.5)
        xdist = (Dx - self.x)
        ydist = (Dy - self.y)
        while not res: #result 값이 true 까지
            if xdist > 0: # 목표 좌표가 오른쪽일때
                self.rightboth.turn(100, 390, False)
                if (self.sensor.get_bearing() - 90) >= 15:
                    self.leftboth.turn(100, 30, False)
                elif (self.sensor.get_bearing() - 90) <= -15:
                    self.rightboth.turn(100, 30, False)
                time.sleep(1)
                while xdist >= 0.2:
                    xdist = (Dx - self.x)  # 좌표 거리 다시 계산
                    ydist = (Dy - self.y)
                    self.both.turn(100, 180, False)
                    time.sleep(1)
                    if (self.sensor.get_bearing() - 90) >= 15:
                        self.leftboth.turn(100, 30, False)
                    elif (self.sensor.get_bearing() - 90) <= -15:
                        self.rightboth.turn(100, 30, False)
                    if self.Ultrasonic1.get_sample() <= 10: # 전방 장애물 감지
                        while self.Ultrasonic1.get_sample() >= 10: # 전방 장애물 감지 안될때까지
                            if self.Ultrasonic2.get_sample() >= 20: # 왼쪽 장애물 없을때
                                self.leftboth.turn(100, 380, False) # 장애물 감지 안될때까지 한칸씩 움직이면서 우측보고 감지
                                time.sleep(1)
                                self.both.turn(100, 360, False)
                                time.sleep(1)
                                self.rightboth.turn(100, 390, False)
                                if (self.sensor.get_bearing() - 90) >= 15:
                                    self.leftboth.turn(100, 30, False)
                                elif (self.sensor.get_bearing() - 90) <= -15:
                                    self.rightboth.turn(100, 30, False)
                            else: # 왼쪽 장애물있을때
                                self.rightboth.turn(100, 390, False) # 장애물 감지 안될때까지 한칸씩 움직이면서 좌측보고 감지
                                time.sleep(1)
                                self.both.turn(100, 360, False)
                                time.sleep(1)
                                self.leftboth.turn(100, 380, False)
                                if (self.sensor.get_bearing() - 90) >= 15:
                                    self.leftboth.turn(100, 30, False)
                                elif (self.sensor.get_bearing() - 90) <= -15:
                                    self.rightboth.turn(100, 30, False)

                xdist = (Dx - self.x) # 좌표 거리 다시 계산
                ydist = (Dy - self.y)

                if ydist > 0: # 목표 좌표가 위일때
                    self.leftboth.turn(100, 380, False)
                    time.sleep(1)
                    if self.sensor.get_bearing() >= 15:
                        self.leftboth.turn(100, 30, False)
                    elif self.sensor.get_bearing() <= -15:
                        self.rightboth.turn(100, 30, False)
                    while ydist >= 0.2:
                        xdist = (Dx - self.x)  # 좌표 거리 다시 계산
                        ydist = (Dy - self.y)
                        self.both.turn(100, 180, False)
                        time.sleep(1)
                        if self.sensor.get_bearing() >= 15:
                            self.leftboth.turn(100, 30, False)
                        elif self.sensor.get_bearing() <= -15:
                            self.rightboth.turn(100, 30, False)
                        if self.Ultrasonic1.get_sample() <= 10: # 전방 장애물 감지
                            while self.Ultrasonic1.get_sample() >= 10:  # 전방 장애물 감지 안될때까지
                                if self.Ultrasonic2.get_sample() >= 20: # 왼쪽 장애물 없을때
                                    self.leftboth.turn(100, 380, False) # 장애물 감지 안될때까지 한칸씩 움직이면서 우측보고 감지
                                    time.sleep(1)
                                    self.both.turn(100, 360, False)
                                    time.sleep(1)
                                    self.rightboth.turn(100, 390, False)
                                    if self.sensor.get_bearing() >= 15:
                                        self.leftboth.turn(100, 30, False)
                                    elif self.sensor.get_bearing() <= -15:
                                        self.rightboth.turn(100, 30, False)
                                else: # 왼쪽 장애물있을때
                                    self.rightboth.turn(100, 390, False) # 장애물 감지 안될때까지 한칸씩 움직이면서 좌측보고 감지
                                    time.sleep(1)
                                    self.both.turn(100, 360, False)
                                    time.sleep(1)
                                    self.leftboth.turn(100, 380, False)
                                    if self.sensor.get_bearing() >= 15:
                                        self.leftboth.turn(100, 30, False)
                                    elif self.sensor.get_bearing() <= -15:
                                        self.rightboth.turn(100, 30, False)

                    self.rightboth.turn(100, 390, False) # 목표 좌표 방향 회전
                    if self.sensor.get_bearing() >= 15:
                        self.leftboth.turn(100, 30, False)
                    elif self.sensor.get_bearing() <= -15:
                        self.rightboth.turn(100, 30, False)

                    xdist = (Dx - self.x)  # 좌표 거리 다시 계산
                    ydist = (Dy - self.y)

                    while xdist > 0.2:
                        xdist = (Dx - self.x)  # 좌표 거리 다시 계산
                        ydist = (Dy - self.y)
                        self.both.turn(100, 180, False)
                        time.sleep(1)

                else: # 목표 좌표가 아래일때
                    self.rightboth.turn(100, 390, False)
                    time.sleep(1)
                    if (self.sensor.get_bearing() - 180) >= 15:
                        self.leftboth.turn(100, 30, False)
                    elif (self.sensor.get_bearing() - 180) <= -15:
                        self.rightboth.turn(100, 30, False)
                    while ydist >= -0.2:
                        xdist = (Dx - self.x)  # 좌표 거리 다시 계산
                        ydist = (Dy - self.y)
                        self.both.turn(100, 180, False)
                        time.sleep(1)
                        if (self.sensor.get_bearing() - 180) >= 15:
                            self.leftboth.turn(100, 30, False)
                        elif (self.sensor.get_bearing() - 180) <= -15:
                            self.rightboth.turn(100, 30, False)
                        if self.Ultrasonic1.get_sample() <= 10: # 전방 장애물 감지
                            while self.Ultrasonic1.get_sample() >= 10:
                                if self.Ultrasonic2.get_sample() >= 20: # 왼쪽 장애물 없을때
                                    self.leftboth.turn(100, 380, False) # 장애물 감지 안될때까지 한칸씩 움직이면서 우측보고 감지
                                    time.sleep(1)
                                    self.both.turn(100, 360, False)
                                    time.sleep(1)
                                    self.rightboth.turn(100, 390, False)
                                    if (self.sensor.get_bearing() - 180) >= 15:
                                        self.leftboth.turn(100, 30, False)
                                    elif (self.sensor.get_bearing() - 180) <= -15:
                                        self.rightboth.turn(100, 30, False)
                                else: # 왼쪽 장애물있을때
                                    self.rightboth.turn(100, 390, False) # 장애물 감지 안될때까지 한칸씩 움직이면서 좌측보고 감지
                                    time.sleep(1)
                                    self.both.turn(100, 360, False)
                                    time.sleep(1)
                                    self.leftboth.turn(100, 380, False)
                                    if (self.sensor.get_bearing() - 180) >= 15:
                                        self.leftboth.turn(100, 30, False)
                                    elif (self.sensor.get_bearing() - 180) <= -15:
                                        self.rightboth.turn(100, 30, False)

                    self.leftboth.turn(100, 360, False) # 목표 좌표 방향 회전
                    if (self.sensor.get_bearing() - 90) >= 15:
                        self.leftboth.turn(100, 30, False)
                    elif (self.sensor.get_bearing() - 90) <= -15:
                        self.rightboth.turn(100, 30, False)

                    xdist = (Dx - self.x)  # 좌표 거리 다시 계산
                    ydist = (Dy - self.y)

                    while xdist >= 0.2:
                        xdist = (Dx - self.x)  # 좌표 거리 다시 계산
                        ydist = (Dy - self.y)
                        self.both.turn(100, 180, False)
                        time.sleep(1)

            else: # 목표 좌표가 왼쪽일때
                self.leftboth.turn(100, 380, False)
                time.sleep(1)
                if (self.sensor.get_bearing() - 270) >= 15:
                    self.leftboth.turn(100, 30, False)
                elif (self.sensor.get_bearing() - 270) <= -15:
                    self.rightboth.turn(100, 30, False)
                while xdist >= -0.2:
                    xdist = (Dx - self.x)  # 좌표 거리 다시 계산
                    ydist = (Dy - self.y)
                    self.both.turn(100, 180, False)
                    time.sleep(1)
                    if (self.sensor.get_bearing() - 270) >= 15:
                        self.leftboth.turn(100, 30, False)
                    elif (self.sensor.get_bearing() - 270) <= -15:
                        self.rightboth.turn(100, 30, False)
                    if self.Ultrasonic1.get_sample() <= 10: # 전방 장애물 감지
                        while self.Ultrasonic1.get_sample() >= 10:
                            if self.Ultrasonic2.get_sample() >= 20: # 왼쪽 장애물 없을때
                                self.leftboth.turn(100, 380, False) # 장애물 감지 안될때까지 한칸씩 움직이면서 우측보고 감지
                                time.sleep(1)
                                self.both.turn(100, 360, False)
                                time.sleep(1)
                                self.rightboth.turn(100, 390, False)
                                if (self.sensor.get_bearing() - 270) >= 15:
                                    self.leftboth.turn(100, 30, False)
                                elif (self.sensor.get_bearing() - 270) <= -15:
                                    self.rightboth.turn(100, 30, False)
                            else: # 왼쪽 장애물있을때
                                self.rightboth.turn(100, 390, False) # 장애물 감지 안될때까지 한칸씩 움직이면서 좌측보고 감지
                                time.sleep(1)
                                self.both.turn(100, 360, False)
                                time.sleep(1)
                                self.leftboth.turn(100, 380, False)
                                if (self.sensor.get_bearing() - 270) >= 15:
                                    self.leftboth.turn(100, 30, False)
                                elif (self.sensor.get_bearing() - 270) <= -15:
                                    self.rightboth.turn(100, 30, False)

                xdist = (Dx - self.x) # 좌표 거리 다시 계산
                ydist = (Dy - self.y)

                if ydist > 0: # 목표 좌표가 위일때
                    self.rightboth.turn(100, 390, False)
                    time.sleep(1)
                    while ydist >= 0.2:
                        xdist = (Dx - self.x)  # 좌표 거리 다시 계산
                        ydist = (Dy - self.y)
                        self.both.turn(100, 180, False)
                        time.sleep(1)
                        if self.sensor.get_bearing() >= 15:
                            self.leftboth.turn(100, 30, False)
                        elif self.sensor.get_bearing() <= -15:
                            self.rightboth.turn(100, 30, False)
                        if self.Ultrasonic1.get_sample() <= 10: # 전방 장애물 감지
                            while self.Ultrasonic1.get_sample() >= 10:
                                if self.Ultrasonic2.get_sample() >= 20: # 왼쪽 장애물 없을때
                                    self.leftboth.turn(100, 380, False) # 장애물 감지 안될때까지 한칸씩 움직이면서 우측보고 감지
                                    time.sleep(1)
                                    self.both.turn(100, 360, False)
                                    time.sleep(1)
                                    self.rightboth.turn(100, 390, False)
                                    if self.sensor.get_bearing() >= 15:
                                        self.leftboth.turn(100, 30, False)
                                    elif self.sensor.get_bearing() <= -15:
                                        self.rightboth.turn(100, 30, False)
                                else: # 왼쪽 장애물있을때
                                    self.rightboth.turn(100, 390, False) # 장애물 감지 안될때까지 한칸씩 움직이면서 좌측보고 감지
                                    time.sleep(1)
                                    self.both.turn(100, 360, False)
                                    time.sleep(1)
                                    self.leftboth.turn(100, 380, False)
                                    if self.sensor.get_bearing() >= 15:
                                        self.leftboth.turn(100, 30, False)
                                    elif self.sensor.get_bearing() <= -15:
                                        self.rightboth.turn(100, 30, False)

                    self.leftboth.turn(100, 380, False) # 목표 좌표 방향 회전
                    if (self.sensor.get_bearing() - 270) >= 15:
                        self.leftboth.turn(100, 30, False)
                    elif (self.sensor.get_bearing() - 270) <= -15:
                        self.rightboth.turn(100, 30, False)

                    xdist = (Dx - self.x)  # 좌표 거리 다시 계산
                    ydist = (Dy - self.y)

                    while xdist >= 0.2:
                        xdist = (Dx - self.x)  # 좌표 거리 다시 계산
                        ydist = (Dy - self.y)
                        self.both.turn(100, 180, False)
                        time.sleep(1)

                else: # 목표 좌표가 아래일때
                    self.leftboth.turn(100, 380, False)
                    time.sleep(1)
                    if (self.sensor.get_bearing() - 180) >= 15:
                        self.leftboth.turn(100, 30, False)
                    elif (self.sensor.get_bearing() - 180) <= -15:
                        self.rightboth.turn(100, 30, False)
                    while ydist >= -0.2:
                        xdist = (Dx - self.x)  # 좌표 거리 다시 계산
                        ydist = (Dy - self.y)
                        self.both.turn(100, 180, False)
                        time.sleep(1)
                        if (self.sensor.get_bearing() - 180) >= 15:
                            self.leftboth.turn(100, 30, False)
                        elif (self.sensor.get_bearing() - 180) <= -15:
                            self.rightboth.turn(100, 30, False)
                        if self.Ultrasonic1.get_sample() <= 10: # 전방 장애물 감지
                            while self.Ultrasonic1.get_sample() >= 10:
                                if self.Ultrasonic2.get_sample() >= 20: # 왼쪽 장애물 없을때
                                    self.leftboth.turn(100, 380, False) # 장애물 감지 안될때까지 한칸씩 움직이면서 우측보고 감지
                                    time.sleep(1)
                                    self.both.turn(100, 360, False)
                                    time.sleep(1)
                                    self.rightboth.turn(100, 390, False)
                                    if (self.sensor.get_bearing() - 180) >= 15:
                                        self.leftboth.turn(100, 30, False)
                                    elif (self.sensor.get_bearing() - 180) <= -15:
                                        self.rightboth.turn(100, 30, False)
                                else: # 왼쪽 장애물있을때
                                    self.rightboth.turn(100, 390, False) # 장애물 감지 안될때까지 한칸씩 움직이면서 좌측보고 감지
                                    time.sleep(1)
                                    self.both.turn(100, 360, False)
                                    time.sleep(1)
                                    self.leftboth.turn(100, 380, False)
                                    if (self.sensor.get_bearing() - 180) >= 15:
                                        self.leftboth.turn(100, 30, False)
                                    elif (self.sensor.get_bearing() - 180) <= -15:
                                        self.rightboth.turn(100, 30, False)

                    self.rightboth.turn(100, 390, False) # 목표 좌표 방향 회전
                    if (self.sensor.get_bearing() - 270) >= 15:
                        self.leftboth.turn(100, 30, False)
                    elif (self.sensor.get_bearing() - 270) <= -15:
                        self.rightboth.turn(100, 30, False)

                    xdist = (Dx - self.x)  # 좌표 거리 다시 계산
                    ydist = (Dy - self.y)

                    while xdist >= 0.2:
                        xdist = (Dx - self.x)  # 좌표 거리 다시 계산
                        ydist = (Dy - self.y)
                        self.both.turn(100, 180, False)
                        time.sleep(1)

            if Dx - self.x <= 0.2 and Dy - self.y <= 0.2: # 목표 좌표 도착
                res = True
            

            




        # TODO:목표 좌표로 이동 하는 알고리즘 작성, 결과에 따른 참/거짓값 res에 저장

        self.sendSocket(str(res))  #결과 메인PC에 전송

        return



    def receiveSocket(self,client_socket):
        """소켓을 통해 명령을 받거나 현재 좌표를 수신하여 클래스 내부 인자 x, y를 지속적으로 수정"""
        while True:
            # 메시지를 수신합니다.
            data = client_socket.recv(1024)
            data = data.decode("utf-8")
            if data[0] == 'C':
                data = data[2:].split(',')
                self.x = float(data[0])
                self.y = float(data[1])
            elif data[0] == 'O':
                data = data[2:].split(',')
                Dx = float(data[2])
                Dy = float(data[3])
                print("receive Order")

                T = threading.Thread(target=self.moveToDestination, args=(Dx, Dy,))
                T.start()
            print(self.x, self.y)




    def sendSocket(self,msg):
        """목표 좌표에 도착 or 경로 없음 or 현재 상태를 메인 컨트롤러에 전송"""
        if str == "close":
            self.client_socket.close()
        self.client_socket.sendall(str.encode('utf-8'))

    def conncet(self):
        # 소켓 객체를 생성합니다.
        # 주소 체계(address family)로 IPv4, 소켓 타입으로 TCP 사용합니다.

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 지정한 HOST와 PORT를 사용하여 서버에 접속합니다.
        self.client_socket.connect((HOST, PORT))
        self.client_socket.sendall(self.name.encode('utf-8'))
        rec = threading.Thread(target=self.receiveSocket, args=(self.client_socket,))
        #sen = threading.Thread(target=self.sendSocket, args=(self.client_socket,))

        #sen.start()
        rec.start()

        #sen.join()
        #rec.join()

    def __str__(self):
        str = None
        if self.state:
            str = "이동 중"
        else:
            str = "정지"

        return "Current State : %s\nCurrent Point : (%f, %f)"%(str, self.x, self.y)



def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch





if __name__ == "__main__":
    ch = ' '
    print("Ready")
    brick = BRICK()
    brick.conncet()
    # while ch != 'q':
    #     ch = getch()
    #
    #     if ch == 's':
    #         print("Backwards")
    #         brick.both.turn(-100, 360, False)
    #     elif ch == 'w':
    #         print("Forwards")
    #         brick.both.turn(100, 360, False)
    #     elif ch == 'd':
    #         print("Right")
    #         brick.leftboth.turn(100, 360, False)
    #     elif ch == 'a':
    #         print("Left")
    #         brick.rightboth.turn(100, 360, False)
    # print("Finished")
