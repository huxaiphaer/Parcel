# 📦 Track & Trace API – parcelLab Backend Challenge

This project is a Django-based backend API for tracking parcel shipments and retrieving current weather information for delivery addresses.

## Features

- REST API to look up shipment info by tracking number and carrier
- Article info per shipment
- Weather data via OpenWeatherMap (with 2-hour caching)
- Modular structure (Shipments, Weather)
- Dockerized setup
- OpenAPI 
- Test coverage

## Setup (Local) (Mac / Linux)

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
## Setup (Docker)

```bash
docker compose up 
```


## Code Formatting & Linting.
To ensure consistent code style and quality, use the following commands (requires invoke , black , isort , and flake8 ):

```
# Format and lint the codebase
inv format

# Run only Black
inv black

# Run only isort
inv isort

# Run only flake8
inv flake8
```

# Access endpoints.
[Swagger Endpoints](http://0.0.0.0:9000/api/schema/swagger-ui/)

## Environment Variables

Create a .env file and the following envs inside the .env.example file for reference.



### Running tests with docker.
```
docker compose run --rm web pytest
```
