# -*- coding:utf-8 -*-
import threading

import SocketServer, SocketClient
import Motor
import time


# 스레드에서 동작할 부분.
# 사용자에게 화면을 계속 출력하기 위해 스레드에서 실행.
def work():
    # 현재 작업중이란걸 판단해줄 변수
    global working
    # 사용자에게 출력할 text를 담은 변수
    global text
    try:
        # 현재 작업 실행을 하고있지 않다면 실행. 중복실행 방지.
        if not working:
            # 현재 작업중이란걸 알려주기 위해. 중복실행 방지.
            working = True

    # 작업이 멈추지 않도록 처리.
    except Exception as e:
        print(e)
    # 데이터 초기화 후 working을 false로 줘서 실행이 가능하도록 함.
    finally:
        working = False


# 메인 진입점.
if __name__ == "__main__":
    # 소켓 서버 실행. 백그라운드에서 계속 데이터를 받아올것임.
    ss = SocketServer.SocketServer(9999)
    server_thread = threading.Thread(target=ss.start)
    server_thread.daemon = True
    server_thread.start()

    # django conn
    #ss2 = SocketServer.SocketServer(9998)
    client_django = SocketClient.SocketClient()
    django_thread = threading.Thread(target=client_django.start, args=("192.168.0.34", 9998))
    django_thread.daemon = True
    django_thread.start()
    
    
    try:
        # 변수 초기화.
        working = False
        # 클라이언트가 작업 종료를 지시한 후에도 프로그램이 종료되지 않고 대기상태에 들어갈 수 있도록 하기 위함.
        while True:
            # 소켓 통신으로 데이터 들어올때까지 실행안함.
            while not ss.data:
                pass
            # 클라이언트가 서버 종료를 지시하기 전까지 계속 반복.
            while ss.server_state:
                if ss.data:
                    now_data = ss.data.pop()
                    print("받은 데이터 :", now_data)
                    
                    if now_data == "start":
                        motor = Motor.Motor()
                        motor.socket = client_django
                        print("start 작업 부분")
                        # motor start
                        motor.speed = 50
                        thread = threading.Thread(target=motor.motor)
                        thread.daemon = True
                        thread.start()
                    elif now_data == "stop":
                        print("stop 작업 부분")
                        motor.speed = 0
                        motor.exit_event.set()
                        del motor
                    elif now_data == "speedUp":
                        print("speedUp 작업 부분")
                        motor.addSpeed(10)
                    elif now_data == "speedDown":
                        print("speedDown 작업 부분")
                        motor.addSpeed(-10)
                    elif now_data == "test":
                        motor = Motor.Motor()
                        thread = threading.Thread(target=motor.motor)
                        thread.daemon = True
                        thread.start()
                        print("speed : 100")
                        motor.speed = 100
                        time.sleep(5)
                        print("speed : 30")
                        motor.speed = 30
                        time.sleep(5)
                        print("speed : 0")
                        motor.speed = 0
                        time.sleep(5)
                        motor.exit_event.set()
                        del motor
                        print("테스트 성공")

            # 클라이언트가 대기 명령을 보낸 후 종료 작업.
            ss.data = []
            print("대기")
    except KeyboardInterrupt as e:
        print("error1")
        motor.speed = 0
        motor.exit_event.set()
        exit()
