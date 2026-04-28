import requests

def test_endpoint(entry):
    try:
        if entry["method"] == "GET":
            res = requests.get(entry["url"], timeout=10)

            if res.status_code == 200 and "application/json" in res.headers.get("content-type", ""):
                return True

    except:
        pass

    return False