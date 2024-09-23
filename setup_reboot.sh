#!/bin/bash
sudo apt-get install curl -y
#Set the timezone based on IP address
echo "Setting timezone..."
timezone=$(curl -s http://ip-api.com/line/?fields=timezone)
sudo timedatectl set-timezone "$timezone"

# Enable passwordless sudo for reboot command
echo "Configuring passwordless sudo for reboot..."
user=$(whoami)
sudo sed -i "/^${user} ALL=(ALL) NOPASSWD: \/sbin\/reboot$/d" /etc/sudoers
echo "${user} ALL=(ALL) NOPASSWD: /sbin/reboot" | sudo tee -a /etc/sudoers

# Set up daily reboot at 2 AM using cron
echo "Setting up cron job for daily reboot at 2 AM in root's crontab..."
temp_cron=$(mktemp)
sudo crontab -l > "$temp_cron"
cron_job="0 2 * * * /sbin/reboot"
if ! grep -Fxq "$cron_job" "$temp_cron"; then
    echo "$cron_job" >> "$temp_cron"
fi
sudo crontab "$temp_cron"
rm "$temp_cron"
sudo systemctl restart cron
echo "Configuration complete."
