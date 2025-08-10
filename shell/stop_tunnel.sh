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

# Match SSH process
PATTERN="-fN -L ${LOCAL_PORT}:127.0.0.1:${REMOTE_PORT} ${REMOTE_USER}@${REMOTE_HOST}"
echo "Looking for tunnel with pattern: ssh ${PATTERN}"

PIDS=$(pgrep -f "ssh ${PATTERN}" || true)

echo "Matched PIDs: ${PIDS}"

if [ -z "$PIDS" ]; then
  echo "No matching tunnel process found."
  exit 0
fi

# Kill matching SSH tunnel process
kill $PIDS
echo "Sent kill signal to tunnel process(es): $PIDS"

# Verify termination
sleep 0.2
REMAINING=$(pgrep -f "ssh ${PATTERN}" || true)
if [ -z "$REMAINING" ]; then
  echo "Tunnel closed: localhost:${LOCAL_PORT} → ${REMOTE_HOST}:${REMOTE_PORT}"
  exit 0
else
  echo "Failed to close tunnel (still running PIDs: $REMAINING)" >&2
  exit 1
fi
