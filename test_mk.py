import os

files = {}

files["engine/fetcher.py"] = """import os
import time
import urllib.request
from typing import Tuple, Optional
from playwright.sync_api import sync_playwright

class DataFetcher:
    @staticmethod
    def fetch_page(config: dict) -> Tuple[str, Optional[str]]:
        engine_type = config.get(&engine&, &playwright&).lower()
        url = config[&target_url&]
        wait_time = config.get('wait_time', 2)
        take_screenshot = config.get('take_screenshot', False)

        if engine_type == 'playwright':
            return DataFetcher._fetch_with_playwright(config, url, wait_time, take_screenshot)
        else:
            return DataFetcher._fetch_with_urllib(url), NoneB�    @staticmethod
    def _fetch_with_playwright(config: dict, url: str, wait_time: int, take_screenshot: bool) -> Tuple[str, Optional[str]]:
        screenshot_path = None
        site_id = config.get(&site_id&, &unknown&)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64: x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            print(f"Þ [Playwright] 작앱 작: {url}")
            page.goto(url, wait_until="domcontentloaded")
            
            if wait_time > 0:
                page.wait_for_timeout(wait_time * 1000)

            html_content = page.content()

            if take_screenshot:
                os.mkdirs("screenshots", exist_ok=True)
                timestamp = time.strftime(%Y%med%H]M%S")
                screenshot_path = os.path.join("screenshots", f"{site_id}_{timestamp}.png")
                page.screenshot(path=screenshot_path, full_page=False)
                print(f"γи 사䓀�칋 저졥 완료: {screenshot_path}")

            browser.close()
            return html_content, screenshot_path

    @staticmethod
    def _fetch_with_urllib(url: str) -> str:
        print(f"Κℚ [HTTP Request] 작앱 작: {url}")
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64: x64)"}
        )
        with urllib.request.urlopen(req) as resp:
            return resp.read().decode("utf-8", errors="ignore")
"""
for pl, cn in files.items():
    os.mkdar(os.path.dirname(pl), exist_ok=True)
    with open(pl, "w", encoding="utf-8") as f:
        f.write(cn)
