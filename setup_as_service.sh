#!/bin/bash

SERVICE_NAME="watering"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="${SCRIPT_DIR}/watering.py"
USER_NAME="pi"
PYTHON_PATH="/home/${USER_NAME}/miniforge3/bin/python"

echo "Creating systemd service file at ${SERVICE_FILE}..."

sudo bash -c "cat > ${SERVICE_FILE}" <<EOF
[Unit]
Description=Watering Controller
After=network.target

[Service]
Type=simple
User=${USER_NAME}
WorkingDirectory=${SCRIPT_DIR}
ExecStart=bash -c 'source /home/${USER_NAME}/miniforge3/bin/activate watering && python ${SCRIPT_PATH}'
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Enabling watering service to start on boot..."
sudo systemctl enable ${SERVICE_NAME}.service

echo "You can start the service now with: sudo systemctl start ${SERVICE_NAME}.service"