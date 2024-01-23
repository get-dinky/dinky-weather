# dinky-weather

Weather widget for the [dinky](https://github.com/get-dinky/dinky) dashboard generator

## Installation

Install this plugin using `pip`:

```bash
pip install dinky-weather
```

## Usage

`dinky-weather` is a plugin for the `dinky` dashboard generator. You can simply register the weather widget with your DashboardManager:

```python
from dinky_weather import DinkyWeatherPlugin

dm.register(
    DinkyWeatherPlugin(
        api_key="accuweather API key",
        location="location name",
        location_id="accuweather location id"
    ), zone="A")
```

Then draw your dashboard as usual:

```python
dm.draw_dashboard()
```

## Development

To contribute to this library, first checkout the code. Then create a new virtual environment:

```bash
cd dinky-weather
python -m venv .venv
source .venv/bin/activate
```

Now install the dependencies and test dependencies:

```bash
pip install -e '.[test]'
```

To run the tests:

```bash
python -m pytest
```

## Acknowledgements

- Icons by [Icons8](https://icons8.com/)