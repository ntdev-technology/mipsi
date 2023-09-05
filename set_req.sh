#!/bin/bash

if [ "$EUID" -eq 0 ]; then
    echo "This script is running with root (administrator) permissions. proceeding..."

else
    echo "This script is not running with root (administrator) permissions."
    echo "Please run this script as a superuser or with sudo."


read -p "Do you want to install the needed requirements for MiPSI? (Y/N): " response

if [[ "$response"] =~ ^[Yy]]; then
    echo "installing needed requirements"
    apt-get update && apt-get install python3 && apt-get install pip && pip install bcript

elif [[ "$response"] =~ ^[Nn]]; then
    echo "exiting..."
    stop

else
    echo "Invalid input. Enter Y/N"

fi