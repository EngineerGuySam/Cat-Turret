#
import time

import RPi.GPIO as GPIO

 

pump = "pin number for pump"

solenoid = "pin nuber for solenoid"

 

def initialize(): #initialize pins for water pump and solenoid

   

    GPIO.setmode(GPIO.BCM)

    GPIO.setup(pump, GPIO.OUT, initial=GPIO.LOW)

    GPIO.setup(solenoid, GPIO.OUT, initial=GPIO.LOW)

   

    print("Initializing water system")

 

def activate(duration=3, delay_before_spray=1): #3 seconds might be a bit much lmao

 

    print("Starting water pump...")

    GPIO.output(pump, GPIO.HIGH)

 

    time.sleep(delay_before_spray)

    print("Pause 1 second")

    GPIO.output(solenoid, GPIO.HIGH)

 

    time.sleep(duration) #stay on for 3 seconds

   

    print("Stopping pump") #turn off pump first

    GPIO.output(pump, GPIO.LOW)

 

    print("Stopping solenoid") #close solenoid

    GPIO.output(solenoid, GPIO.LOW)

 

def cleanup(): #cleanup pins casuse thats what sophia told me to do with the 4B

   

    GPIO.cleanup()

    print("Clearing pins")