# To use this, run in terminal: pip install playwright
# Then run: playwright install

from playwright.sync_api import sync_playwright
import re

def intercept_stream_token():
    with sync_playwright() as p:
        # Launch browser invisibly
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Monitor all web requests happening in the background
        def handle_request(request):
            if "token=" in request.url:
                token_match = re.search(r'token=[^&]+', request.url)
                if token_match:
                    print(f"Caught Token from live network stream: {token_match.group(0)}")

        page.on("request", handle_request)
        
        # Navigate to the match page and wait for the video player to load
        print("Loading page and waiting for video connection...")
        page.goto("https://bingstream.info/live-sport/genoa-vs-ac-milan-1629485561.html")
        page.wait_for_timeout(5000)  # Wait 5 seconds for the player to request the .m3u8 file
        
        browser.close()

if __name__ == "__main__":
    intercept_stream_token()
