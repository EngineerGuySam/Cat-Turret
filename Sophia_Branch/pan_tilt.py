import pigpio
import time

# GPIO pins
PAN_PIN = 12
TILT_PIN = 17

# Pulse width range (microseconds)
PAN_MIN = 500
PAN_MAX = 2500
TILT_MIN = 500
TILT_MAX = 1600

# Motion parameters
STEPS = 500
BASE_DELAY = 0.01
MIN_DELAY = 0.005

# Start pigpio and connect to the daemon
pi = pigpio.pi()
if not pi.connected:
    print("Failed to connect to pigpio daemon.")
    exit()

# Initialize to center
current_pan = 1500
current_tilt = 1000
SCAN_STEP = 100


def move_pan(us: int):
    """Move pan servo to specified pulse width (µs)."""
    global current_pan
    us = max(PAN_MIN, min(PAN_MAX, int(us)))
    pi.set_servo_pulsewidth(PAN_PIN, us)
    current_pan = us


def move_tilt(us: int):
    """Move tilt servo to specified pulse width (µs)."""
    global current_tilt
    us = max(TILT_MIN, min(TILT_MAX, int(us)))
    pi.set_servo_pulsewidth(TILT_PIN, us)
    current_tilt = us


def smooth_move_timed(target_pan, target_tilt, steps=500, min_delay=0.005, max_delay=0.02):
    """Smoothly move from current position to target pan/tilt using easing."""
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

    # Snap to final target
    move_pan(target_pan)
    move_tilt(target_tilt)
    current_pan = target_pan
    current_tilt = target_tilt


def idle_scan():
    """Sweep back and forth until interrupted (used when no cat is detected)."""
    global current_pan
    direction = 1
    while True:
        next_pos = current_pan + SCAN_STEP * direction
        if next_pos >= PAN_MAX or next_pos <= PAN_MIN:
            direction *= -1
            next_pos = max(PAN_MIN, min(PAN_MAX, next_pos))
        move_pan(next_pos)
        time.sleep(0.05)


def cleanup():
    """Stop PWM and release servos."""
    pi.set_servo_pulsewidth(PAN_PIN, 0)
    pi.set_servo_pulsewidth(TILT_PIN, 0)
    pi.stop()


if __name__ == "__main__":
    try:
        while True:
            x = int(input("Enter target PAN (µs 500–2500): "))
            y = int(input("Enter target TILT (µs 500–1600): "))
            smooth_move_timed(x, y)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        cleanup()