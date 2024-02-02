import pluggy
import os
import requests
import datetime
import json
import textwrap
from io import BytesIO
import base64
from PIL import Image, ImageFont, ImageDraw
import pkg_resources
from io import BytesIO
from dinky.display_configuration import DisplayConfiguration

from dinky.layouts.layout_configuration import Zone
from dinky_weather.assets import icons

hookimpl = pluggy.HookimplMarker("dinky")

class DinkyWeatherPlugin:
    primary_color = "#e9c46a"

    def __init__(self, api_key: str, location: str, location_id: int):
        self.api_key = api_key
        self.location = location
        self.location_id = location_id

    def _get_current_weather(self):
        response = requests.get(f"http://dataservice.accuweather.com/forecasts/v1/daily/5day/{self.location_id}?apikey={self.api_key}&details=true&metric=true")
        return response.json()
    
    def _get_icon(self, name: str):
        return Image.open(BytesIO(base64.b64decode(icons[name])))

    @hookimpl
    def dinky_draw(self, zone: Zone, fullscreen: DisplayConfiguration):
        # Weather forecast
        weather = self._get_current_weather()

        # Fonts
        font_data = pkg_resources.resource_stream('dinky_weather', 'fonts/Roboto-Regular.ttf')
        font_bytes = BytesIO(font_data.read())
        font_header = ImageFont.truetype(font_bytes, 36)
        font_bytes.seek(0)
        font_temp = ImageFont.truetype(font_bytes, 28)
        font_bytes.seek(0)
        font_temp_full = ImageFont.truetype(font_bytes, 22)
        font_bytes.seek(0)
        font_info = ImageFont.truetype(font_bytes, 18)
        font_data = pkg_resources.resource_stream('dinky_weather', 'fonts/Roboto-Bold.ttf')
        font_bytes = BytesIO(font_data.read())
        font_description = ImageFont.truetype(font_bytes, 18)

        # Panel
        im_panel = Image.new('RGB', (zone.width, zone.height), (255, 255, 255))
        draw = ImageDraw.Draw(im_panel)

        draw.rectangle((zone.padding, zone.padding, zone.width-zone.padding, zone.padding + 55), fill=self.primary_color)
        draw.text((zone.padding + 5, zone.padding + 5), self.location, font=font_header, fill="white")

        # Weather icon
        img = self._get_icon(weather['DailyForecasts'][0]['Day']['Icon'])
        img.thumbnail((50, 50))
        im_panel.paste(img, (zone.padding + 5, zone.padding + 65))

        # Temperature
        draw.text((zone.padding + 75, zone.padding + 70), f"{round(weather['DailyForecasts'][0]['Temperature']['Minimum']['Value'])}-{round(weather['DailyForecasts'][0]['Temperature']['Maximum']['Value'])} °C", font=font_temp, fill="black")
        
        # Description
        draw.multiline_text((zone.padding + 5, zone.padding + 125), textwrap.fill(weather['DailyForecasts'][0]['Day']['LongPhrase'], width=30), font=font_description, fill="black")
        
        # Details
        segment_width = int(zone.width / 3)

        # Chance of rain
        img = self._get_icon(50)
        img.thumbnail((20, 20))
        im_panel.paste(img, (0 * segment_width + zone.padding + int(0.37 * segment_width), zone.padding + 185))
        draw.text((0 * segment_width + zone.padding + int(0.33 * segment_width), zone.padding + 205), f"{weather['DailyForecasts'][0]['Day']['RainProbability']} %", font=font_info, fill="black")
        
        # Wind speed
        img = self._get_icon(51)
        img.thumbnail((20, 20))
        im_panel.paste(img, (1 * segment_width + zone.padding + int(0.37 * segment_width), zone.padding + 185))
        draw.text((1 * segment_width + zone.padding + int(0.09 * segment_width), zone.padding + 205), f"{weather['DailyForecasts'][0]['Day']['Wind']['Speed']['Value']} {weather['DailyForecasts'][0]['Day']['Wind']['Speed']['Unit']}", font=font_info, fill="black")

        # UV index
        img = self._get_icon(52)
        img.thumbnail((20, 20))
        im_panel.paste(img, (2 * segment_width + zone.padding + int(0.37 * segment_width), zone.padding + 185))
        draw.text((2 * segment_width + zone.padding + int(0.25 * segment_width), zone.padding + 205), f"{next(item for item in weather['DailyForecasts'][0]['AirAndPollen'] if item['Name'] == 'UVIndex')['Value']} UV", font=font_info, fill="black")

        # Fullscreen
        im_fullscreen = Image.new('RGB', (fullscreen.width, fullscreen.height), (255, 255, 255))
        draw = ImageDraw.Draw(im_fullscreen)

        draw.rectangle((zone.padding, zone.padding, fullscreen.width-zone.padding, zone.padding + 55), fill=self.primary_color)
        draw.text((zone.padding + 5, zone.padding + 5), self.location, font=font_header, fill="white")

        for i in range(5):
            # Day
            date = datetime.datetime.fromisoformat(weather['DailyForecasts'][i]['Date'])
            draw.text((zone.padding + 5 + i * 158, zone.padding + 65), date.strftime("%a"), font=font_temp_full, fill="black")

            # Weather icon
            img = self._get_icon(weather['DailyForecasts'][i]['Day']['Icon'])
            img.thumbnail((50, 50))
            im_fullscreen.paste(img, (zone.padding + 5 + 55 + i * 158, zone.padding + 65))

            # Temperature
            draw.text((zone.padding + 5 + i * 158, zone.padding + 120), f"{round(weather['DailyForecasts'][i]['Temperature']['Minimum']['Value'])}-{round(weather['DailyForecasts'][i]['Temperature']['Maximum']['Value'])} °C", font=font_temp, fill="black")
            
            # Description
            draw.multiline_text((zone.padding + 5 + i * 158, zone.padding + 165), textwrap.fill(weather['DailyForecasts'][i]['Day']['LongPhrase'], width=16), font=font_description, fill="black")

            # Chance of rain
            img = self._get_icon(50)
            img.thumbnail((20, 20))
            im_fullscreen.paste(img, (zone.padding + 5 + i * 158, zone.padding + 340))
            draw.text((zone.padding + 5 + 25 + i * 158, zone.padding + 340), f"{weather['DailyForecasts'][i]['Day']['RainProbability']} %", font=font_info, fill="black")

            # Wind speed
            img = self._get_icon(51)
            img.thumbnail((20, 20))
            im_fullscreen.paste(img, (zone.padding + 5 + i * 158, zone.padding + 390))
            draw.text((zone.padding + 5 + 25 + i * 158, zone.padding + 390), f"{weather['DailyForecasts'][i]['Day']['Wind']['Speed']['Value']} {weather['DailyForecasts'][i]['Day']['Wind']['Speed']['Unit']}", font=font_info, fill="black")

            # UV index
            img = self._get_icon(52)
            img.thumbnail((20, 20))
            im_fullscreen.paste(img, (zone.padding + 5 + i * 158, zone.padding + 440))
            draw.text((zone.padding + 5 + 25 + i * 158, zone.padding + 440), f"{next(item for item in weather['DailyForecasts'][i]['AirAndPollen'] if item['Name'] == 'UVIndex')['Value']} UV", font=font_info, fill="black")

        return im_panel, im_fullscreen