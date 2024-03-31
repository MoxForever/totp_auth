#!/bin/bash

# Setup dependencies
apt install python3 python3-venv

# Set variables
PROJECT_DIR="/home/$(whoami)/.config/"
VENV_DIR="${PROJECT_DIR}/venv"

# Create project directory
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR" || exit

# Create virtual environment
python3 -m venv "$VENV_DIR"

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install TOTP Auth
pip install totp-auth

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

# Save to PATH
export PATH="$VENV_DIR/bin:$PATH"
source ~/.bashrc
