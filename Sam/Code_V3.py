import pigpio
import time

# GPIO pins
PAN_PIN = 16
TILT_PIN = 20

# Pulse width range (microseconds)
PAN_MIN = 1000
PAN_MAX = 2500
TILT_MIN = 1300
TILT_MAX = 2500


STEPS= 500
BASE_DELAY=.01
MIN_DELAY= .005

confidence= 0
# Start pigpio and connect to the daemon
pi = pigpio.pi()
if not pi.connected:
    print("Failed to connect to pigpio daemon.")
    exit()

# Initialize to center
x = 2500
y = 1600
SCAN_STEP = 100

current_pan = x
current_tilt = y

def move_pan(us):
    global current_pan
    us = max(PAN_MIN, min(PAN_MAX, int(us)))
    pi.set_servo_pulsewidth(PAN_PIN, us)
    current_pan = us

def move_tilt(us):
    global current_tilt
    us = max(TILT_MIN, min(TILT_MAX, int(us)))
    pi.set_servo_pulsewidth(TILT_PIN, us)
    current_tilt = us
        

def smooth_move_timed(target_pan, target_tilt, steps=500, min_delay=0.005, max_delay=0.02):
    global current_pan, current_tilt

    start_pan = current_pan
    start_tilt = current_tilt
    delta_pan = target_pan - start_pan
    delta_tilt = target_tilt - start_tilt

    def delay_ease(t):
        return (2 * t - 1) ** 2  # Slow start/end, fast middle (parabolic)

    for i in range(steps + 1):
        t = i / steps
        new_pan = start_pan + t * delta_pan
        new_tilt = start_tilt + t * delta_tilt

        move_pan(new_pan)
        move_tilt(new_tilt)

        delay = min_delay + (max_delay - min_delay) * delay_ease(t)
        time.sleep(delay)

    
    move_pan(target_pan)
    move_tilt(target_tilt)
    current_pan = target_pan
    current_tilt = target_tilt
    
    
def cat_detected(confidence):
    if(confidence <= .8):
        return true
    else:
        return false

def idle_scan():
    direction =1
    while (not cat_detected()):
        next_pos = current_pan + SCAN_STEP * direction
        if (next_pos >= PAN_MAX or next_pos <= PAN_MIN):
            direction *= -1
            next_pos = max(PAN_MIN, min(PAN_MAX, next_pos))
        move_pan(next_pos)
        time.sleep(.05)
        
        
move_pan(x)
move_tilt(y)


try:
    while True:
        
        
        
        x = int(input("Enter target PAN (us 500–2500): "))
        y = int(input("Enter target TILT (us 500–1600): "))
        
        move_pan(x)
        move_tilt(y)
        #smooth_move_timed(x,y)
        
    while (0):
        #this code essentially lays out the process of how the code will flow through the processes. integrating with team members code will be durring 405
        if cat_detected():
            print("cat detected!")
            smooth_move_timed(x,y)
            while (cat_detected()):
                move_pan(x)
                move_tilt(y)
            time.sleep(.02)
        else:
            idle_scan()
except KeyboardInterrupt:
    print("Exiting...")

finally:
    pi.set_servo_pulsewidth(PAN_PIN, 0)
    pi.set_servo_pulsewidth(TILT_PIN, 0)
    pi.stop()