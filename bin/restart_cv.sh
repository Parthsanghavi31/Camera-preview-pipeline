echo "Stopping cv services"
sudo systemctl stop camera-preview.service
echo "Killed all cv services"
sleep 3
echo " Starting cv services"
sudo systemctl start camera-preview.service
echo "Finished restart procedure"

