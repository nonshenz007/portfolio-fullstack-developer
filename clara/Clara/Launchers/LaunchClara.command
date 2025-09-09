#!/bin/zsh
# macOS Launcher for Clara

# Get the absolute path of the script's directory
SCRIPT_DIR="${0:A:h}"

# Navigate to the Core directory, which is one level up and then into Core
cd "${SCRIPT_DIR}/../Core"

# Check if python is available
if ! command -v python &> /dev/null
then
    echo "Python could not be found. Please install Python."
    exit
fi

# Launch the main application
python cortex.py
