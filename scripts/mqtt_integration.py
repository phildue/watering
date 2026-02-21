import json
import logging
import threading
from datetime import datetime
from typing import Optional

import paho.mqtt.client as mqtt


class MqttIntegration:
    def __init__(
        self,
        host: str,
        port: int,
        base_topic: str,
        client_id: str,
        username: Optional[str],
        password: Optional[str],
        discovery: bool,
        discovery_prefix: str,
        default_duration: int,
        pump,
    ):
        self.host = host
        self.port = port
        self.base_topic = base_topic.rstrip("/")
        self.client_id = client_id
        self.username = username
        self.password = password
        self.discovery = discovery
        self.discovery_prefix = discovery_prefix.rstrip("/")
        self.default_duration = default_duration
        self.pump = pump

        self._client = None
        self._lock = threading.Lock()

        self.command_topic = f"{self.base_topic}/pump/command"
        self.state_topic = f"{self.base_topic}/pump/state"
        self.availability_topic = f"{self.base_topic}/availability"
        self.last_run_topic = f"{self.base_topic}/last_run"

    @classmethod
    def from_settings(cls, settings, pump):
        mqtt_settings = settings.get("mqtt", {})
        if not mqtt_settings.get("enabled", False):
            return None

        return cls(
            host=mqtt_settings.get("host", "localhost"),
            port=int(mqtt_settings.get("port", 1883)),
            base_topic=mqtt_settings.get("base_topic", "watering"),
            client_id=mqtt_settings.get("client_id", "watering-controller"),
            username=mqtt_settings.get("username"),
            password=mqtt_settings.get("password"),
            discovery=bool(mqtt_settings.get("discovery", True)),
            discovery_prefix=mqtt_settings.get("discovery_prefix", "homeassistant"),
            default_duration=int(settings.get("pump", {}).get("default_duration", 10)),
            pump=pump,
        )

    def start(self):
        self._client = mqtt.Client(client_id=self.client_id, clean_session=True)
        if self.username:
            self._client.username_pw_set(self.username, self.password or "")

        self._client.will_set(self.availability_topic, payload="offline", retain=True)
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.on_disconnect = self._on_disconnect

        logging.info("Connecting to MQTT broker %s:%s", self.host, self.port)
        self._client.connect(self.host, self.port, keepalive=60)
        self._client.loop_start()

    def stop(self):
        if not self._client:
            return
        self._client.publish(self.availability_topic, "offline", retain=True)
        self._client.loop_stop()
        self._client.disconnect()

    def state_callback(self, state: str):
        if not self._client:
            return
        self._client.publish(self.state_topic, state, retain=True)
        if state == "ON":
            self._client.publish(
                self.last_run_topic,
                datetime.now().isoformat(timespec="seconds"),
                retain=True,
            )

    def _on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            logging.error("MQTT connection failed with code %s", rc)
            return
        logging.info("MQTT connected.")
        client.subscribe(self.command_topic)
        client.publish(self.availability_topic, "online", retain=True)

        if self.discovery:
            self._publish_discovery_config(client)

    def _on_disconnect(self, client, userdata, rc):
        if rc != 0:
            logging.warning("MQTT disconnected unexpectedly with code %s", rc)
        else:
            logging.info("MQTT disconnected.")

    def _on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8").strip()
        duration = self._parse_duration(payload)
        if duration is None:
            logging.warning("MQTT command ignored: %s", payload)
            return

        with self._lock:
            threading.Thread(
                target=self.pump.activate,
                args=(duration, self.state_callback),
                daemon=True,
            ).start()

    def _parse_duration(self, payload: str) -> Optional[int]:
        if not payload:
            return None

        if payload.upper() == "ON":
            return self.default_duration

        if payload.upper() == "OFF":
            return None

        try:
            value = int(payload)
            return max(1, value)
        except ValueError:
            pass

        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            return None

        if isinstance(data, dict):
            state = str(data.get("state", "ON")).upper()
            if state != "ON":
                return None
            duration = data.get("duration", self.default_duration)
            try:
                duration = int(duration)
            except (TypeError, ValueError):
                return None
            return max(1, duration)

        return None

    def _publish_discovery_config(self, client):
        object_id = "watering_pump"
        config_topic = f"{self.discovery_prefix}/switch/{object_id}/config"
        device = {
            "identifiers": ["watering_controller"],
            "name": "Watering Controller",
            "manufacturer": "Custom",
            "model": "GPIO Pump",
        }
        payload = {
            "name": "Watering Pump",
            "unique_id": "watering_pump_switch",
            "command_topic": self.command_topic,
            "state_topic": self.state_topic,
            "availability_topic": self.availability_topic,
            "payload_on": "ON",
            "payload_off": "OFF",
            "device": device,
        }
        client.publish(config_topic, json.dumps(payload), retain=True)
