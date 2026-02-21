try:
    import RPi.GPIO as GPIO
except:
    import Mock.GPIO as GPIO


import time
import yaml
import logging
from datetime import datetime
import threading

# ---- Load Configs ----
def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

config = load_yaml("config.yaml")
settings = load_yaml("settings.yaml")


# ---- Logging Setup ----
log_file = settings["logging"].get("file")
handlers = [logging.StreamHandler()]
if log_file:
    handlers.append(logging.FileHandler(log_file))

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%a %H:%M:%S',
    handlers=handlers
)

# ---- Pump Control ----
def activate_pump(pin, duration):
    try:
        logging.info(f"Pump ON for {duration} seconds")
        GPIO.output([pin], GPIO.HIGH)
        time.sleep(duration)
        GPIO.output([pin], GPIO.LOW)
        logging.info("Pump OFF")
    except Exception as e:
        logging.error("Pump Error: " + str(e))

# ---- Scheduler ----
def run_scheduler():
    pump_pin = settings['gpio']['pin']
    schedule = config['schedule']
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pump_pin, GPIO.OUT)
    GPIO.output([pump_pin], GPIO.LOW)

    already_triggered = set()
    logging.info("Watering scheduler started.")

    try:
        while True:
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            current_day = now.strftime("%a").lower()[:3]

            for task in schedule:
                task_day = task['weekday'].lower()
                task_time = task['time']
                task_id = f"{task_day}-{task_time}"

                if task_day == current_day and task_time == current_time:
                    if task_id not in already_triggered:
                        duration = task['duration']
                        threading.Thread(
                            target=activate_pump, args=(pump_pin, duration), daemon=True
                        ).start()
                        already_triggered.add(task_id)

            if current_time == "00:00":
                already_triggered.clear()

            time.sleep(1)

    except KeyboardInterrupt:
        logging.info("Scheduler stopped.")
    finally:
        GPIO.cleanup()
        logging.info("GPIO cleaned up.")


if __name__ == "__main__":
    run_scheduler()