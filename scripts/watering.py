

import time
import logging
from pump import Pump
from utils import load_yaml, setup_logging
from mqtt_server import MqttServer


if __name__ == "__main__":
    settings = load_yaml("configs/settings.yaml")
    setup_logging(settings=settings)
    
    try:
        pump = Pump(pin=settings["pump"]["pin"])
        mqtt_server = MqttServer.from_settings(settings, pump)
        
        if mqtt_server:
            mqtt_server.start()
            logging.info("MQTT integration started. Waiting for commands...")
            
            # Keep the process running
            while True:
                time.sleep(60)
        else:
            logging.error("MQTT integration not enabled in settings.")
            
    except KeyboardInterrupt:
        logging.info("Shutting down...")
    finally:
        if "mqtt_server" in locals() and mqtt_server:
            mqtt_server.stop()
        logging.info("Program ended.")
        