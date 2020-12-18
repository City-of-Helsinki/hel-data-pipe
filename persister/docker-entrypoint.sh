#!/bin/bash

set -e

until nc -z -v -w30 "$DATABASE_HOST" 5432
do
    echo "Waiting for postgres database connection..."
    sleep 1
done
echo "Database is up!"

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
elif [[ "$DEV_SERVER" = "1" ]]; then
    python ./manage.py runserver 0.0.0.0:8080
else
    uwsgi --ini .prod/uwsgi.ini
fi
