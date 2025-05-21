import logging
import time
import RPi.GPIO as GPIO
    
class Pump:
    def __init__(self, pin):
        
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.HIGH)
        logging.info(f"Pump initialized on pin [{self.pin}].")

    def activate(self, duration):
        try:
            logging.info(f"Pump ON for {duration} seconds..")
            GPIO.output(self.pin, GPIO.LOW)
            time.sleep(duration)
            GPIO.output(self.pin, GPIO.HIGH)
            logging.info("Pump OFF")
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