# sudo apt update -y
# sudo apt install rabbitmq-server -y
# sudo rabbitmq-plugins enable rabbitmq_management
# sudo service rabbitmq-server start
# sudo rabbitmqctl add_user nano nano
# sudo rabbitmqctl set_permissions -p / nano ".*" ".*" ".*"
# sudo service rabbitmq-server restart

user=$(whoami)
current_dir=$(pwd)
original_service="[Unit]
Description=camera-preview.service
After=network.target

[Service]
User=${user}
Type=idle
WorkingDirectory=${current_dir}
ExecStartPre=/bin/bash -c 'sudo service nvargus-daemon restart'
ExecStart=/usr/bin/python3 -u main.py
StandardOutput=inherit
StandardError=inherit
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target"

echo "$original_service" > camera-preview.service
sudo mv camera-preview.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable camera-preview.service
sudo systemctl start camera-preview.service
