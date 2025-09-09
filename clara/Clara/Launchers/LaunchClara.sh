#!/bin/bash
# Linux Launcher for Clara

# Get the absolute path of the script's directory
SCRIPT_DIR="$(dirname "$(realpath "$0")")"

# Navigate to the Core directory, which is one level up and then into Core
cd "${SCRIPT_DIR}/../Core"

# Check if python3 is available
if ! command -v python3 &> /dev/null
then
    echo "Python 3 could not be found. Please install Python 3."
    exit
fi

# Launch the main application
python3 cortex.py
