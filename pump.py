import logging
import time

class Pump:
    def __init__(self, pin):
        try:
            import RPi.GPIO as GPIO
            logging.info("Running live..")
        except ImportError:
            logging.info("Running against GPIO.Mock")
            import Mock.GPIO as GPIO
        self.GPIO = GPIO
        self.pin = pin
        self.GPIO.setmode(self.GPIO.BCM)
        self.GPIO.setup(self.pin, self.GPIO.OUT)
        self.GPIO.output([self.pin], self.GPIO.LOW)
        logging.info("Pump initialized.")

    def activate(self, duration):
        try:
            logging.info(f"Pump ON for {duration} seconds")
            self.GPIO.output([self.pin], self.GPIO.HIGH)
            time.sleep(duration)
            self.GPIO.output([self.pin], self.GPIO.LOW)
            logging.info("Pump OFF")
        except Exception as e:
            logging.error("Pump Error: " + str(e))
    
    def __del__(self):
        self.GPIO.cleanup()