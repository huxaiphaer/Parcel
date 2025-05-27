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