echo "Stopping cv services"
sudo systemctl stop upload.service
echo "Killed all cv services"
sleep 3
echo " Starting cv services"
sudo systemctl start upload.service
echo "Finished restart procedure"

