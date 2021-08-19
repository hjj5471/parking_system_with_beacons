import socket
import argparse
import threading
import time


host = "192.168.200.143"
port = 9999
user_list = {}
notice_flag = 0


class Controller:
    qq = 0

    def handle_receive(self, client_socket, addr, user):
        while True:
            data = client_socket.recv(1024)
            string = data.decode('utf-8')
            if string == "/종료":
                break
            self.qq = "%s : %s" % (user, string)
            for con in user_list.values():
                try:
                    con.sendall(string.encode('utf-8'))
                except:
                    print("연결이 비 정상적으로 종료된 소켓 발견")
        del user_list[user]
        client_socket.close()

    def handle_notice(self, client_socket, addr, user):
        pass

    def server_send_user(self):
        while True:
            command = input()
            if command[0] == 'A':
                string = command[1:]
                for con in user_list.values():
                    con.sendall(string.encode('utf-8'))

            elif command[0] == 'U':
                idx = command.find(' ', 2)
                client_socket = user_list[command[2:idx]]
                client_socket.sendall(command[idx + 1:])

            elif command[0] == 'S':
               print(self.qq)

    def accept_func(self):
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
        while cnt != 1:
            try:
                # 클라이언트 함수가 접속하면 새로운 소켓을 반환한다.
                client_socket, addr = server_socket.accept()
            except KeyboardInterrupt:
                for user, con in user_list:
                    con.close()
                    server_socket.close()
                    print("Keyboard interrupt")
                    break
            cnt += 1

            user = client_socket.recv(1024)
            print("Connected user '%s' " % (user.decode('utf-8')))
            user = user.decode('utf-8')

            user_list[user] = client_socket
            # accept()함수로 입력만 받아주고 이후 알고리즘은 핸들러에게 맡긴다.

            notice_thread = threading.Thread(target=self.handle_notice, args=(client_socket, addr, user))
            receive_thread = threading.Thread(target=self.handle_receive, args=(client_socket, addr, user))
            send_thread = threading.Thread(target=self.server_send_user)

            notice_thread.daemon = False
            receive_thread.daemon = False
            send_thread.daemon = False

            notice_thread.start()
            receive_thread.start()
            send_thread.start()



if __name__ == '__main__':
    a = Controller()

    a.accept_func()

