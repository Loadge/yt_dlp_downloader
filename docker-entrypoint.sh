#!/bin/bash
set -e

# Print environment info
echo "YouTube Downloader - Docker Container"
echo "======================================"
echo "Config path: $CONFIG_PATH"
echo "Download path: $DOWNLOAD_PATH"
echo "Log path: $LOG_PATH"
echo "JSON output: $JSON_OUTPUT"
echo "======================================"

# Use default config path if not set
if [ -z "$CONFIG_PATH" ]; then
    CONFIG_PATH="/config/videos.yaml"
    echo "Using default config path: $CONFIG_PATH"
fi

# Check if config file exists
if [ ! -f "$CONFIG_PATH" ]; then
    echo "Error: Configuration file not found at $CONFIG_PATH"
    echo "Please mount your config file to /config/videos.yaml"
    exit 1
fi

# Build command with options
CMD="python /app/youtube_downloader.py $CONFIG_PATH"

# Add log file if LOG_PATH is set
if [ -n "$LOG_PATH" ] && [ "$LOG_PATH" != "false" ]; then
    LOG_FILE="$LOG_PATH/download_$(date +%Y%m%d_%H%M%S).log"
    CMD="$CMD --log-file $LOG_FILE"
    echo "Logging to: $LOG_FILE"
fi

# Add JSON output flag if enabled
if [ "$JSON_OUTPUT" = "true" ]; then
    CMD="$CMD --json"
    echo "JSON output mode enabled"
fi

echo "Starting download..."
echo ""

# Execute the command
exec $CMD