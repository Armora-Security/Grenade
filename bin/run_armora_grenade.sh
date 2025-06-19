#!/bin/sh

# File: bin/run_armora_grenade.sh
# Description: Launcher script for Armora Grenade web application.

APP_ROOT=$(dirname "$(dirname "$(readlink -f "$0")")")
VENV_DIR="$APP_ROOT/venv"
LOG_DIR="$APP_ROOT/logs"
LOG_FILE="$LOG_DIR/armora_grenade.log"
PID_FILE="$APP_ROOT/armora_grenade.pid"

# --- Create logs directory if it doesn't exist ---
mkdir -p "$LOG_DIR"

# --- Check for Python and ensure virtual environment ---
echo "Checking Python environment..."
if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: Python 3 is not installed or not found in PATH."
    echo "Please install Python 3 (e.g., 'pkg install python3' on FreeBSD)."
    exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Creating a new one at $VENV_DIR..."
    python3 -m venv "$VENV_DIR" || { echo "Failed to create virtual environment. Ensure python3-venv is installed."; exit 1; }
fi

echo "Activating virtual environment..."
. "$VENV_DIR/bin/activate" || { echo "Failed to activate virtual environment."; exit 1; }

# --- Install dependencies if not already installed ---
echo "Installing/Updating Python dependencies..."
# It's good practice to have a requirements.txt
# If you don't have one, list them here:
# FLASK_DEPS="Flask libvirt-python"
# pip install $FLASK_DEPS || { echo "Failed to install Python dependencies."; deactivate; exit 1; }
if [ -f "$APP_ROOT/requirements.txt" ]; then
    pip install -r "$APP_ROOT/requirements.txt" || { echo "Failed to install dependencies from requirements.txt."; deactivate; exit 1; }
else
    echo "Warning: requirements.txt not found. Please ensure all dependencies (Flask, libvirt-python) are installed manually."
    echo "Attempting to install common ones: Flask libvirt-python"
    pip install Flask libvirt-python || { echo "Failed to install Flask or libvirt-python. Install them manually or create requirements.txt"; deactivate; exit 1; }
fi


# --- Check if the application is already running ---
if [ -f "$PID_FILE" ]; then
    RUNNING_PID=$(cat "$PID_FILE")
    if ps -p "$RUNNING_PID" > /dev/null; then
        echo "Armora Grenade is already running with PID $RUNNING_PID."
        echo "Access it at http://127.0.0.1:5000"
        echo "To stop, use: kill $RUNNING_PID"
        exit 0
    else
        echo "Stale PID file found. Removing..."
        rm "$PID_FILE"
    fi
fi

# --- Run the Flask application in the background ---
echo "Starting Armora Grenade web server..."
# Using gunicorn for production-ready deployment is recommended.
# For simplicity, we'll use Flask's built-in server here, but redirect output to a log file.
# Note: For production, do NOT use debug=True or the built-in server.
# Consider 'gunicorn -w 4 app.main:app' (after installing gunicorn)

nohup python3 "$APP_ROOT/app/main.py" > "$LOG_FILE" 2>&1 &
PID=$!
echo "$PID" > "$PID_FILE"

echo "Armora Grenade started successfully with PID $PID."
echo "Access the application at http://127.0.0.1:5000"
echo "Log file: $LOG_FILE"
echo "To stop the application, run: kill $PID"
echo "Or simply find the PID (e.g., 'pgrep -f app/main.py') and kill it."

deactivate # Deactivate virtual environment, as nohup detaches the process
