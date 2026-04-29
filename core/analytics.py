import requests

def get_visitor_info():
    try:
        res = requests.get("http://ip-api.com/json/", timeout=5)
        data = res.json()

        return {
            "ip": data.get("query"),
            "country": data.get("country"),
            "city": data.get("city"),
            "isp": data.get("isp")
        }
    except:
        return {
            "ip": "unknown",
            "country": "unknown",
            "city": "unknown",
            "isp": "unknown"
        }