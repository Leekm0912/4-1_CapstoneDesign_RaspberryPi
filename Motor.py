import spidev, time
import RPi.GPIO as GPIO
import threading
import os
from time import strftime,gmtime
import csv

class Motor:
    def __init__(self):
        self.speed = 50
        GPIO.setmode(GPIO.BCM)
        self.socket = None
        self.channel = 1
        self.spi =spidev.SpiDev()
        self.spi.open(0, 0)
        #spi.max_speed_hz = 1350000
        self.spi.max_speed_hz = 1000000

        self.motor_pin_1 = 22
        self.motor_pin_2 = 27
        self.EN1 = 25 # for pwm
        GPIO.setup(self.motor_pin_1, GPIO.OUT)
        GPIO.setup(self.motor_pin_2, GPIO.OUT)
        GPIO.setup(self.EN1, GPIO.OUT)

        self.pwm1 = GPIO.PWM(self.EN1, 500)
        self.pwm1.start(10)

        self.count = 0
        self.tmp = []

        self.exit_event = threading.Event()
        

    def motor(self):
        def read_vib():
            r = self.spi.xfer2([1, (8+self.channel) << 4, 0])
            adc_out = ((r[1]&3<<8) + r[2])
            return adc_out

        while not self.exit_event.is_set():
            self.pwm1.ChangeDutyCycle(self.speed)
            GPIO.output(self.motor_pin_1, False)
            GPIO.output(self.motor_pin_2, True)
            reading = read_vib()
            voltage = reading*3.3/1024
            #print(f"Reading={reading} Voltage={voltage}")
            self.tmp.append(reading)
            time.sleep(0.01)
            self.count += 1
            if self.count == 100:
                avg = sum(self.tmp) / len(self.tmp)
                print("avg :", avg)
                self.tmp = []
                self.count = 0
                dt_gmt = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                
                # send data to django
                # if dont connect to server, pause this line
                with open("sensor.csv", "a") as f:
                    write = csv.writer(f)
                    write.writerow([dt_gmt, avg])
                self.socket.send_data(dt_gmt + " " + str(avg))
            
        GPIO.output(self.EN1, False)
        self.pwm1.stop()
        GPIO.cleanup()


    def addSpeed(self, speed):
        change_speed = self.speed + speed
        if 0 <= change_speed <= 100:
            self.speed += speed
            print(self.speed)

if __name__ == "__main__":
    motor = Motor()
    thread = threading.Thread(target=motor.motor)
    thread.daemon = True
    thread.start()
    try:
        while True:
            time.sleep(0.1)
            # motor.addSpeed(-10)
            pass
    except KeyboardInterrupt as e:
        print("error2")
        motor.speed = 0
        motor.exit_event.set()
        exit()
            
    
