import pytest
from unittest.mock import patch, MagicMock
from weather.services import get_weather


@pytest.mark.django_db
class TestGetWeather:

    def setup_method(self):
        from django.core.cache import cache
        cache.clear()

    @patch("weather.services.requests.get")
    def test_successful_weather_response(self, mock_get):
        """Test successful weather API response"""
        # Mock geo response
        mock_geo = MagicMock()
        mock_geo.raise_for_status.return_value = None
        mock_geo.json.return_value = [{"lat": 48.8566, "lon": 2.3522}]

        # Mock weather response
        mock_weather = MagicMock()
        mock_weather.raise_for_status.return_value = None
        mock_weather.json.return_value = {
            "main": {"temp": 25.0},
            "weather": [{"description": "clear sky"}],
        }

        mock_get.side_effect = [mock_geo, mock_weather]

        result = get_weather("Paris")
        assert result == {"temp": 25.0, "description": "clear sky"}

    @patch("weather.services.requests.get")
    def test_city_not_found_error(self, mock_get):
        """Empty geo response = no coordinates = fallback response"""
        mock_geo = MagicMock()
        mock_geo.raise_for_status.return_value = None
        mock_geo.json.return_value = []

        mock_get.return_value = mock_geo

        result = get_weather("FakeCity")
        assert result == {"temp": None, "description": "Weather not available"}

    def test_empty_city_input(self):
        """Calling with empty string = fallback response"""
        result = get_weather("")
        assert result == {"temp": None, "description": "Weather not available"}

    @patch("weather.services.requests.get")
    def test_missing_temp_field(self, mock_get):
        """Missing temp should trigger fallback"""
        mock_geo = MagicMock()
        mock_geo.raise_for_status.return_value = None
        mock_geo.json.return_value = [{"lat": 48.8566, "lon": 2.3522}]

        mock_weather = MagicMock()
        mock_weather.raise_for_status.return_value = None
        mock_weather.json.return_value = {
            "main": {},  # No "temp"
            "weather": [{"description": "sunny"}],
        }

        mock_get.side_effect = [mock_geo, mock_weather]

        result = get_weather("Berlin")
        assert result == {"temp": None, "description": "Weather not available"}

    @patch("weather.services.requests.get")
    def test_missing_weather_description(self, mock_get):
        """Missing description = fallback response"""
        mock_geo = MagicMock()
        mock_geo.raise_for_status.return_value = None
        mock_geo.json.return_value = [{"lat": 48.8566, "lon": 2.3522}]

        mock_weather = MagicMock()
        mock_weather.raise_for_status.return_value = None
        mock_weather.json.return_value = {
            "main": {"temp": 21.0},
            "weather": [{}],
        }

        mock_get.side_effect = [mock_geo, mock_weather]

        result = get_weather("Berlin")
        assert result == {"temp": None, "description": "Weather not available"}
