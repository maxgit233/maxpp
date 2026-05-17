import re
import sys
from playwright.sync_api import sync_playwright

def intercept_stream_token():
    # Using a set to avoid printing duplicate tokens if the stream refreshes
    found_tokens = set()

    with sync_playwright() as p:
        print("Launching headless Chromium browser...")
        
        # 1. Added critical arguments for Docker/Cloud compatibility (--no-sandbox)
        # 2. Added blink features flag to reduce bot detection
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox", 
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        
        # Use a custom user agent so the streaming site doesn't flag Playwright as a bot
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Monitor all background network traffic
        def handle_request(request):
            url = request.url
            if "token=" in url:
                token_match = re.search(r'token=[^&?\'"\s]+', url)
                if token_match:
                    token = token_match.group(0)
                    if token not in found_tokens:
                        found_tokens.add(token)
                        # Print clearly to stdout so cloud provider logs capture it instantly
                        print(f"\n[SUCCESS] Caught Token: {token}")
                        sys.stdout.flush() 

        page.on("request", handle_request)
        
        try:
            print("Navigating to target streaming page...")
            # wait_until="domcontentloaded" speeds up the initial script access
            page.goto(
                "https://bingstream.info/live-sport/genoa-vs-ac-milan-1629485561.html", 
                wait_until="domcontentloaded",
                timeout=30000
            )
            
            print("Waiting 10 seconds for HLS streams and video players to initialize...")
            page.wait_for_timeout(10000)  # Increased to 10s to give slow streams time to load
            
        except Exception as e:
            print(f"[ERROR] Page navigation failed: {e}")
        finally:
            print("Closing browser session.")
            browser.close()

if __name__ == "__main__":
    intercept_stream_token()
