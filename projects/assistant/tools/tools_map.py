from .weather import get_weather
# , SCHEMA as get_weather_schema
from .search import search_web

# TOOLS = [get_weather_schema]
# TOOLS_MAP = {"get_weather": get_weather}

TOOLS = [get_weather, search_web]
