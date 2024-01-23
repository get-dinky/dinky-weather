import os
from PIL import Image

from dinky_weather import DinkyWeatherPlugin

def test_dinky_weather_plugin_init():
    plugin = DinkyWeatherPlugin('api_key', 'location', 'location_id')
    assert plugin.api_key == 'api_key'
    assert plugin.location == 'location'
    assert plugin.location_id == 'location_id'
