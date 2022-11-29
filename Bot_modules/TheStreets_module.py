import requests
import json
import time
from csv import DictReader
import csv
import unidecode
from discord_webhook import DiscordEmbed, DiscordWebhook
from colorama import Fore, init, Style
init(convert=True)
import datetime
import threading
import random
import os
from twocaptcha import TwoCaptcha

tasks = []

def read_tasks(csv_selected, path):
    with open (path + "/" + csv_selected, 'r') as read_obj:
        csv_dict_reader = DictReader(read_obj)
        for row in csv_dict_reader:
            tasks.append(row)

def random_proxy(path, proxy_file):
    with open(path + '/' + proxy_file + '.txt') as f:
        proxy_lines = f.readlines()
        f.close()
    if len(proxy_lines) > 0:
        random_line = random.choice(proxy_lines).strip()
    else:
        return None
    if len(random_line.split(":")) == 2:
        return {
            "http": "http://{}".format(random_line),
            "https": "http://{}".format(random_line),
        }
    elif len(random_line.split(":")) == 4:
        splitted = random_line.split(":")
        return {
            "http": "http://{0}:{1}@{2}:{3}".format(
                splitted[2], splitted[3], splitted[0], splitted[1]
            ),
            "https": "http://{0}:{1}@{2}:{3}".format(
                splitted[2], splitted[3], splitted[0], splitted[1]
            ),
        }

def get_csv_data(url, csv_selected, path, i):
    task = tasks[i]
    store = task['store']
    if url == None:
        url = task['url']
    size = task['size']
    first_name = task['firstName']
    last_name = task['lastName']
    zip_code = task['zip']
    phone = task['phone']
    email = task['email']
    city = task['city']
    country = task['country'].lower()
    address = task['address']
    house_number = ['houseNumber']
    shipping_method = task['shipping_method']

    return store, url, size, first_name, last_name, zip_code, phone, email, city, country, address, house_number, shipping_method


def get_product_info(url):
    headers = {
        'Host': 'www.thestreets.cz',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
        'accept-language': 'cs-CZ,cs;q=0.9',
        'referer': 'https://www.thestreets.cz/',
    }
    response = requests.get(url, headers=headers)

    customer_id = json.loads(response.text.split('window.checkout = ')[1].split('</script>')[0])['customerLoginUrl'].split('referer/')[1].split('/')[0]
    product_id = json.loads(response.text.split('Objects = [')[1].split('];')[0])['item_id']
    product_info_str = response.text.split('type="application/ld+json">')[1].split('</script>')[0]
    product_info_json = json.loads(product_info_str)
    product_name = product_info_json['name']
    product_sku = product_info_json['sku']
    product_image = product_info_json['image']
    product_price = str(product_info_json['offers'][1]['price']) +  product_info_json['offers'][1]['priceCurrency']
    form_key = response.text.split('"form_key" type="hidden" value="')[1].split('"')[0]

    product_sizes_str = response.text.split('<ul id="sizeSelector"')[1].split('</ul>')[0].split('<li class="size-selector-item"')
    product_sizes_lib = {}
    m = 1
    while m < len(product_sizes_str):
        size = product_sizes_str[m].split('EUR: </span>')[1].split('</div>')[0]
        pid = product_sizes_str[m].split('data-code="')[1].split('">')[0]
        product_sizes_lib[size] = pid
        m += 1

    return product_name, product_sku, product_image, product_price, product_sizes_lib, customer_id, product_id, form_key

def product_atc(product_id, size, product_sizes_lib, customer_id, phpsess_id, cf_cookie, url, form_key):
    cookies = {
        'mage-cache-sessid': 'true',
        'mage-cache-storage': '{}',
        'mage-cache-storage-section-invalidation': '{}',
        'mage-messages': '',
        'product_data_storage': '{}',
        'recently_compared_product': '{}',
        'recently_compared_product_previous': '{}',
        'recently_viewed_product': '{}',
        'recently_viewed_product_previous': '{}',
    }

    headers = {
        'Pragma': 'no-cache',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'cs-CZ,cs;q=0.9',
        'Cache-Control': 'no-cache',
        'Host': 'www.thestreets.cz',
        'Origin': 'https://www.thestreets.cz',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
        'Connection': 'keep-alive',
        'X-Requested-With': 'XMLHttpRequest',
    }

    files = {
        'product': (None, '"48460"'),
        'selected_configurable_option': (None, '""'),
        'related_product': (None, '""'),
        'item': (None, '"48460"'),
        'form_key': (None, '"' + form_key + '"'),
        'super_attribute[142]': (None, '"319"'),
        'qty': (None, '"1"'),
    }

    response = requests.post('https://www.thestreets.cz/checkout/cart/add/uenc/' + customer_id + '/product/48460/', cookies=cookies, headers=headers, files=files)
    print(response.text)





def phpsessid(customer_id):
    headers_cf = {
        'Host': 'www.thestreets.cz',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'accept-language': 'cs-CZ,cs;q=0.9',
    }

    response_cf = requests.get('https://www.thestreets.cz/', headers=headers_cf)

    cf_cookie = response_cf.cookies['__cf_bm']

    cookies = {
        'mage-cache-sessid': 'true',
        'mage-cache-storage': '{}',
        'mage-cache-storage-section-invalidation': '{}',
        'mage-messages': '',
        'product_data_storage': '{}',
        'recently_compared_product': '{}',
        'recently_compared_product_previous': '{}',
        'recently_viewed_product': '{}',
        'recently_viewed_product_previous': '{}',
        '__cf_bm': cf_cookie,
    }

    headers = {
        'Host': 'www.thestreets.cz',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
        'accept-language': 'cs-CZ,cs;q=0.9',
        'referer': 'https://www.thestreets.cz/',
    }

    response = requests.get('https://www.thestreets.cz/customer/account/login/referer/' + customer_id + '/', cookies=cookies, headers=headers)
    phpsess_id = response.cookies['PHPSESSID']
    
    return phpsess_id, cf_cookie

def run_tasks_the_streets(url, csv_selected, path, proxy_file, webhook_url, monitor_delay, checkout_delay, twocaptcha, i):
    store, url, size, first_name, last_name, zip_code, phone, email, city, country, address, house_number, shipping_method = get_csv_data(url, csv_selected, path, i)
    product_name, product_sku, product_image, product_price, product_sizes_lib, customer_id, product_id, form_key = get_product_info(url)
    phpsess_id, cf_cookie = phpsessid(customer_id)
    product_atc(product_id, size, product_sizes_lib, customer_id, phpsess_id, cf_cookie, url, form_key)


def the_streets(url, csv_selected, path, proxy_file, webhook_url, monitor_delay, checkout_delay, twocaptcha):
    read_tasks(csv_selected, path)
    running_tasks = []
    for i in range(len(tasks)):
        tasks_run = threading.Thread(target=run_tasks_the_streets, args=(url, csv_selected, path, proxy_file, webhook_url, monitor_delay, checkout_delay, twocaptcha, i))
        running_tasks.append(tasks_run)
    for t in running_tasks:
        t.start()
    for t in running_tasks:
        t.join()


