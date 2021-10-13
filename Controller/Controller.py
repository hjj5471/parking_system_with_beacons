import socket
import threading
from time import sleep
from marvelmind import MarvelmindHedge
from algorithm import Board
from hedge import Hedge

dx, dy = [1, -1, 0, 0], [0, 0, 1, -1]
host = "192.168.145.214"
port = 9999
size_X = 8
size_Y = 5

class Controller:
    socket_list = {}
    brick_list = {}
    hedge = None
    threads = {}
    parking_list = [[-1]*size_Y for i in range(size_X)]
    str = None

    def selectBrick(self):
        """이동 중이 아닌 브릭 중 택 1"""
        while True:
            for key in self.brick_list.keys():
                if not self.brick_list[key]:
                    return key

    def inputCar(self, carNum):
        """차량 입차"""
        Des = self.parkingAlgorithm()
        if Des[0] != None and Des[1] != None:
            self.parking_list[Des[0]][Des[1]] = carNum

        Ix = size_X
        Iy = size_Y              #차량이 들어오는 위치

        self.sendOrder((Ix, Iy, Des[0], Des[1]))
        
    def inputCarXY(self, carNum, dX, dY):
         if self.parking_list[dX][dY] == -1:

            self.parking_list[dX][dY] = carNum
            sleep(6)
            print("(%d,%d)에 %d차량 주차를 완료하였습니다."%(dX, dY, carNum))
         else:
             print("Error")
             print("(X,Y)는 이미 차량이 존재합니다.")


    def outputCar(self, carNum):
        board = Board(self.parking_list, carNum)
        flag, movingStk = board.algorithm()           #차량들의 이동 동선

        if not flag:
            for move in movingStk:
                print(move[0] + 1, move[1]+ 1, '->', move[0] + 1 -dx[move[2]], move[1] + 1-dy[move[2]])  # x,y -> dx, dy
                self.parking_list[move[0] - dx[move[2]]][move[1] - dy[move[2]]] = self.parking_list[move[0]][move[1]]
                self.parking_list[move[0]][move[1]] = -1

                #self.sendOrder((move[0] + dx[move[2]], move[1] + dy[move[2]], move[0], move[1]))

        else:
            qx, qy = [-1, 1, 0, 0], [0, 0, -1, 1]
            for move in movingStk:
                print(move[0] + 1, move[1] + 1, '->', move[0] + 1 - qx[move[2]],
                      move[1] + 1 - qy[move[2]])  # x,y -> dx, dy
                self.parking_list[move[0] - qx[move[2]]][move[1] - qy[move[2]]] = self.parking_list[move[0]][move[1]]
                self.parking_list[move[0]][move[1]] = -1

        if self.parking_list[size_X - 1][size_Y - 1] == carNum:
            self.parking_list[size_X - 1][size_Y - 1] = -1
            print("%d 차량이 정상적으로 출차되었습니다." % carNum)


    def printCar(self):
        parking_list = self.parking_list
        for i in range(len(parking_list)):
            for j in range(len(parking_list[0])):
                if parking_list[i][j] != -1:
                    print("Car Number :", parking_list[i][j], "Parking Slot :", "(%d, %d)"%(i,j))

    def parkingAlgorithm(self):
        parking_list = self.parking_list
        x = None
        y = None
        for i in range(len(parking_list)):
            flag = False
            for j in range(len(parking_list[0])):
                if parking_list[i][j] == -1:
                    x = i
                    y = j
                    flag = True
                    break
            if flag:
                break

        return x, y

    def sendOrder(self, Des):
        #brick = self.selectBrick()
        brick='brick1'
        con = self.socket_list[brick]

        order = "O,%f,%f,%f,%f" % (Des[0], Des[1], Des[2], Des[3])  # x,y 에서 Dx,Dy로 진행

        con.sendall(order.encode('utf-8'))

        self.brick_list[brick] = True
        print('send')


    def sendCurrentPoint(self):
        sleep(1)

        while True:
            point = self.hedge.position()
            print(point)
            try:
                if point[0] == 5:
                    client = self.socket_list["brick2"]
                elif point[0] == 6:
                    client = self.socket_list["brick1"]

                cur = "C,%f,%f,%f" % (point[1], point[2], point[5])
                print(cur)
                client.sendall(cur.encode('utf-8'))
                sleep(1)

            except KeyError:
                pass

    def handle_receive(self, client_socket, addr, user):
        while True:
            data = client_socket.recv(1024)
            command = data.decode('utf-8').split(',')

            if command[0] == 'D':  # Done
                brick = command[1]
                brick_list[brick] = False

            # elif command[0] ==

    def handle_notice(self, client_socket, addr, user):
        pass

    def server_send_user(self):
        while True:
            command = input()
            if command[0] == 'A':
                string = command[1:]
                for con in self.socket_list.values():
                    con.sendall(string.encode('utf-8'))

            elif command[0] == 'U':
                idx = command.find(' ', 2)
                client_socket = socket_list[command[2:idx]]
                client_socket.sendall(command[idx + 1:])

            elif command[0] == 'S':
                print(self.qq)

    def setHedge(self):

        hedge = MarvelmindHedge(tty="COM3", debug=False)  # create MarvelmindHedge thread
        hedge.start()
        #########################
        self.hedge = hedge
        #########################


    def connect(self):
        # IPv4 체계, TCP 타입 소켓 객체를 생성
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 포트를 사용 중 일때 에러를 해결하기 위한 구문
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # ip주소와 port번호를 함께 socket에 바인드 한다.
        # #포트의 범위는 1-65535 사이의 숫자를 사용할 수 있다.
        server_socket.bind((host, port))
        # 서버가 최대 5개의 클라이언트의 접속을 허용한다.
        server_socket.listen(5)

        cnt = 0
        while cnt != 1:         # 연결할 로봇 수
            try:
                # 클라이언트 함수가 접속하면 새로운 소켓을 반환한다.
                client_socket, addr = server_socket.accept()
            except KeyboardInterrupt:
                for user, con in socket_list:
                    con.close()
                    server_socket.close()
                    print("Keyboard interrupt")
                    break
            cnt += 1

            user = client_socket.recv(1024)
            print("Connected robot '%s' " % (user.decode('utf-8')))
            user = user.decode('utf-8')

            self.socket_list[user] = client_socket
            self.brick_list[user] = False
            # accept()함수로 입력만 받아주고 이후 알고리즘은 핸들러에게 맡긴다.

            if user == "brick1":
                hedgeAdr = Hedge.brick1     #Hedge Adrress
            elif user == "brick2":
                hedgeAdr = Hedge.brick2
            else:
                hedgeAdr = None


            #notice_thread = threading.Thread(target=self.handle_notice, args=(client_socket, addr, user))
            receive_thread = threading.Thread(target=self.handle_receive, args=(client_socket, addr, user))
            # send_thread = threading.Thread(target=self.server_send_user)
            CurPoint_thread = threading.Thread(target=self.sendCurrentPoint, args=())


            #notice_thread.daemon = False
            receive_thread.daemon = False
            CurPoint_thread.daemon = False
            # send_thread.daemon = False

            #notice_thread.start()
            receive_thread.start()
            CurPoint_thread.start()
            # send_thread.start()


