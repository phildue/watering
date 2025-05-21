

import time
import logging
from datetime import datetime
import threading
from pump import Pump
from utils import load_yaml, setup_logging

        
# ---- Scheduler ----
def run_scheduler(pump: Pump):
    already_triggered = set()
    logging.info("Watering scheduler started.")

    while True:
        config = load_yaml("config.yaml")
        schedule = config['schedule']
        
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        current_day = now.strftime("%a").lower()[:3]

        for task in schedule:
            task_day = task['weekday'].lower()
            task_time = task['time']
            task_id = f"{task_day}-{task_time}"

            if task_day == current_day or task_day == 'all' and task_time == current_time:
                if task_id not in already_triggered:
                    duration = task['duration']
                    threading.Thread(
                        target=pump.activate, args=(duration,), daemon=True
                    ).start()
                already_triggered.add(task_id)

        if current_time == "00:00":
            already_triggered.clear()

        time.sleep(30)




if __name__ == "__main__":
    settings = load_yaml("settings.yaml")
    setup_logging(settings=settings)
    try:
        pump = Pump(pin=settings["pump"]["pin"])
        run_scheduler(pump = pump)
    except KeyboardInterrupt:
        logging.info("Scheduler stopped.")
    finally:
        logging.info("Program ended.")
        