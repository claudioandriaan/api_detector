def is_valid_api(entry):
    url = entry["url"]

    ignore = [".jpg", ".png", ".css", ".js", "analytics", "tracking"]

    if any(x in url for x in ignore):
        return False

    return True


def classify(entry):
    url = entry["url"]
    method = entry["method"]

    if "graphql" in url.lower():
        return "GRAPHQL"

    if method == "POST":
        return "POST_API"

    return "REST_GET"


def detect_pagination(url):
    patterns = ["page=", "offset=", "cursor=", "limit="]
    return any(p in url.lower() for p in patterns)