#!/bin/bash

# Platform Hook: .platform/hooks/prestart/01_configure_nginx_for_follower.sh
# Purpose: Modifies the Nginx configuration on follower instances before Nginx starts.
# This script runs in /var/app/current.

set -e # Exit immediately if a command exits with a non-zero status.

NGINX_CONFIG_PATH="/var/app/current/.platform/nginx/nginx.conf"
MASTER_IP_FILE="/var/app/current/.masterIP"
MASTER_FLAG_FILE="/var/app/current/.master"

LOG_PREFIX="[configure_nginx_for_follower_hook]"

echo "$LOG_PREFIX Starting..."

# Check if this is a follower instance
if [ ! -f "$MASTER_FLAG_FILE" ]; then
    echo "$LOG_PREFIX This is a FOLLOWER instance (no $MASTER_FLAG_FILE found)."

    if [ ! -f "$MASTER_IP_FILE" ]; then
        echo "$LOG_PREFIX ERROR: $MASTER_IP_FILE not found. Cannot determine Master IP for follower. Exiting."
        exit 1
    fi

    MASTER_IP=$(cat "$MASTER_IP_FILE")
    echo "$LOG_PREFIX Read Master IP: '$MASTER_IP' from $MASTER_IP_FILE"

    if [ -z "$MASTER_IP" ] || [ "$MASTER_IP" == "127.0.0.1" ]; then
        echo "$LOG_PREFIX ERROR: Master IP in $MASTER_IP_FILE is empty or '127.0.0.1'. This is unexpected for a follower. Exiting."
        # If 127.0.0.1 is a valid master IP for some single-instance test, adjust this logic.
        exit 1
    fi

    if [ ! -f "$NGINX_CONFIG_PATH" ]; then
        echo "$LOG_PREFIX ERROR: Nginx source config $NGINX_CONFIG_PATH not found for follower modification! Exiting."
        exit 1
    fi

    echo "$LOG_PREFIX Follower: Master IP is '$MASTER_IP'. Modifying $NGINX_CONFIG_PATH to point to master."
    
    # Create a backup before modifying
    cp "$NGINX_CONFIG_PATH" "${NGINX_CONFIG_PATH}.bak"
    
    # Use sed to replace 127.0.0.1 with the actual Master IP.
    # Ensure the sed command is robust. Using a different delimiter for sed if IPs contain slashes (not typical for IPs).
    sed -i "s|http://127.0.0.1:|http://${MASTER_IP}:|g" "$NGINX_CONFIG_PATH"

    if [ $? -eq 0 ]; then
        echo "$LOG_PREFIX Nginx config $NGINX_CONFIG_PATH modified successfully for follower."
        echo "$LOG_PREFIX Verifying modification (diff against backup):"
        diff "${NGINX_CONFIG_PATH}.bak" "$NGINX_CONFIG_PATH" || true # Show diff, continue even if no changes (should be changes)
        echo "$LOG_PREFIX Content of $NGINX_CONFIG_PATH after modification:"
        cat "$NGINX_CONFIG_PATH"
    else
        echo "$LOG_PREFIX ERROR: Failed to modify $NGINX_CONFIG_PATH for follower using sed. Restoring from backup."
        mv "${NGINX_CONFIG_PATH}.bak" "$NGINX_CONFIG_PATH" # Restore backup
        exit 1
    fi
else
    echo "$LOG_PREFIX This is a MASTER instance ($MASTER_FLAG_FILE found). No Nginx modification needed by this hook."
fi

echo "$LOG_PREFIX Finished successfully."
exit 0 