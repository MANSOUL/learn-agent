# pip install requests
import requests
from langchain_core.tools import tool

_WEATHER_CODE_2_TEXT = {
    0: "晴",
    1: "大部晴朗",
    2: "多云",
    3: "阴",
    45: "雾",
    48: "雾凇",
    51: "小毛毛雨",
    53: "毛毛雨",
    61: "小雨",
    63: "中雨",
    65: "大雨",
    71: "小雪",
    73: "中雪",
    75: "大雪",
    80: "阵雨",
    81: "强阵雨",
    95: "雷暴",
    96: "雷暴伴小冰雹",
    99: "强雷暴冰雹",
}

@tool
def get_weather(latitude: float, longitude: float) -> str:
    """通过经纬度查询指定城市的天气信息。

        Args:
            latitude: 纬度，如 39.9042
            longitude: 经度，如 116.4074

        Returns:
            返回天气、气温(°C)、体感温度(°C)、相对湿度(%)、风速(km/h)、风向(度)、降水(mm)
    """
    # print(f"调用天气API，纬度{latitude}，经度{longitude}")
    # 发起 http 请求
    try:
        resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m,wind_direction_10m,precipitation",
                "timezone": "Asia/Shanghai",
            },
            timeout=10,
        )
        resp.raise_for_status()  # 非 2xx 抛 HTTPError
        data = resp.json()
        current = data.get("current")
        detail = (
            f"{_WEATHER_CODE_2_TEXT.get(current["weather_code"])}；"
            f"气温：{current["temperature_2m"]}；体感温度：{current["apparent_temperature"]}；"
            f"相对湿度：{current["relative_humidity_2m"]}；风速：{current["wind_speed_10m"]}；"
            f"风向：{current["wind_direction_10m"]}；降水：{current["precipitation"]}"
        )
        return detail
    except requests.exceptions.Timeout:
        return "请求超时"
    except requests.exceptions.ConnectionError:
        return "网络不通"
    except requests.exceptions.HTTPError as e:
        return f"HTTP 错误: {e.response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"其他请求错误: {e}"

SCHEMA = {
    "type": "function",
    "name": "get_weather",
    "description": "通过经纬度查询指定城市的天气信息。",
    "parameters": {
        "type": "object",
        "properties": {
            "latitude": {
                "type": "string",
                "description": "纬度，如 39.9042",
            },
            "latitude": {
                "type": "string",
                "description": "经度，如 116.4074",
            },
        },
        "required": ["latitude", "latitude"],
        "additionalProperties": False,
    },
    "strict": True,
}