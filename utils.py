import yaml
import logging
# ---- Load Configs ----
def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

# ---- Logging Setup ----
def setup_logging(settings):
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
    logging.info("Logging initalized.")
