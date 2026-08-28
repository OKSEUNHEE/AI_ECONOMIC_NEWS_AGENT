import os
import glob
import json
from flask import Flask, render_template, request, jsonify, send_from_directory
from engine.parser import ConfigParser
from engine.fetcher import DataFetcher
from engine.extractor import DataExtractor
from storage.exporter import DataExporter

app = Flask(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), 'screenshots')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/news')
def get_news():
    keyword = request.args.get('keyword', '').strip().lower()
    site_id = request.args.get('site_id', '').strip()

    all_items = []
    json_files = glob.glob(os.path.join(DATA_DIR, '*.json'))
    json_files.sort(key=os.path.getmtime, reverse=True)

    seen_links = set()

    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            cur_site_id = data.get('site_id', '')
            if site_id and cur_site_id != site_id:
                continue

            crawled_at = data.get('crawled_at', '')
            items = data.get('items', [])
            screenshot_path = data.get('screenshot_path', '')
            screenshot_file = os.path.basename(screenshot_path) if screenshot_path else ''

            for item in items:
                link = item.get('link', '')
                if link and link in seen_links:
                    continue
                if link:
                    seen_links.add(link)

                title = item.get('title', '')
                press = item.get('press', '경제뉴스')

                if keyword:
                    if keyword not in title.lower() and keyword not in press.lower():
                        continue

                all_items.append({
                    'title': title,
                    'link': link,
                    'press': press if press else '경제뉴스',
                    'site_id': cur_site_id,
                    'crawled_at': crawled_at,
                    'screenshot': screenshot_file
                })
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    return jsonify({
        'total': len(all_items),
        'items': all_items
    })

@app.route('/api/crawl', methods=['POST'])
def trigger_crawl():
    body = request.get_json() or {}
    search_keyword = body.get('keyword', '').strip()

    if search_keyword:
        import urllib.parse
        encoded_kw = urllib.parse.quote(search_keyword)
        cfg = {
            'site_id': f"search_{search_keyword}",
            'site_name': f"네이버 뉴스 - {search_keyword}",
            'engine': 'playwright',
            'target_url': f"https://search.naver.com/search.naver?where=news&query={encoded_kw}",
            'wait_time': 2,
            'take_screenshot': True,
            'selectors': {
                'container': 'ul.list_news > li, div.news_wrap',
                'fields': {
                    'title': 'a.news_tit',
                    'link': 'a.news_tit::attr(href)',
                    'press': 'a.info.press'
                }
            }
        }
        try:
            html_content, screenshot_path = DataFetcher.fetch_page(cfg)
            data = DataExtractor.extract(html_content, cfg)
            if data:
                DataExporter.export(cfg['site_id'], data, screenshot_path)
                return jsonify({'success': True, 'count': len(data), 'message': f"'{search_keyword}' 관련 뉴스 {len(data)}건 수집 완료!"})
            else:
                return jsonify({'success': False, 'message': '추출된 뉴스가 없습니다.'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})

    else:
        configs = ConfigParser.load_all_configs('configs')
        total_count = 0
        for cfg in configs:
            try:
                html_content, screenshot_path = DataFetcher.fetch_page(cfg)
                data = DataExtractor.extract(html_content, cfg)
                if data:
                    DataExporter.export(cfg['site_id'], data, screenshot_path)
                    total_count += len(data)
            except Exception as e:
                print(f"Crawl error: {e}")

        return jsonify({'success': True, 'count': total_count, 'message': f'전체 크롤링 완료 ({total_count}건 수집)'})

@app.route('/screenshots/<filename>')
def get_screenshot(filename):
    return send_from_directory(SCREENSHOT_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)