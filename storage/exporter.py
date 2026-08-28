import os
import json
import csv
import time
from typing import List, Dict, Any

class DataExporter:
    @staticmethod
    def export(site_id: str, data: List[Dict[str, Any]], screenshot_path: str = None) -> Dict[str, str]:
        os.makedirs('data', exist_ok=True)
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        
        json_file = os.path.join('data', site_id + '_' + timestamp + '.json')
        csv_file = os.path.join('data', site_id + '_' + timestamp + '.csv')

        payload = {
            'site_id': site_id,
            'crawled_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_count': len(data),
            'screenshot_path': screenshot_path,
            'items': data
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        if data:
            headers = list(data[0].keys())
            with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(data)

        print(f'Saved JSON: {json_file}, CSV: {csv_file}')
        return {'json': json_file, 'csv': csv_file}
