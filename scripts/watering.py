

import time
import logging
from pump import Pump
from utils import load_yaml, setup_logging
from mqtt_integration import MqttIntegration


if __name__ == "__main__":
    settings = load_yaml("configs/settings.yaml")
    setup_logging(settings=settings)
    
    try:
        pump = Pump(pin=settings["pump"]["pin"])
        mqtt_integration = MqttIntegration.from_settings(settings, pump)
        
        if mqtt_integration:
            mqtt_integration.start()
            logging.info("MQTT integration started. Waiting for commands...")
            
            # Keep the process running
            while True:
                time.sleep(60)
        else:
            logging.error("MQTT integration not enabled in settings.")
            
    except KeyboardInterrupt:
        logging.info("Shutting down...")
    finally:
        if "mqtt_integration" in locals() and mqtt_integration:
            mqtt_integration.stop()
        logging.info("Program ended.")
        