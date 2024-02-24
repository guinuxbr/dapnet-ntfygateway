#!/usr/bin/env bash

# Define colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RESET='\033[0m'

# This script will execute all necessary steps to install the dapnet-ntfygateway on a Debian based OS like Ubuntu or Raspberry Pi OS.

# Ensure we are running as pi-star user
if [[ $(whoami) != "pi-star" ]]; then
    echo "${RED}This script must be run as user 'pi-star'${RESET}"
    exit 1
fi

# Update the system and install OS dependencies
echo "${GREEN}Updating the system and installing OS dependencies...${RESET}"
sudo apt update && sudo apt upgrade -y >/dev/null 2>&1 
sudo apt install -y git python3 python3-venv >/dev/null 2>&1

# Create the needed directories
echo "${GREEN}Creating the needed directories...${RESET}"
mkdir -p ~/git
mkdir -p ~/logs/dapnet-ntfygateway
mkdir -p ~/.config/systemd/user/

# Clone the repository
echo "${GREEN}Cloning the repository...${RESET}"
cd ~/git || echo "${RED}Directory ~/git does not exist!${RESET}" && exit 1
git clone https://github.com/guinuxbr/dapnet-ntfygateway.git >/dev/null 2>&1

# Create and activate the virtual environment
echo "${GREEN}Creating and activating the virtual environment...${RESET}"
cd ~/git/dapnet-ntfygateway || echo "${RED}Directory ~/git/dapnet-ntfygateway does not exist!${RESET}" && exit 1
python3 -m venv venv >/dev/null 2>&1
source venv/bin/activate >/dev/null 2>&1

# Install Python dependencies
echo "${GREEN}Installing Python dependencies...${RESET}"
pip install -r requirements.txt >/dev/null 2>&1

# Prepare the config file
echo "${GREEN}Preparing the config file...${RESET}"
cp config.json.example config.json

# Create the systemd service
echo "${GREEN}Creating the systemd service...${RESET}"
cp dapnet-ntfygateway.service ~/.config/systemd/user/dapnet-ntfygateway.service
systemctl --user daemon-reload

# Start and enable the service
echo "${GREEN}Starting and enabling the service...${RESET}"
systemctl --user start dapnet-ntfygateway.service
systemctl --user enable dapnet-ntfygateway.service