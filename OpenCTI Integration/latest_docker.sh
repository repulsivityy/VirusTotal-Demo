#!/bin/bash
#
echo "####################"
echo "This script will stop the current OpenCTI Docker, pull the latest docker-compose.yml from github, and spins it up"
echo "Entering (Del) will essentially recreate the entire OpenCTI from scratch with the latest code. Volumes are deleted as well"
echo "####################"
read -p "Shall we continue (Y/N/Del)" choice

while [[ "$choice" != "Y" && "$choice" != "N" && "$choice" != "Del" ]]; do
  echo "Invalid choice. Please enter Y, N, or Del."
  read choice
done

if [ "$choice" == "Y" ]; then
  cd ~/opencti
  echo "Bringing Docker Image Down"
  sudo docker compose down
  echo "Downloading latest YML file"
  wget -O docker-compose.yml "https://raw.githubusercontent.com/repulsivityy/VirusTotal/refs/heads/main/OpenCTI%20Integration/docker-compose.yml"
  sudo docker compose up -d  
elif [ "$choice" == "Del" ]; then
  cd ~/opencti
  echo "Bringing Docker Image Down"
  sudo docker compose down -v
  echo "Pruning all unused docker image + volumes"
  sudo docker system prune -a --volumes -f
  echo "Downloading latest YML file"
  wget -O docker-compose.yml "https://raw.githubusercontent.com/repulsivityy/VirusTotal/refs/heads/main/OpenCTI%20Integration/docker-compose.yml"
  sudo docker compose up -d 
else
  echo "You selected 'N'. Exiting the application"
fi