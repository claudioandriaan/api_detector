from playwright.sync_api import sync_playwright

def capture_api_calls(url):
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        def handle_response(response):
            try:
                content_type = response.headers.get("content-type", "")

                if "application/json" in content_type:
                    req = response.request

                    results.append({
                        "url": response.url,
                        "method": req.method,
                        "headers": dict(req.headers),
                        "post_data": req.post_data
                    })
            except:
                pass

        page.on("response", handle_response)

        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)

        browser.close()

    return results