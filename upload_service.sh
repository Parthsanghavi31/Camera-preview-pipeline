user=$(whoami)
current_dir=$(pwd)
upload_service="[Unit]
Description=upload.service
After=network.target

[Service]
User=${user}
Type=idle
WorkingDirectory=${current_dir}
ExecStart=/usr/bin/python3 -u upload_module.py
StandardOutput=inherit
StandardError=inherit
Restart=always
RestartSec=3600

[Install]
WantedBy=multi-user.target"

echo "$upload_service" > upload.service
sudo mv upload.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable upload.service
sudo systemctl start upload.service
