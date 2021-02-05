# HelDataPipe

The purpose of the system is to be able to receive any kind of IoT data of City of Helsinki in a performant, reliable and secure manner and serve it as an API for further usage.

## Environments

Review (PR branch): Delpoyed temporarily at <temporary name>.test.kuva.hel.ninja. See the nams from review's deploy step. Valid until the PR gets closed.

Staging (develop branch): https://api.heldatapipe.test.kuva.hel.ninja/, https://endpoint.heldatapipe.test.kuva.hel.ninja/.

Production (master branch): https://api.heldatapipe.prod.kuva.hel.ninja/, https://endpoint.heldatapipe.prod.kuva.hel.ninja/.

## Components

- [Endpoint](https://github.com/City-of-Helsinki/hel-data-pipe/tree/develop/endpoint) - Flask API that receives data from IoT sensors and gateways, authenticates the requests and puts the data to the buffer for further processing as Kafka producer.
- [Parser](https://github.com/City-of-Helsinki/hel-data-pipe/tree/develop/parser) - Kafka consumer that receives data (serialised HTTP requests) from a Kafka topic, parses the payload and then as Kafka producer puts the parsed data to another Kafka topic for further processing.
- [Persister](https://github.com/City-of-Helsinki/hel-data-pipe/tree/develop/persister) - Kafka consumer that receives parsed data and stores it to database, Django admin interface for defining data sources and channels, Django API for providing access to stored data.

## Development with docker

Prerequisites:
- Docker engine: 19.03.0+
- Docker compose 1.25.5+

1. Copy and modify local environment variables:
```
cp .env.dev-sample .env
```

1.  When running Kafka, Zookeeper and databases in Docker, copy `docker-compose.env.yaml.example` to `docker-compose.override.yml` and modify if needed.
```
cp docker-compose.dev.yml-sample docker-compose.override.yml
```

1. Run (with docker-compose.yml and docker-compose.override.yml):
```
docker-compose up
```

1. Alternatively, run with external Kafka, Zookeeper and databases by skipping overrides:
```
docker-compose -f docker-compose.yml up
```

- The project is now running:
  - IoT data input API at http://localhost:5000
  - Persister admin at http://localhost:8080/admin/
  - Datasources API at http://localhost:8080/datasources/


## Code formatting and linting

- `setup.cfg` in each project directory
- black, isort, autoflake and flake8
- for static code analysis details, see `ci.yml`

NOTE! Because of monorepo project structure `pre-commit` doesn't work that well. Instead we have utility script (`format.sh`) that runs all the necesssary stuff for each project. You can choose to install the script as a pre-commit hook or run it manually before commits.

## Issues board

https://helsinkisolutionoffice.atlassian.net/projects/HDP/issues
