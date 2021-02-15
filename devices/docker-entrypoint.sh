#!/bin/bash

set -e

#until nc -z -v -w30 "$DATABASE_HOST" $DATABASE_PORT
#do
#    echo "Waiting for postgres database connection at ${DATABASE_HOST}:${DATABASE_PORT} ..."
#    sleep 1
#done
#echo "Database is up!"

if [ -z "$SKIP_KAFKA_CHECK" -o "$SKIP_KAFKA_CHECK" = "0" ]; then
    until nc -vz -w30 "$KAFKA_HOST" $KAFKA_PORT
    do
      echo "Waiting for kafka connection at ${KAFKA_HOST}:${KAFKA_PORT} ..."
      sleep 1
    done
    echo "Kafka is up!"
fi

if [[ "$APPLY_MIGRATIONS" = "1" ]]; then
    echo "Applying database migrations..."
    ./manage.py migrate --noinput
fi


if [[ "$INITIALIZE_DATA" = "1" ]]; then
    echo "TODO: Initializing data..."
    #./manage.py initialize_data
fi

# Start server
if [ ! -z "$@" ]; then
    "$@"
elif [ "$PARSER" = "1" ]; then
    python ./manage.py parse_data
elif [ "$DEV_SERVER" = "1" ]; then
    python ./manage.py runserver 0.0.0.0:8080
else
    uwsgi --ini .prod/uwsgi.ini
fi
