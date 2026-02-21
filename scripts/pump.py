import logging
import time

try:
    import RPi.GPIO as GPIO
except Exception:
    class _FakeGPIO:
        BCM = "BCM"
        OUT = "OUT"
        HIGH = 1
        LOW = 0

        def setmode(self, mode):
            logging.warning("FakeGPIO setmode(%s)", mode)

        def setup(self, pin, mode):
            logging.warning("FakeGPIO setup(pin=%s, mode=%s)", pin, mode)

        def output(self, pin, value):
            logging.warning("FakeGPIO output(pin=%s, value=%s)", pin, value)

        def cleanup(self):
            logging.warning("FakeGPIO cleanup")

    GPIO = _FakeGPIO()
    logging.warning("Using FakeGPIO; GPIO not available on this device.")
    
class Pump:
    def __init__(self, pin):
        
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.HIGH)
        logging.info(f"Pump initialized on pin [{self.pin}].")

    def activate(self, duration, on_state_change=None):
        try:
            logging.info(f"Pump ON for {duration} seconds..")
            if on_state_change:
                on_state_change("ON")
            GPIO.output(self.pin, GPIO.LOW)
            time.sleep(duration)
            GPIO.output(self.pin, GPIO.HIGH)
            logging.info("Pump OFF")
            if on_state_change:
                on_state_change("OFF")
        except Exception as e:
            logging.error("Pump Error: " + str(e))
    
    def __del__(self):
        GPIO.cleanup()


if __name__ == "__main__":
    try:
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%a %H:%M:%S',
            handlers=[logging.StreamHandler()]
        )
        pump = Pump(pin=17)
        pump.activate(duration=20)  # Activate the pump for 5 seconds
    except KeyboardInterrupt:
        logging.info("Stopped.")
    finally:
        logging.info("Program ended.")