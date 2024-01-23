import pluggy
import os
import requests
import textwrap
from PIL import Image, ImageFont, ImageDraw

from dinky.layouts.layout_configuration import Zone

hookimpl = pluggy.HookimplMarker("dinky")

class DinkyWeatherPlugin:
    primary_color = "#e9c46a"

    def __init__(self, api_key: str, location: str, location_id: int):
        self.api_key = api_key
        self.location = location
        self.location_id = location_id

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

    ICONS = {
        1: os.path.join(ASSETS_DIR, "sun.png"),
        2: os.path.join(ASSETS_DIR, "sun.png"),
        3: os.path.join(ASSETS_DIR, "partly-cloudy-day.png"),
        4: os.path.join(ASSETS_DIR, "partly-cloudy-day.png"),
        5: os.path.join(ASSETS_DIR, "haze.png"),
        6: os.path.join(ASSETS_DIR, "cloud.png"),
        7: os.path.join(ASSETS_DIR, "clouds.png"),
        8: os.path.join(ASSETS_DIR, "clouds.png"),
        11: os.path.join(ASSETS_DIR, "fog.png"),
        12: os.path.join(ASSETS_DIR, "rain-cloud.png"),
        13: os.path.join(ASSETS_DIR, "rain-cloud-sun.png"),
        14: os.path.join(ASSETS_DIR, "rain-cloud-sun.png"),
        15: os.path.join(ASSETS_DIR, "cloud-lightning.png"),
        16: os.path.join(ASSETS_DIR, "storm.png"),
        17: os.path.join(ASSETS_DIR, "stormy-weather.png"),
        18: os.path.join(ASSETS_DIR, "heavy-rain.png"),
        19: os.path.join(ASSETS_DIR, "moderate-rain.png"),
        20: os.path.join(ASSETS_DIR, "rain.png"),
        21: os.path.join(ASSETS_DIR, "light-rain.png"),
        22: os.path.join(ASSETS_DIR, "snow.png"),
        23: os.path.join(ASSETS_DIR, "light-snow.png"),
        24: os.path.join(ASSETS_DIR, "snow-storm.png"),
        25: os.path.join(ASSETS_DIR, "sleet.png"),
        26: os.path.join(ASSETS_DIR, "sleet.png"),
        29: os.path.join(ASSETS_DIR, "sleet.png"),
        30: os.path.join(ASSETS_DIR, "hot.png"),
        31: os.path.join(ASSETS_DIR, "cold.png"),
        32: os.path.join(ASSETS_DIR, "wind.png")
    }

    def _get_current_weather(self):
        response = requests.get(f"http://dataservice.accuweather.com/forecasts/v1/daily/1day/{self.location_id}?apikey={self.api_key}&details=true&metric=true")
        return response.json()

    @hookimpl
    def dinky_draw_zone(self, zone: Zone):
        im = Image.new('RGBA', (zone.width, zone.height), (255, 255, 255))
        draw = ImageDraw.Draw(im)
        fnt_header = ImageFont.truetype("arial.ttf", 36)
        fnt_temp = ImageFont.truetype("arial.ttf", 28)
        fnt_description = ImageFont.truetype("arialbd.ttf", 18)
        fnt_info = ImageFont.truetype("arial.ttf", 18)

        draw.rectangle((zone.padding, zone.padding, zone.width-zone.padding, zone.padding + 55), fill=self.primary_color)
        draw.text((zone.padding + 5, zone.padding + 5), self.location, font=fnt_header, fill="white")

        weather = self._get_current_weather()

        # Weather icon
        img = Image.open(self.ICONS[weather['DailyForecasts'][0]['Day']['Icon']], 'r')
        img.thumbnail((50, 50))
        im.paste(img, (zone.padding + 5, zone.padding + 65))

        # Temperature
        draw.text((zone.padding + 75, zone.padding + 70), f"{round(weather['DailyForecasts'][0]['Temperature']['Minimum']['Value'])}-{round(weather['DailyForecasts'][0]['Temperature']['Maximum']['Value'])} °C", font=fnt_temp, fill="black")
        
        # Description
        draw.multiline_text((zone.padding + 5, zone.padding + 125), textwrap.fill(weather['DailyForecasts'][0]['Day']['LongPhrase'], width=30), font=fnt_description, fill="black")
        
        # Details
        segment_width = int(zone.width / 3)

        # Chance of rain
        img = Image.open(os.path.join(self.ASSETS_DIR, "rainfall.png"), 'r')
        img.thumbnail((20, 20))
        im.paste(img, (0 * segment_width + zone.padding + int(0.37 * segment_width), zone.padding + 185))
        draw.text((0 * segment_width + zone.padding + int(0.33 * segment_width), zone.padding + 205), f"{weather['DailyForecasts'][0]['Day']['RainProbability']} %", font=fnt_info, fill="black")
        
        # Wind speed
        img = Image.open(os.path.join(self.ASSETS_DIR, "windsock.png"), 'r')
        img.thumbnail((20, 20))
        im.paste(img, (1 * segment_width + zone.padding + int(0.37 * segment_width), zone.padding + 185))
        draw.text((1 * segment_width + zone.padding + int(0.09 * segment_width), zone.padding + 205), f"{weather['DailyForecasts'][0]['Day']['Wind']['Speed']['Value']} {weather['DailyForecasts'][0]['Day']['Wind']['Speed']['Unit']}", font=fnt_info, fill="black")

        # UV index
        img = Image.open(os.path.join(self.ASSETS_DIR, "uv.png"), 'r')
        img.thumbnail((20, 20))
        im.paste(img, (2 * segment_width + zone.padding + int(0.37 * segment_width), zone.padding + 185))
        draw.text((2 * segment_width + zone.padding + int(0.25 * segment_width), zone.padding + 205), f"{next(item for item in weather['DailyForecasts'][0]['AirAndPollen'] if item['Name'] == 'UVIndex')['Value']} UV", font=fnt_info, fill="black")

        return im