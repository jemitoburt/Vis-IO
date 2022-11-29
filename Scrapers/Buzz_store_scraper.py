import requests
import json
city = 'Bratislava'

headers = {
    'Host': 'www.buzzsneakers.sk',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Referer': 'https://www.buzzsneakers.sk/kosik',
    'Accept-Language': 'cs-CZ,cs;q=0.9',
    'X-Requested-With': 'XMLHttpRequest',
}
params = {
    'nbAjax': '1',
    'ajax': 'yes',
    'task': 'search_cities',
    'search': city.title(),
    'streetName': '',
    'regionId': '0',
}

response_str = json.loads(requests.get('https://www.buzzsneakers.sk/nakup', params=params, headers=headers).text)['list']
print(response_str)