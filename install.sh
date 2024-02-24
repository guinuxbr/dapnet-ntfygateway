#!/usr/bin/env bash

# Define colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RESET='\033[0m'

# This script will execute all necessary steps to install the dapnet-ntfygateway on a Debian based OS like Ubuntu or Raspberry Pi OS.

# Ensure we are running as pi-star user
if [[ $(whoami) != "pi-star" ]]; then
    echo -e "❌ ${RED}This script must be run as user 'pi-star'${RESET}"
    exit 1
else
    echo -e "🚀 ${GREEN}Running as user 'pi-star'${RESET}"
fi

# Update the system and install OS dependencies
echo ""
echo -e "${GREEN}Updating the system and installing OS dependencies...${RESET}"
sudo apt update
sudo apt upgrade -y 
sudo apt install -y git python3 python3-venv

# Create the needed directories
echo ""
echo -e "${GREEN}Creating the needed directories...${RESET}"
mkdir -p /home/pi-star/git
echo -e "✅ ${GREEN}Ensuring /home/pi-star/git/ exists...${RESET}"
mkdir -p /home/pi-star/logs/dapnet-ntfygateway
echo -e "✅ ${GREEN}Ensuring /home/pi-star/logs/dapnet-ntfygateway/ exists...${RESET}"
mkdir -p /home/pi-star/.config/systemd/user/
echo -e "✅ ${GREEN}Ensuring /home/pi-star/.config/systemd/user/ exists...${RESET}"

# Clone the repository
echo ""
echo -e "${GREEN}Cloning the repository...${RESET}"
git clone https://github.com/guinuxbr/dapnet-ntfygateway.git /home/pi-star/git/dapnet-ntfygateway

# Entering the cloned repository directory
cd /home/pi-star/git/dapnet-ntfygateway || echo -e " ❌ ${RED}Failed to enter the cloned repository directory${RESET}" && exit 1

# Create and activate the virtual environment
echo ""
echo -e "${GREEN}Creating and activating the virtual environment...${RESET}"
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo ""
echo -e "${GREEN}Installing Python dependencies...${RESET}"
pip install -r requirements.txt

# Prepare the config file
echo ""
echo -e "${GREEN}Preparing the config file...${RESET}"
cp config.json.example config.json

# Create the systemd service
echo ""
echo -e "${GREEN}Creating the systemd service...${RESET}"
cp dapnet-ntfygateway.service /home/pi-star/.config/systemd/user/dapnet-ntfygateway.service
systemctl --user daemon-reload

# Start and enable the service
echo ""
echo -e "${GREEN}Starting and enabling the service...${RESET}"
systemctl --user start dapnet-ntfygateway.service
systemctl --user enable dapnet-ntfygateway.service