#!/bin/sh
set -e

# If --help or -h is used, show Python + Go help
if echo "$@" | grep -qE -- "--help|-h"; then
  echo "### Python Entrypoint Help ###"
  /app/entrypoint.py --help || true
  echo "\n### HMS Program Help ###"
  --help || true
  exit 0
fi

CONFIG_FLAG=0
CONFIG_JSON=""
CMD=""
ARGS=""

# Parse args: --config '<json>' myapp trinity_log
for arg in "$@"; do
  if [ "$CONFIG_FLAG" = 1 ]; then
    CONFIG_JSON="$arg"
    CONFIG_FLAG=0
  elif [ "$arg" = "--config" ]; then
    CONFIG_FLAG=1
  elif [ -z "$CMD" ]; then
    CMD="$arg"
  else
    ARGS="$ARGS $arg"
  fi
done

# Run Python entrypoint to handle downloads and write runtime env vars
/app/entrypoint.py --config "$CONFIG_JSON" download

# Load generated env vars from the entrypoint (saved by Python)
if [ -f /tmp/.env.runtime ]; then
  echo "Sourcing runtime env vars from /tmp/.env.runtime"
  . /tmp/.env.runtime
fi

echo "Running: $CMD $ARGS"
exec $CMD $ARGS
