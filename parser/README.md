# Parser
## Description
A Python application that receives data (serialised HTTP requests)
from a Kafka topic, parses the payload and then puts
the parsed data to another Kafka topic for further processing.

## Technology
### Main technologies
- kafka-python

### Supporting technologies and tools
- `pytest` for testing
- `black` for formatting
- `flake8` for code style
- `isort` for sorting imports
- `pre-commit` for running checks before commits (see `pre-commit-config.yaml` file for details)

- `pip-compile` for compiling requirements*.txt
- `uwsgi` for production server

## Running test suite with docker-compose

While project running with docker-compose run `$ docker-compose exec endpoint pytest`

## Supported hardware

TODO

## Documentation

Further documentation can be found [here](https://helsinkisolutionoffice.atlassian.net/wiki/spaces/DD/pages/617709741/IoT+sensor+data+collector+persister+and+API)

## Environments

TODO

## CI/CD builds

TODO
