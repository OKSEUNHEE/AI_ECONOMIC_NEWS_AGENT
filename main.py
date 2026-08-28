import os
import sys
from engine.parser import ConfigParser
from engine.fetcher import DataFetcher
from engine.extractor import DataExtractor
from storage.exporter import DataExporter

def run_crawler():
    print("=" * 60)
    print("🚀 [YAML Based News Crawler Engine] Starting...")
    print("=" * 60)

    configs = ConfigParser.load_all_configs('configs')
    if not configs:
        print("❌ No valid YAML configs found in 'configs' directory.")
        return

    print(f"📋 Loaded {len(configs)} crawler configs.")

    for idx, cfg in enumerate(configs, 1):
        site_name = cfg.get('site_name', cfg['site_id'])
        print(f"[{idx}/{len(configs)}] Processing: '{site_name}'...")

        try:
            html_content, screenshot_path = DataFetcher.fetch_page(cfg)
            data = DataExtractor.extract(html_content, cfg)
            
            if data:
                DataExporter.export(cfg['site_id'], data, screenshot_path)
                print(f"✅ Successfully collected {len(data)} items.")
            else:
                print("⚠️ No data extracted. Check your CSS Selectors.")

        except Exception as e:
            print(f"❌ Error while crawling ({site_name}): {e}")
        
        print("-" * 60)

    print("🎉 All crawling tasks completed successfully!")

if __name__ == '__main__':
    run_crawler()