from machine import Pin, time_pulse_us
from time import sleep_ms

# GPIO setup
signalpin = Pin(20, Pin.IN, Pin.PULL_UP)
LED = Pin(22, Pin.OUT)

# Threshold for water detection (µs)
threshhold = 30000  


def periodcalc():
    """Measure pulse high/low duration from sensor pin."""
    high = time_pulse_us(signalpin, 1, 100_000)
    low = time_pulse_us(signalpin, 0, 100_000)
    return high, low


def main_loop():
    """Continuously monitor water level and update LED."""
    while True:
        high, low = periodcalc()

        if high > threshhold:
            # No water (LED off)
            LED.value(0)
        else:
            # Water present (LED on)
            LED.value(1)

        print("high", high, "low", low)
        sleep_ms(200)


if __name__ == "__main__":
    # Run standalone if executed directly
    try:
        main_loop()
    except KeyboardInterrupt:
        print("Exiting water monitor...")
