#!/bin/bash

# Request root access
sudo echo "Root access granted"

# Setup dependencies
sudo apt install python3 python3-venv

# Set variables
PROJECT_DIR="/home/$(whoami)/.config/totp-auth"
VENV_DIR="${PROJECT_DIR}/venv"

# Create project directory
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Setup virtual environment
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip3 install totp-auth

# Create systemd service file
cat <<EOF | sudo tee /etc/systemd/system/totp-auth.service > /dev/null
[Unit]
Description=TOTP Auth Service
After=network.target

[Service]
User=$(whoami)
WorkingDirectory=$PROJECT_DIR
ExecStart=$VENV_DIR/bin/totp-auth run
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and start the service
sudo systemctl daemon-reload
sudo systemctl enable totp-auth
sudo systemctl start totp-auth

# Symlink for script
sudo ln -s $VENV_DIR/bin/totp-auth /usr/bin/totp-auth
