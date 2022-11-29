import requests

cookies = {
    'form_key': 'aavfIhDlBPTd6R72',
    'mage-cache-sessid': 'true',
    'mage-cache-storage': '{}',
    'mage-cache-storage-section-invalidation': '{}',
    'mage-messages': '',
    'product_data_storage': '{}',
    'recently_compared_product': '{}',
    'recently_compared_product_previous': '{}',
    'recently_viewed_product': '{}',
    'recently_viewed_product_previous': '{}',
    '__cf_bm': 'fRfhl1AOFT_7XjVIF48a_jxLGUwBHZussop0weXBxvs-1669337997-0-AXko74po89zluLmQkqjDTR9f2VwLfmb1CDLM6h4wdhsGyn7CSzBkjm4wTuy/NjFvlwXXGp4EHObZ/hVTkK9B1iI=',
}

headers = {
    'Host': 'www.thestreets.cz',
    'content-type': 'multipart/form-data; boundary=----WebKitFormBoundary',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'x-requested-with': 'XMLHttpRequest',
    'accept-language': 'cs-CZ,cs;q=0.9',
    'origin': 'https://www.thestreets.cz',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'referer': 'https://www.thestreets.cz/nike-cosmic-unity-2-we-fly-to-defy-dh1537-602',
}

data = '------WebKitFormBoundary\nContent-Disposition: form-data; name="product"\n\n49276\n------WebKitFormBoundary\nContent-Disposition: form-data; name="selected_configurable_option"\n\n\n------WebKitFormBoundary\nContent-Disposition: form-data; name="related_product"\n\n\n------WebKitFormBoundary\nContent-Disposition: form-data; name="item"\n\n49276\n------WebKitFormBoundary\nContent-Disposition: form-data; name="form_key"\n\nTyrsD7sPJh2yPUdz\n------WebKitFormBoundary\nContent-Disposition: form-data; name="super_attribute[142]"\n\n322\n------WebKitFormBoundary\nContent-Disposition: form-data; name="qty"\n\n1\n------WebKitFormBoundary--\n'

response = requests.post('https://www.thestreets.cz/checkout/cart/add/uenc/aHR0cHM6Ly93d3cudGhlc3RyZWV0cy5jei9uaWtlLWNvc21pYy11bml0eS0yLXdlLWZseS10by1kZWZ5LWRoMTUzNy02MDI%2C/product/49276/', cookies=cookies, headers=headers, data=data)
export = open("export.html", "w")
export.write(response.text)
export.close()