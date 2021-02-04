#!/bin/bash

set -e

if [ -z "$SKIP_KAFKA_CHECK" -o "$SKIP_KAFKA_CHECK" = "0" ]; then
    until nc -vz -w30 "$KAFKA_HOST" $KAFKA_PORT
    do
      echo "Waiting for kafka connection at ${KAFKA_HOST}:${KAFKA_PORT} ..."
      sleep 1
    done
    echo "Kafka is up!"
fi

# Start server
if [[ ! -z "$@" ]]; then
    "$@"
elif [[ "$DEV_SERVER" = "1" ]]; then
    FLASK_DEBUG="$DEBUG" flask run --host=0.0.0.0
else
    uwsgi --ini .prod/uwsgi.ini
fi
