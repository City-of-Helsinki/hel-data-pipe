# HelDataPipe

The purpose of the system is to be able to receive any kind of IoT data of City of Helsinki in a performant, reliable and secure manner and serve it as an API for further usage.

## Components

- [Endpoint](https://github.com/City-of-Helsinki/hel-data-pipe/tree/develop/endpoint)

## Development with docker
Prerequisites:
- Docker engine: 19.03.0+
- Docker compose 1.25.5+

Run `docker-compose up`
- The project is now running:
  - Endpoint at `http://localhost:5000`


### Code formatting and linting

- `setup.cfg` in each project directory
- black, isort, autoflake and flake8
- for static code analysis details, see `ci.yml`

NOTE! Because of monorepo project structure `pre-commit` doesn't work that well. Instead we have utility script (`format.sh`) that runs all the necesssary stuff for each project. You can choose to install the script as a pre-commit hook or run it manually before commits.
