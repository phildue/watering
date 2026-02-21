import RPi.GPIO as GPIO
import time

RELAIS_1_GPIO = 17  # Beispiel-Pin, anpassen falls nötig

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAIS_1_GPIO, GPIO.OUT)

try:
    while True:
        GPIO.output(RELAIS_1_GPIO, GPIO.LOW)  # aus
        time.sleep(5)  # 1 Sekunde warten
        GPIO.output(RELAIS_1_GPIO, GPIO.HIGH)  # an
        time.sleep(5)  # 1 Sekunde warten
except KeyboardInterrupt:
    print("Beendet durch Benutzer")
finally:
    GPIO.cleanup()