if __name__ == '__main__':
    a = Controller()
    #a.connect()
    #a.setHedge()
    #print("setHedge")
    #a.sendOrder([1,1,2.5, 8.2])

    command = None
    #a.parking_list = [[2,3,1],[7,-1,-1],[4,5,6],[8,-1,-1],[9,-1,-1]]
    a.parking_list = [[-1,-1,-1,-1,-1],[1111,-1,-1,-1,2222],[-1,-1,3333,-1,6666],[-1,-1,7777,-1,-1],[-1,-1,-1,-1,4444],[5555,-1,-1,-1,-1],
                      [-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1],]
    #a.outputCar(1)
    while command != 'q':
        print("Menu( q : QUIT)\n"
              "1 : 입차\n"
              "2 : (X,Y)에 주차\n"
              "3 : 출차\n"
              "4 : 주차된 차량 리스트 출력")
        command = input("Select : ")
        if command == '1':
            carNum = int(input("차량 번호 입력(4자리) : "))
            a.inputCar(carNum)
        elif command == '2':
            carNum = int(input("차량 번호 입력(4자리) : "))
            x, y = input("희망 좌표 입력(x,y) : ").split()
            x = int(x)
            y = int(y)
            a.inputCarXY(carNum, x, y)
        elif command == '3':
            carNum = int(input("차량 번호 입력(4자리) : "))
            a.outputCar(carNum)
        elif command == '4':
            a.printCar()
        else:
            print("error")


