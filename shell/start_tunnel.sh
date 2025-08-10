#!/usr/bin/env bash
set -e

# Get config
SHELL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$CHROMADB_DIR")"
CONFIG_DIR="${PROJECT_ROOT}/config"
CONFIG_FILE="${CONFIG_DIR}/config.yaml"

# Extract YAML values
get_value() {
  local key="$1"
  grep "$key:" "$CONFIG_FILE" | sed -E 's/.*: *//' | tr -d '\r' | xargs
}

REMOTE_USER=$(get_value "REMOTE_USER")
REMOTE_HOST=$(get_value "REMOTE_HOST")
LOCAL_PORT=$(get_value "LOCAL_PORT")
REMOTE_PORT=$(get_value "REMOTE_PORT")

# Open SSH tunnel
ssh -fN -L ${LOCAL_PORT}:127.0.0.1:${REMOTE_PORT} ${REMOTE_USER}@${REMOTE_HOST}

# SSH tunnel feedback
if [ $? -eq 0 ]; then
  echo "Tunnel open: localhost:${LOCAL_PORT} → ${REMOTE_HOST}:${REMOTE_PORT}"
else
  echo "Failed to open tunnel" >&2
  exit 1
fi
