import pytest
import requests
from weather.services import get_weather

from unittest.mock import patch

@pytest.mark.django_db
class TestGetWeather:
    @patch("weather.services.requests.get")
    def test_successful_weather_response(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "main": {"temp": 25.0},
            "weather": [{"description": "clear sky"}]
        }

        result = get_weather("Paris")

        assert result["temp"] == 25.0
        assert result["description"] == "clear sky"

    @patch("weather.services.requests.get")
    def test_city_not_found_error(self, mock_get):
        mock_get.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error")
        with pytest.raises(requests.exceptions.HTTPError):
            get_weather("FakeCity")

    def test_empty_city_raises_value_error(self):
        with pytest.raises(ValueError, match="City is required"):
            get_weather("")

    @patch("weather.services.requests.get")
    def test_missing_temp_field(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "main": {},
            "weather": [{"description": "sunny"}]
        }

        with pytest.raises(KeyError):
            get_weather("Berlin")

    @patch("weather.services.requests.get")
    def test_missing_weather_description(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "main": {"temp": 21.0},
            "weather": [{}]
        }

        with pytest.raises(KeyError):
            get_weather("Berlin")
