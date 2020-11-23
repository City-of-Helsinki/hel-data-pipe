#!/bin/bash

set -e

if [ -z "$SKIP_KAFKA_CHECK" -o "$SKIP_KAFKA_CHECK" = "0" ]; then
    until nc -vz -w30 "$KAFKA_HOST" $KAFKA_PORT
    do
      echo "Waiting for kafka connection..."
      sleep 1
    done
    echo "Kafka is up!"
fi

# Start server
if [[ ! -z "$@" ]]; then
    "$@"
else
    python3 app.py
fi
