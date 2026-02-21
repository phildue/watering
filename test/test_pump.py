from utils import load_yaml, setup_logging
import logging

from pump import Pump
if __name__ == "__main__":
    settings = load_yaml("settings.yaml")
    setup_logging(settings=settings)
    try:
        pump = Pump(pin=settings["pump"]["pin"])
        pump.activate(5)  # Activate the pump for 5 seconds
    except KeyboardInterrupt:
        logging.info("Scheduler stopped.")
    finally:
        logging.info("Program ended.")