from bs4 import BeautifulSoup
from typing import Dict, Any, List
from urllib.parse import urljoin

class DataExtractor:
    @staticmethod
    def extract(html_content: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html_content, 'lxml')
        selectors = config.get('selectors', {})
        container_selector = selectors.get('container')
        fields = selectors.get('fields', {})
        base_url = config.get('target_url', '')

        items = soup.select(container_selector)
        results = []

        print(f'Found {len(items)} items using container [{container_selector}]')

        for item in items:
            row = {}
            valid_row = False

            for field_name, selector_rule in fields.items():
                val = DataExtractor._extract_field(item, selector_rule, base_url)
                row[field_name] = val
                if val:
                    valid_row = True

            if valid_row:
                results.append(row)

        return results

    @staticmethod
    def _extract_field(item_element, selector_rule: str, base_url: str) -> str:
        if '::attr(' in selector_rule:
            css_sel, attr_part = selector_rule.split('::attr(')
            attr_name = attr_part.rstrip(')')
            target = item_element.select_one(css_sel.strip()) if css_sel.strip() else item_element
            if target and target.has_attr(attr_name):
                val = target[attr_name]
                if attr_name in ['href', 'src']:
                    val = urljoin(base_url, val)
                return val.strip()
            return ''
        else:
            target = item_element.select_one(selector_rule.strip())
            if target:
                return target.get_text(strip=True)
            return ''
