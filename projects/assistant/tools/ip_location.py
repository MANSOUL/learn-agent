import requests

def where_am_i():
    """获取当前所在位置，包含纬度、经度、城市
    
    """
    try:
        d = requests.get("http://ip-api.com/json/?lang=zh-CN", timeout=8).json()
        if d["status"] == "success":
            location = f"纬度：{d["lat"]}，经度：{d["lon"]}，省份：{d['regionName']}，城市：{d['city']}"
            print(location)
            return location
    except Exception as e:
        return f"无法获取当前所在位置"
    return f"无法获取当前所在位置"

where_am_i()