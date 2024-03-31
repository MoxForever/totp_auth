#!/bin/bash

# Install
apt install python3 pip3
pip3 install totp_auth

# Systemd service
cat <<EOF | sudo tee /etc/systemd/system/totp-auth.service > /dev/null
[Unit]
Description=TOTP Auth Service
After=network.target

[Service]
User=$(whoami)
WorkingDirectory=/home/$(whoami)/.config/totp-auth
ExecStart=python3 -m totp-auth run
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable totp-auth
systemctl start totp-auth
