from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time


def capture_api_calls(url, timeout=30000, wait_time=5, max_retries=2):
    results = []
    seen = set()

    for attempt in range(max_retries):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-blink-features=AutomationControlled",
                        "--disable-gpu"
                    ]
                )

                context = browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                    viewport={"width": 1280, "height": 800},
                    ignore_https_errors=True
                )

                page = context.new_page()

                # 🚫 Block useless resources (performance boost)
                page.route(
                    "**/*",
                    lambda route: route.abort()
                    if route.request.resource_type in ["image", "font", "media"]
                    else route.continue_()
                )

                # 📡 Capture API responses
                def handle_response(response):
                    try:
                        content_type = response.headers.get("content-type", "")

                        if "application/json" not in content_type:
                            return

                        req = response.request
                        key = f"{req.method}:{response.url}"

                        if key in seen:
                            return

                        seen.add(key)

                        results.append({
                            "url": response.url,
                            "method": req.method,
                            "status": response.status,
                            "headers": dict(req.headers),
                            "post_data": req.post_data
                        })

                    except Exception:
                        pass

                page.on("response", handle_response)

                # 🌍 Navigate properly
                page.goto(url, timeout=timeout, wait_until="domcontentloaded")

                # ⏳ Smart waiting (better than fixed sleep)
                page.wait_for_load_state("networkidle", timeout=timeout)

                # Optional extra wait (for lazy APIs)
                time.sleep(wait_time)

                browser.close()
                return results

        except PlaywrightTimeoutError:
            print(f"[Retry {attempt+1}] Timeout, retrying...")
        except Exception as e:
            print(f"[Retry {attempt+1}] Error:", e)

    return results