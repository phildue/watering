# Watering Controller with MQTT and Home Assistant Integration

A Raspberry Pi-based watering system controller with MQTT support and automatic Home Assistant discovery.

## Features

- Schedule-based watering via cron-like configuration
- MQTT control and status reporting
- Home Assistant auto-discovery
- Docker deployment with built-in Mosquitto broker
- Mock GPIO for local testing (non-Pi environments)

## Quick Start (Raspberry Pi)

### Using Docker (Recommended)

1. **Clone and configure**
   ```bash
   git clone <this-repo>
   cd watering
   # Edit configs/settings.yaml if needed (default settings work for Docker deployment)
   ```

2. **Run with Docker**
   ```bash
   docker network create watering-net
   
   # Start Mosquitto MQTT broker
   docker run -d --name mosquitto \
     --restart unless-stopped \
     --network watering-net \
     -p 1883:1883 \
     -v $(pwd)/configs/mosquitto.conf:/mosquitto/config/mosquitto.conf:ro \
     -v mosquitto-data:/mosquitto/data \
     eclipse-mosquitto:2
   
   # Build and run watering controller
   docker build -t watering-controller .
   docker run -d --name watering-controller \
     --restart unless-stopped \
     --network watering-net \
     --privileged \
     --device /dev/gpiomem:/dev/gpiomem \
     -v $(pwd)/configs/settings.yaml:/app/configs/settings.yaml:ro \
     -e TZ=UTC \
     watering-controller
   ```

3. **Check logs**
   ```bash
   docker logs -f watering-controller
   ```

### Using Systemd Service

1. **Install dependencies**
   ```bash
   # Create conda environment
   conda env create -f environment.yaml
   conda activate watering
   ```

2. **Install as service**
   ```bash
   ./setup_as_service.sh
   sudo systemctl start watering
   sudo systemctl status watering
   ```

## Home Assistant Integration

### Connection to Local Docker MQTT Broker

1. **In Home Assistant, go to Settings → Devices & Services → Integrations**

2. **Add MQTT Integration**
   - Click "Add Integration"
   - Search for "MQTT"
   - Configure connection:
     - **Broker**: `<raspberry-pi-ip>` (or `localhost` if HA is on same device)
     - **Port**: `1883`
     - **Username**: (leave blank if using default mosquitto.conf)
     - **Password**: (leave blank if using default mosquitto.conf)

3. **Discovery should be automatic**
   - A "Watering Pump" switch should appear under MQTT devices
   - Device name: "Watering Controller"
   - You'll see availability status and can control the pump

### Connection to Existing MQTT Broker

If you already have an MQTT broker in Home Assistant:

1. **Update settings.yaml**
   ```yaml
   mqtt:
     enabled: true
     host: "<your-mqtt-broker-ip>"
     port: 1883
     username: "your-username"  # if required
     password: "your-password"  # if required
     base_topic: "watering"
     client_id: "watering-controller"
     discovery: true
     discovery_prefix: "homeassistant"
   ```

2. **Skip running the mosquitto container**
   - Only run the watering-controller container
   - Remove `--network watering-net` if not using the included broker

### Home Assistant Entity

Once connected, you can:

- **Turn pump on/off** via the switch entity
- **Set duration** by publishing to `watering/pump/command`:
  - `ON` - runs for default duration (10 seconds)
  - `15` - runs for 15 seconds
  - `{"state":"ON","duration":20}` - runs for 20 seconds
- **View status** on the `watering/pump/state` topic (ON/OFF)
- **Check availability** on the `watering/availability` topic (online/offline)
- **See last run** on the `watering/last_run` topic (ISO timestamp)

### Automations Example

```yaml
automation:
  - alias: "Water plants at sunset"
    trigger:
      - platform: sun
        event: sunset
    action:
      - service: mqtt.publish
        data:
          topic: "watering/pump/command"
          payload: "30"  # 30 seconds
```

## Configuration

### config.yaml - Watering Schedule

```yaml
schedule:
  - weekday: "all"     # mon, tue, wed, thu, fri, sat, sun, or "all"
    time: "18:15"      # HH:MM format
    duration: 30       # seconds
  - weekday: "mon"
    time: "08:00"
    duration: 45
```

### settings.yaml - System Settings

```yaml
logging:
  file: "watering.log"

pump:
  pin: 17                  # BCM GPIO pin number
  default_duration: 10     # default seconds for MQTT ON command

mqtt:
  enabled: true
  host: "mosquitto"        # or IP of your MQTT broker
  port: 1883
  username: null           # set if your broker requires auth
  password: null
  base_topic: "watering"
  client_id: "watering-controller"
  discovery: true          # Home Assistant auto-discovery
  discovery_prefix: "homeassistant"
```

## MQTT Topics

| Topic | Direction | Description |
|-------|-----------|-------------|
| `watering/pump/command` | Subscribe | Control pump (ON, OFF, integer seconds, or JSON) |
| `watering/pump/state` | Publish | Current state (ON/OFF) |
| `watering/availability` | Publish | Controller status (online/offline) |
| `watering/last_run` | Publish | ISO timestamp of last activation |
| `homeassistant/switch/watering_pump/config` | Publish | Auto-discovery config (retained) |

## Testing Locally (Non-Raspberry Pi)

The controller includes a FakeGPIO fallback for testing on non-Pi hardware:

```bash
# Start local test environment
docker network create watering-net

docker run -d --name mosquitto \
  --network watering-net \
  -p 1883:1883 \
  -v $(pwd)/configs/mosquitto.conf:/mosquitto/config/mosquitto.conf:ro \
  eclipse-mosquitto:2

docker build -t watering-controller .
docker run -d --name watering-controller \
  --network watering-net \
  -v $(pwd)/configs/settings.yaml:/app/configs/settings.yaml:ro \
  watering-controller

# Test pump control
docker run --rm --network watering-net eclipse-mosquitto:2 \
  mosquitto_pub -h mosquitto -t watering/pump/command -m 5

# Check logs
docker logs -f watering-controller

# Clean up
docker rm -f watering-controller mosquitto
docker network rm watering-net
```

## Troubleshooting

### Controller won't start
```bash
docker logs watering-controller
# Check for GPIO permissions or config file issues
```

### MQTT not connecting
```bash
docker logs mosquitto
# Verify mosquitto is running and accessible
# Check settings.yaml has correct host/port
```

### Home Assistant not discovering device
- Verify MQTT integration is configured in HA
- Check discovery is enabled in settings.yaml
- Restart the controller to republish discovery config
- Check HA MQTT integration logs

### GPIO Permission Denied
```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER

# Or run container with --privileged flag (Docker)
```

## Hardware Setup

Connect your pump relay to:
- **GPIO Pin 17** (BCM numbering, configurable in settings.yaml)
- **Ground**
- **5V or 3.3V** depending on relay module

Most relay modules are active-low:
- `GPIO.HIGH` = relay OFF (default state)
- `GPIO.LOW` = relay ON (pump running)

## License

MIT
