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

## Setup (Local)

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
## Setup (Docker)

```bash
docker-compose up --build
```

API Example

```bash
GET /api/shipments/TN12345678/DHL/
```

## Environment Variables

Create a .env file and the following envs


- SECRET_KEY
- OPENWEATHERMAP_API_KEY
- SECRET_KEY
- DEBUG=true
- POSTGRES_DB=parcels
- POSTGRES_USER
- POSTGRES_PASSWORD

### Running tests with docker.
```
docker compose exec web pytest 
```

## License.
MIT
