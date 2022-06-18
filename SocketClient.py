# 소켓을 사용하기 위해서는 socket을 import해야 한다.
import socket, threading
from datetime import datetime


class SocketClient:
    def __init__(self):
        self.client_socket = None

    # 데이터를 전송합니다.
    def send_data(self, data):
        # 바이너리(byte)형식으로 변환한다.
        data = data.encode()
        # 바이너리의 데이터 사이즈를 구한다.
        length = len(data)
        # 데이터 사이즈를 little 엔디언 형식으로 byte로 변환한 다음 전송한다.
        self.client_socket.sendall(length.to_bytes(4, byteorder='little'))
        # 데이터를 클라이언트로 전송한다.
        self.client_socket.sendall(data)

        data = self.client_socket.recv(4)
        # 최초 4바이트는 전송할 데이터의 크기이다. 그 크기는 little big 엔디언으로 byte에서 int형식으로 변환한다.
        # C#의 BitConverter는 big엔디언으로 처리된다.
        length = int.from_bytes(data, "little")
        # 다시 데이터를 수신한다.
        data = self.client_socket.recv(length)
        # 수신된 데이터를 str형식으로 decode한다.
        msg = data.decode()
        print(msg)

    def stop(self):
        # 소켓을 닫습니다.
        self.client_socket.close()

    # 서버의 주소, 연결할 포트를 설정.
    def start(self, host='127.0.0.1', port=9999):
        # 소켓 객체를 생성합니다.
        # 주소 체계(address family)로 IPv4, 소켓 타입으로 TCP 사용합니다.
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # 지정한 HOST와 PORT를 사용하여 서버에 접속합니다.
            self.client_socket.connect((host, port))
        # 예외 발생시 연결 종료
        except Exception as e:
            self.client_socket.close()


if __name__ == "__main__":
    client1 = SocketClient()
    client1.start("localhost", 9999)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = now + " " + str(100)
    client1.send_data(data)

    client2 = SocketClient()
    client2.start("localhost", 9998)
    data = "client2"
    client2.send_data(data)

    client1.stop()
    client2.stop()


