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

def get_csv_data(url, i):
    task = tasks[i]
    if url == None:
        url = task['url']
    size = task['size']
    mode = task['mode']
    first_name = task['firstName']
    last_name = task['lastName']
    zip_code = task['zip']
    phone = task['phone']
    email = task['email']
    city = task['city']
    country = task['country'].lower()
    address = task['address']
    house_number = task['homeNumber']
    return url, size, first_name, last_name, zip_code, phone, email, city, country, address, house_number, mode

def get_product_info(url, i, monitor_delay, checkout_delay, path, proxy_file):
    i += 1
    while True:
        now = datetime.datetime.now()
        headers = {
            'Host': 'www.queens.cz',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'accept-language': 'cs-CZ,cs;q=0.9',
        }
        try:

            response = requests.get(url, headers=headers, proxies=random_proxy(path, proxy_file))
            sizes = response.text.split("class='form-control'>")[1].split('</select>')[0].split('<option')
            m = 1
            size_pids = {}
            while m < len(sizes):
                size = sizes[m].split('eur ')[1].split(')</option>')[0]
                sizepid = sizes[m].split("value='")[1].split("'>US")[0]
                size_pids[size] = sizepid
                m += 1
            phpsessid = response.cookies['PHPSESSID']
            csrf = response.cookies['_csrf']
            cart_cookie = response.cookies['queens_cz_cart']
            currency_cookie = response.cookies['queens_cz_currency']

            product_id = json.loads(response.text.split('[];</script><script>dataLayer.push(')[1].split(');')[0].replace("'", '"'))['ecommerce']['detail']['products'][0]['id']
            product_name = json.loads(response.text.split('[];</script><script>dataLayer.push(')[1].split(');')[0].replace("'", '"'))['ecommerce']['detail']['products'][0]['name']
            product_category = json.loads(response.text.split('*/dataLayer.push(')[1].split(');/')[0].replace("'", '"').replace('"variant": variant,', ''))['ecommerce']['add']['products'][0]['category']
            product_price = json.loads(response.text.split('*/dataLayer.push(')[1].split(');/')[0].replace("'", '"').replace('"variant": variant,', ''))['ecommerce']['add']['products'][0]['price']
            product_price = round(product_price)
            atc_id = json.loads(response.text.split('*/dataLayer.push(')[1].split(');/')[0].replace("'", '"').replace('"variant": variant,', ''))['facebook_add_to_cart_event_id']
            csrf_token = response.text.split('name="_csrf" value="')[1].split('"')[0]
            print(Fore.GREEN + now.strftime(f"[%H:%M:%S - Queens CZ - TASK {i}]") + " - " + "Got product info" + Fore.RESET)
            time.sleep(checkout_delay)
            return size_pids, phpsessid, csrf, cart_cookie, currency_cookie, product_id, product_name, product_category, atc_id, product_price, csrf_token, i

        except:
            print(Fore.RED + now.strftime(f"[%H:%M:%S - Queens CZ - TASK {i}]") + " - " + "Connection error,retrying..." + Fore.RESET)
            time.sleep(monitor_delay)

def product_atc(size_pids, phpsessid, csrf, cart_cookie, currency_cookie, product_id, product_name, product_category, atc_id, product_price, item_id, size, csrf_token, i, monitor_delay, checkout_delay, path, proxy_file):
    while True:
        carts = 0
        now = datetime.datetime.now()
        size_pid = size_pids[size]
        if size == 'RANDOM':
            size_pid = random.choice(list(size_pids.values()))
        headers = {
            'Host': 'www.queens.cz',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'accept-language': 'cs-CZ,cs;q=0.9',
        }

        cookies = {
            'PHPSESSID': phpsessid,
            '_csrf': csrf,
            'queens_cz_cart': cart_cookie,
            'queens_cz_currency': currency_cookie,
        }

        params = {
            'id': product_id,
            'product_name': product_name,
            'product_category': product_category,
            'product_price': product_price,
            'event_id': atc_id,
        }

        data = {
            '_csrf': csrf_token,
            'variant': size_pid,
            'item_id': item_id,
            'quantity': '1',
        }


        try:
            atc_status = json.loads(requests.post('https://www.queens.cz/ajax/addcart/', params=params, cookies=cookies, headers=headers, data=data, proxies=random_proxy(path, proxy_file)).text)['ret']['status']
            if atc_status == 2:
                print(Fore.GREEN + now.strftime(f"[%H:%M:%S - Queens CZ - TASK {i}]") + " - " + "Added to cart" + Fore.RESET)
                carts += 1
                os.system('title "Vis IO 1.4 | Running: ' + str(len(tasks)) + ' tasks | Carts: ' + str(carts) + ' | Successful checkouts: 0 | Failed checkouts: 0 | Monitor delay: ' + str(monitor_delay*1000).split('.')[0] + ' | Checkout delay: ' + str(checkout_delay*1000).split('.')[0] + ' | Selected proxy file: ' + proxy_file + '"')
                time.sleep(checkout_delay)
                return carts
            else:
                print(Fore.RED + now.strftime(f"[%H:%M:%S - Queens CZ - TASK {i}]") + " - " + "Product out of stock" + Fore.RESET)
                time.sleep(monitor_delay)
        except:
            print(Fore.RED + now.strftime(f"[%H:%M:%S - Queens CZ - TASK {i}]") + " - " + "Connection error,retrying..." + Fore.RESET)
            time.sleep(monitor_delay)

def get_cart(phpsessid, csrf, cart_cookie, currency_cookie, i, monitor_delay, checkout_delay, path, proxy_file):
    while True:
        now = datetime.datetime.now()
        cookies = {
            'PHPSESSID': phpsessid,
            '_csrf': csrf,
            'queens_cz_cart': cart_cookie,
            'queens_cz_currency': currency_cookie,
        }

        headers = {
            'Host': 'www.queens.cz',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'accept-language': 'cs-CZ,cs;q=0.9',
            'referer': 'https://www.queens.cz/kosik/',
        }
        try:
            response = requests.get('https://www.queens.cz/kosik/doprava/', cookies=cookies, headers=headers, proxies=random_proxy(path, proxy_file))
            queens_cz_checkout_country = response.cookies['queens_cz_checkout_country']
            if response.status_code == 200:
                print(Fore.GREEN + now.strftime(f"[%H:%M:%S - Queens CZ - TASK {i}]") + " - " + "Got cart" + Fore.RESET)
                time.sleep(checkout_delay)
                return queens_cz_checkout_country
            else:
                print(Fore.RED + now.strftime(f"[%H:%M:%S - Queens CZ - TASK {i}]") + " - " + "Failed to get cart" + Fore.RESET)
                time.sleep(monitor_delay)
        except:
            print(Fore.RED + now.strftime(f"[%H:%M:%S - Queens CZ - TASK {i}]") + " - " + "Connection error,retrying..." + Fore.RESET)
            time.sleep(monitor_delay)

def get_shipping(phpsessid, csrf, cart_cookie, currency_cookie, i, monitor_delay, checkout_delay, path, proxy_file):
    while True:
        now = datetime.datetime.now()
        cookies = {
            'PHPSESSID': phpsessid,
            '_csrf': csrf,
            'queens_cz_cart': cart_cookie,
            'queens_cz_currency': currency_cookie,
        }

        headers = {
            'Host': 'www.queens.cz',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'cs-CZ,cs;q=0.9',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'referer': 'https://www.queens.cz/kosik/doprava/',
        }

        params = {
            'country': 'CZ',
            'shipping_id': '21',
            'payment_id': '3',
        }
        try:
            response = requests.get('https://www.queens.cz/ajax/getshippingtotal/', params=params, cookies=cookies, headers=headers, proxies=random_proxy(path, proxy_file))
            if response.status_code == 200:
                print(Fore.GREEN + now.strftime(f"[%H:%M:%S - Queens CZ - TASK {i}]") + " - " + "Got shipping info" + Fore.RESET)
                time.sleep(checkout_delay)
                return i
            else:
                print(Fore.RED + now.strftime(f"[%H:%M:%S - Queens CZ - TASK {i}]") + " - " + "Failed to get shipping inof" + Fore.RESET)
                time.sleep(monitor_delay)
        except:
            print(Fore.RED + now.strftime(f"[%H:%M:%S - Queens CZ - TASK {i}]") + " - " + "Connection error,retrying..." + Fore.RESET)
            time.sleep(monitor_delay)

def get_shipping_pickup(phpsessid, csrf, cart_cookie, currency_cookie, i, monitor_delay, checkout_delay, path, proxy_file):
    while True:
        now = datetime.datetime.now()

        cookies = {
            'PHPSESSID': phpsessid,
            '_csrf': csrf,
            'queens_cz_cart': cart_cookie,
            'queens_cz_currency': currency_cookie,
        }
        headers = {
            'Host': 'www.queens.cz',
            # Requests sorts cookies= alphabetically
            # 'Cookie': '__exponea_etc__=3f700107-d4b9-4715-838d-b860d38354cf; __exponea_time2__=0.06925368309020996; _fbp=fb.1.1669336190259.1263588345; _ga=GA1.2.1650512675.1669336181; _ga_NC66NG9247=GS1.1.1669336180.1.1.1669336197.52.0.0; _gid=GA1.2.1609100626.1669336190; _tt_enable_cookie=1; _ttp=12953e7d-aac1-4670-8e38-8b7edce42ddc; cto_bundle=l5WVMl8wJTJCN3BWdk1zMkclMkJraVJDcWlnWEtmSlhuNkdpZGMlMkZUaldMTTZFbXNIbWN2S0NwYnJ6c2NCUlo5VEg1MnNrVnVlTG1Hd3RaM0JTJTJCV3QlMkZEUWxNUXlPU1ZKYlFFSWRtR3Jha3ZmVDVaZjIlMkZ5VDlWVlVKMXVFUCUyQkdKZUQ5M0JQY3IlMkZBamk5VFQ0VXVEVVZqZjlsMnQ0VWQ2RExSRTRNdU5CJTJGRVRoQXM3cklCR3MlM0Q; _vsid=ff43c723-8a23-484b-9b3d-cff9d74c25c8; db_ui=43013e92-ae45-642e-7ab9-7ead5137f383; db_uicd=96caacd8-d5a3-ac52-28f0-5363d3645faa; gp_s=244088228.1669336181; _sp_id.8b6c=59bc87db986adc3d.1669336191.1.1669336197.1669336191; _sp_ses.8b6c=*; queens_cz_checkout_country=e3886c5b418a21cec5cadbbac27bc8c9605408f1a55843872bd130791ca8c4f1a%3A2%3A%7Bi%3A0%3Bs%3A26%3A%22queens_cz_checkout_country%22%3Bi%3A1%3Bs%3A2%3A%22CZ%22%3B%7D; cjConsent=MHxZfDB8Tnww; _dc_gtm_UA-39487499-3=1; _gat_UA-39487499-3=1; _gcl_au=1.1.698495736.1669336190; CookieConsent={stamp:%27wW6iT2j7+WAWpYcx1ga+bNrvBf08uL2jH/hUv7c26H8AmWPAdu6a+A==%27%2Cnecessary:true%2Cpreferences:true%2Cstatistics:true%2Cmarketing:true%2Cver:1%2Cutc:1669336189763%2Cregion:%27cz%27}; gp_e=0; gp_g=0; PHPSESSID=qbuo7ehn06cr80t2simrlmd6hi; _csrf=326513d9678bb24cc428d12405dc4bc8142b03319ca2155000197179e77cb4d3a%3A2%3A%7Bi%3A0%3Bs%3A5%3A%22_csrf%22%3Bi%3A1%3Bs%3A32%3A%22j-s5bFzfv2xpW28IxKWmT-wU7koFHpWl%22%3B%7D; queens_cz_cart=f4961021e1b636e1d67fda4c25f0e1cd5a88c7c368b7b0dc3c893ea4df33ff6da%3A2%3A%7Bi%3A0%3Bs%3A14%3A%22queens_cz_cart%22%3Bi%3A1%3Bs%3A32%3A%225950f2f0469b24d7142c6ba85fe793e9%22%3B%7D; queens_cz_currency=e97d8f31e27eb9cefd26a13bcd631a5bc11eb88e73b5c1662d15f71059c529e6a%3A2%3A%7Bi%3A0%3Bs%3A18%3A%22queens_cz_currency%22%3Bi%3A1%3Bs%3A3%3A%22CZK%22%3B%7D',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'cs-CZ,cs;q=0.9',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'referer': 'https://www.queens.cz/kosik/doprava/',
        }

        params = {
            'country': 'CZ',
            'shipping_id': '10',
            'payment_id': '2',
        }
        try:
            response = requests.get('https://www.queens.cz/ajax/getshippingtotal/', params=params, cookies=cookies, headers=headers, proxies = random_proxy(path, proxy_file))
            if response.status_code == 200:
                print(Fore.GREEN + now.strftime(f"[%H:%M:%S - Queens CZ - TASK {i}]") + " - " + "Submitted instore pickup" + Fore.RESET)
                time.sleep(checkout_delay)
                return i
            else:
                print(Fore.RED + now.strftime(f"[%H:%M:%S - Queens CZ - TASK {i}]") + " - " + "Failed to submit instore pickup" + Fore.RESET)
                time.sleep(monitor_delay)
        except:
            print(Fore.RED + now.strftime(f"[%H:%M:%S - Queens CZ - TASK {i}]") + " - " + "Connection error,retrying..." + Fore.RESET)
            time.sleep(monitor_delay)

def submit_shipping(phpsessid, csrf, cart_cookie, currency_cookie, csrf_token, i, monitor_delay, checkout_delay, path, proxy_file):
    while True:
        now = datetime.datetime.now()
        cookies = {
            'PHPSESSID': phpsessid,
            '_csrf': csrf,
            'queens_cz_cart': cart_cookie,
            'queens_cz_currency': currency_cookie,
        }
        headers = {
            'Host': 'www.queens.cz',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'content-type': 'multipart/form-data; boundary=----WebKitFormBoundary',
            'origin': 'https://www.queens.cz',
            'accept-language': 'cs-CZ,cs;q=0.9',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'referer': 'https://www.queens.cz/kosik/doprava/',
        }

        data = '------WebKitFormBoundary\nContent-Disposition: form-data; name="_csrf"\n\n' + csrf_token + '\n------WebKitFormBoundary\nContent-Disposition: form-data; name="search_pickup_post_city_15"\n\n\n------WebKitFormBoundary\nContent-Disposition: form-data; name="search_pickup_post_zip_15"\n\n\n------WebKitFormBoundary\nContent-Disposition: form-data; name="search_delivery_post_zip_2"\n\n\n------WebKitFormBoundary\nContent-Disposition: form-data; name="packeta-selector-branch-name"\n\n\n------WebKitFormBoundary\nContent-Disposition: form-data; name="packeta-selector-branch-id"\n\n\n------WebKitFormBoundary\nContent-Disposition: form-data; name="shipping"\n\n21\n------WebKitFormBoundary\nContent-Disposition: form-data; name="search_pickup_post_city_22"\n\n\n------WebKitFormBoundary\nContent-Disposition: form-data; name="search_pickup_post_zip_22"\n\n\n------WebKitFormBoundary\nContent-Disposition: form-data; name="payment"\n\n3\n------WebKitFormBoundary--\n'
        try:
            response = requests.post('https://www.queens.cz/kosik/doprava/', cookies=cookies, headers=headers, data=data, allow_redirects=False, proxies=random_proxy(path, proxy_file))
            queens_cz_checkout_afternoon_delivery = response.cookies['queens_cz_checkout_afternoon_delivery']
            queens_cz_checkout_payment = response.cookies['queens_cz_checkout_payment']
            queens_cz_checkout_shipping = response.cookies['queens_cz_checkout_shipping']
            queens_cz_checkout_zasilkovna_branch_id = response.cookies['queens_cz_checkout_zasilkovna_branch_id']
            queens_cz_checkout_zasilkovna_branch_name = response.cookies['queens_cz_checkout_zasilkovna_branch_name']
            if response.status_code == 302:
                print(Fore.GREEN + now.strftime(f"[%H:%M:%S - Queens CZ - TASK {i}]") + " - " + "Submitted shipping info" + Fore.RESET)
                time.sleep(checkout_delay)
                return queens_cz_checkout_afternoon_delivery, queens_cz_checkout_payment, queens_cz_checkout_shipping, queens_cz_checkout_zasilkovna_branch_id, queens_cz_checkout_zasilkovna_branch_name, i
            else:
                print(Fore.RED + now.strftime(f"[%H:%M:%S - Queens CZ - TASK {i}]") + " - " + "Failed to submit shipping info" + Fore.RESET)
                time.sleep(monitor_delay)
        except:
            print(Fore.RED + now.strftime(f"[%H:%M:%S - Queens CZ - TASK {i}]") + " - " + "Connection error,retrying..." + Fore.RESET)
            time.sleep(monitor_delay)

def submit_shipping_pickup(phpsessid, csrf, cart_cookie, currency_cookie, csrf_token, i, monitor_delay, checkout_delay, path, proxy_file):
    while True:
        now = datetime.datetime.now()
        cookies = {
                'PHPSESSID': phpsessid,
                '_csrf': csrf,
                'queens_cz_cart': cart_cookie,
                'queens_cz_currency': currency_cookie,
            }
        headers = {
            'Host': 'www.queens.cz',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'content-type': 'multipart/form-data; boundary=----WebKitFormBoundary',
            'origin': 'https://www.queens.cz',
            'accept-language': 'cs-CZ,cs;q=0.9',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'referer': 'https://www.queens.cz/kosik/doprava/',
        }

        data = '------WebKitFormBoundary\nContent-Disposition: form-data; name="_csrf"\n\n' + csrf_token + '\n------WebKitFormBoundary\nContent-Disposition: form-data; name="search_pickup_post_city_15"\n\n\n------WebKitFormBoundary\nContent-Disposition: form-data; name="search_pickup_post_zip_15"\n\n\n------WebKitFormBoundary\nContent-Disposition: form-data; name="search_delivery_post_zip_2"\n\n\n------WebKitFormBoundary\nContent-Disposition: form-data; name="packeta-selector-branch-name"\n\n\n------WebKitFormBoundary\nContent-Disposition: form-data; name="packeta-selector-branch-id"\n\n\n------WebKitFormBoundary\nContent-Disposition: form-data; name="search_pickup_post_city_22"\n\n\n------WebKitFormBoundary\nContent-Disposition: form-data; name="search_pickup_post_zip_22"\n\n\n------WebKitFormBoundary\nContent-Disposition: form-data; name="shipping"\n\n10\n------WebKitFormBoundary\nContent-Disposition: form-data; name="payment"\n\n2\n------WebKitFormBoundary--\n'
        try:
            response = requests.post('https://www.queens.cz/kosik/doprava/', cookies=cookies, headers=headers, data=data, proxies=random_proxy(path, proxy_file), allow_redirects=False)
            queens_cz_checkout_afternoon_delivery = response.cookies['queens_cz_checkout_afternoon_delivery']
            queens_cz_checkout_payment = response.cookies['queens_cz_checkout_payment']
            queens_cz_checkout_shipping = response.cookies['queens_cz_checkout_shipping']
            queens_cz_checkout_zasilkovna_branch_id = response.cookies['queens_cz_checkout_zasilkovna_branch_id']
            queens_cz_checkout_zasilkovna_branch_name = response.cookies['queens_cz_checkout_zasilkovna_branch_name']
            if response.status_code == 302:
                print(Fore.GREEN + now.strftime(f"[%H:%M:%S - Queens CZ - TASK {i}]") + " - " + "Submitted pickup info" + Fore.RESET)
                time.sleep(checkout_delay)
                return queens_cz_checkout_afternoon_delivery, queens_cz_checkout_payment, queens_cz_checkout_shipping, queens_cz_checkout_zasilkovna_branch_id, queens_cz_checkout_zasilkovna_branch_name, i
            else:
                print(Fore.RED + now.strftime(f"[%H:%M:%S - Queens CZ - TASK {i}]") + " - " + "Failed to submit pickup info" + Fore.RESET)
                time.sleep(monitor_delay)
        except:
            print(Fore.RED + now.strftime(f"[%H:%M:%S - Queens CZ - TASK {i}]") + " - " + "Connection error,retrying..." + Fore.RESET)
            time.sleep(monitor_delay)

def get_billing_info(queens_cz_checkout_afternoon_delivery, queens_cz_checkout_payment, queens_cz_checkout_shipping, queens_cz_checkout_zasilkovna_branch_id, queens_cz_checkout_zasilkovna_branch_name, phpsessid, csrf, cart_cookie, currency_cookie, i, monitor_delay, checkout_delay, path, proxy_file):
    while True:
        now = datetime.datetime.now()
        cookies = {
            'queens_cz_checkout_afternoon_delivery': queens_cz_checkout_afternoon_delivery,
            'queens_cz_checkout_payment': queens_cz_checkout_payment,
            'queens_cz_checkout_shipping': queens_cz_checkout_shipping,
            'queens_cz_checkout_zasilkovna_branch_id': queens_cz_checkout_zasilkovna_branch_id,
            'queens_cz_checkout_zasilkovna_branch_name': queens_cz_checkout_zasilkovna_branch_name,
            'PHPSESSID': phpsessid,
            '_csrf': csrf,
            'queens_cz_cart': cart_cookie,
            'queens_cz_currency': currency_cookie,
        }

        headers = {
            'Host': 'www.queens.cz',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'accept-language': 'cs-CZ,cs;q=0.9',
            'referer': 'https://www.queens.cz/kosik/doprava/',
        }
        try:
            response = requests.get('https://www.queens.cz/kosik/udaje/', cookies=cookies, headers=headers, proxies=random_proxy(path, proxy_file))
            if response.status_code == 200:
                print(Fore.GREEN + now.strftime(f"[%H:%M:%S - Queens CZ - TASK {i}]") + " - " + "Got billing info" + Fore.RESET)
                time.sleep(checkout_delay)
                return i
            else:
                print(Fore.RED + now.strftime(f"[%H:%M:%S - Queens CZ - TASK {i}]") + " - " + "Error getting billing info" + Fore.RESET)
                time.sleep(monitor_delay)
        except:
            print(Fore.RED + now.strftime(f"[%H:%M:%S - Queens CZ - TASK {i}]") + " - " + "Connection error,retrying..." + Fore.RESET)
            time.sleep(monitor_delay)

def submit_billing(queens_cz_checkout_afternoon_delivery, queens_cz_checkout_payment, queens_cz_checkout_shipping, queens_cz_checkout_zasilkovna_branch_id, queens_cz_checkout_zasilkovna_branch_name, phpsessid, csrf, cart_cookie, currency_cookie, queens_cz_checkout_country, csrf_token, first_name, last_name, zip_code, phone, email, city, country, address, house_number, i, webhook_url, url, monitor_delay, path, proxy_file, carts, checkout_delay):
    while True:
        checkouts = 0
        failed_checkouts = 0
        now = datetime.datetime.now()
        cookies = {
            'queens_cz_checkout_afternoon_delivery': queens_cz_checkout_afternoon_delivery,
            'queens_cz_checkout_payment': queens_cz_checkout_payment,
            'queens_cz_checkout_shipping': queens_cz_checkout_shipping,
            'queens_cz_checkout_zasilkovna_branch_id': queens_cz_checkout_zasilkovna_branch_id,
            'queens_cz_checkout_zasilkovna_branch_name': queens_cz_checkout_zasilkovna_branch_name,
            'queens_cz_checkout_country': queens_cz_checkout_country,
            'PHPSESSID': phpsessid,
            '_csrf': csrf,
            'queens_cz_cart': cart_cookie,
            'queens_cz_currency': currency_cookie,
        }

        headers = {
            'Host': 'www.queens.cz',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'origin': 'https://www.queens.cz',
            'accept-language': 'cs-CZ,cs;q=0.9',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'referer': 'https://www.queens.cz/kosik/udaje/',
        }

        data = {
            '_csrf': csrf_token,
            'CheckoutForm[first_name]': first_name,
            'CheckoutForm[surname]': last_name,
            'CheckoutForm[company_name]': '',
            'CheckoutForm[email]': email,
            'CheckoutForm[phone]': '+420' + phone,
            'CheckoutForm[street]': address,
            'CheckoutForm[street_number]': house_number,
            'CheckoutForm[city]': city.title(),
            'CheckoutForm[zip]': zip_code.strip(),
            'CheckoutForm[note]': '',
            'CheckoutForm[accept_tc]': '1',
            'CheckoutForm[is_not_heureka]': '0',
            'CheckoutForm[state_id]': '1',
            'finish_order': '',
        }

        try:
            response = requests.post('https://www.queens.cz/kosik/udaje/', cookies=cookies, headers=headers, data=data, allow_redirects=True, proxies=random_proxy(path, proxy_file))
            if response.status_code == 302 or response.status_code == 200:
                print(Fore.GREEN + now.strftime(f"[%H:%M:%S - Queens CZ - TASK {i}]") + " - " + "Order confirmed" + Fore.RESET)
                checkouts += 1
                os.system('title "Vis IO 1.4 | Running: ' + str(len(tasks)) + ' tasks | Carts: ' + str(carts) + ' | Successful checkouts: ' + str(checkouts) + ' | Failed checkouts: ' + str(failed_checkouts) + ' | Monitor delay: ' + str(monitor_delay*1000).split('.')[0] + ' | Checkout delay: ' + str(checkout_delay*1000).split('.')[0] + ' | Selected proxy file: ' + proxy_file + '"')
                order_number = json.loads(response.text.split('[];</script><script>dataLayer.push(')[1].split(');')[0].replace("'", '"'))['ecommerce']['purchase']['actionField']['id']
                order_price = str(json.loads(response.text.split('[];</script><script>dataLayer.push(')[1].split(');')[0].replace("'", '"'))['ecommerce']['purchase']['actionField']['revenue'])
                product_name = json.loads(response.text.split('[];</script><script>dataLayer.push(')[1].split(');')[0].replace("'", '"'))['ecommerce']['purchase']['products'][0]['name']
                product_size = json.loads(response.text.split('[];</script><script>dataLayer.push(')[1].split(');')[0].replace("'", '"'))['ecommerce']['purchase']['products'][0]['variant']
                webhook = DiscordWebhook(url=webhook_url)
                embed = DiscordEmbed(title = 'Succesfully checked out', color = 5202069, url = url)
                embed.add_embed_field(name = 'Product', value = product_name)
                embed.add_embed_field(name = 'Size', value = product_size)
                embed.add_embed_field(name = 'Order number', value = '||' + str(order_number) + '||')
                embed.add_embed_field(name = 'Price', value = order_price)
                embed.add_embed_field(name = 'Email', value = email)
                embed.set_footer(text = 'Queens CZ by @je_mi_to_burt#2604'.format(country.upper()), icon_url = 'https://i.imgur.com/sVNBL0b.png')
                webhook.add_embed(embed)
                response = webhook.execute()

                webhook = DiscordWebhook(url='https://discord.com/api/webhooks/1042009798440398878/27Ed3Q_36kU9fwQNFFT4UF3gZMOeuLlWRbI1MZE006zFfb2MzHH9vOt0eNFkxJKaRMw6')
                embed = DiscordEmbed(title = 'Succesfully checked out', color = 5202069, url = url)
                embed.add_embed_field(name = 'Product', value = product_name)
                embed.add_embed_field(name = 'Price', value = order_price)
                embed.set_footer(text = 'Queens CZ by @je_mi_to_burt#2604'.format(country.upper()), icon_url = 'https://i.imgur.com/sVNBL0b.png')
                webhook.add_embed(embed)
                response = webhook.execute()
                input()
                break
            else:
                print(Fore.RED + now.strftime(f"[%H:%M:%S - Queens CZ - TASK {i}]") + " - " + "Failed to checkout" + Fore.RESET)
                failed_checkouts += 1
                os.system('title "Vis IO 1.4 | Running: ' + str(len(tasks)) + ' tasks | Carts: ' + str(carts) + ' | Successful checkouts: ' + str(checkouts) + ' | Failed checkouts: ' + str(failed_checkouts) + ' | Monitor delay: ' + str(monitor_delay*1000).split('.')[0] + ' | Checkout delay: ' + str(checkout_delay*1000).split('.')[0] + ' | Selected proxy file: ' + proxy_file + '"')
                input()
                break
        except:
            print(Fore.RED + now.strftime(f"[%H:%M:%S - Queens CZ - TASK {i}]") + " - " + "Connection error,retrying..." + Fore.RESET)
            time.sleep(monitor_delay)
        
def submit_billing_pickup(queens_cz_checkout_afternoon_delivery, queens_cz_checkout_payment, queens_cz_checkout_shipping, queens_cz_checkout_zasilkovna_branch_id, queens_cz_checkout_zasilkovna_branch_name, phpsessid, csrf, cart_cookie, currency_cookie, queens_cz_checkout_country, csrf_token, first_name, last_name, phone, email, country, i, webhook_url, url, monitor_delay, path, proxy_file, carts, checkout_delay):
    while True:
        checkouts = 0
        failed_checkouts = 0
        now = datetime.datetime.now()
        cookies = {
            'queens_cz_checkout_afternoon_delivery': queens_cz_checkout_afternoon_delivery,
            'queens_cz_checkout_payment': queens_cz_checkout_payment,
            'queens_cz_checkout_shipping': queens_cz_checkout_shipping,
            'queens_cz_checkout_zasilkovna_branch_id': queens_cz_checkout_zasilkovna_branch_id,
            'queens_cz_checkout_zasilkovna_branch_name': queens_cz_checkout_zasilkovna_branch_name,
            'queens_cz_checkout_country': queens_cz_checkout_country,
            'PHPSESSID': phpsessid,
            '_csrf': csrf,
            'queens_cz_cart': cart_cookie,
            'queens_cz_currency': currency_cookie,
        }
        headers = {
            'Host': 'www.queens.cz',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'origin': 'https://www.queens.cz',
            'accept-language': 'cs-CZ,cs;q=0.9',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'referer': 'https://www.queens.cz/kosik/udaje/',
        }

        data = {
            '_csrf': csrf_token,
            'PickupForm[first_name]': first_name,
            'PickupForm[surname]': last_name,
            'PickupForm[email]': email,
            'PickupForm[phone]': '+420' + phone,
            'PickupForm[note]': '',
            'PickupForm[accept_tc]': '1',
            'PickupForm[is_not_heureka]': '0',
            'finish_order': '',
        }
        
        try:
            response = requests.post('https://www.queens.cz/kosik/udaje/', cookies=cookies, headers=headers, data=data, proxies = random_proxy(path, proxy_file))
            if response.status_code == 302 or response.status_code == 200:
                print(Fore.GREEN + now.strftime(f"[%H:%M:%S - Queens CZ - TASK {i}]") + " - " + "Order confirmed" + Fore.RESET)
                checkouts += 1
                os.system('title "Vis IO 1.4 | Running: ' + str(len(tasks)) + ' tasks | Carts: ' + str(carts) + ' | Successful checkouts: ' + str(checkouts) + ' | Failed checkouts: ' + str(failed_checkouts) + ' | Monitor delay: ' + str(monitor_delay*1000).split('.')[0] + ' | Checkout delay: ' + str(checkout_delay*1000).split('.')[0] + ' | Selected proxy file: ' + proxy_file + '"')
                order_number = json.loads(response.text.split('[];</script><script>dataLayer.push(')[1].split(');')[0].replace("'", '"'))['ecommerce']['purchase']['actionField']['id']
                order_price = str(json.loads(response.text.split('[];</script><script>dataLayer.push(')[1].split(');')[0].replace("'", '"'))['ecommerce']['purchase']['actionField']['revenue'])
                product_name = json.loads(response.text.split('[];</script><script>dataLayer.push(')[1].split(');')[0].replace("'", '"'))['ecommerce']['purchase']['products'][0]['name']
                product_size = json.loads(response.text.split('[];</script><script>dataLayer.push(')[1].split(');')[0].replace("'", '"'))['ecommerce']['purchase']['products'][0]['variant']
                webhook = DiscordWebhook(url=webhook_url)
                embed = DiscordEmbed(title = 'Succesfully reserved item', color = 5202069, url = url)
                embed.add_embed_field(name = 'Product', value = product_name)
                embed.add_embed_field(name = 'Size', value = product_size)
                embed.add_embed_field(name = 'Order number', value = '||' + str(order_number) + '||')
                embed.add_embed_field(name = 'Price', value = order_price)
                embed.add_embed_field(name = 'Email', value = email)
                embed.set_footer(text = 'Queens CZ by @je_mi_to_burt#2604'.format(country.upper()), icon_url = 'https://i.imgur.com/sVNBL0b.png')
                webhook.add_embed(embed)
                response = webhook.execute()

                webhook = DiscordWebhook(url='https://discord.com/api/webhooks/1042009798440398878/27Ed3Q_36kU9fwQNFFT4UF3gZMOeuLlWRbI1MZE006zFfb2MzHH9vOt0eNFkxJKaRMw6')
                embed = DiscordEmbed(title = 'Succesfully reserved item', color = 5202069, url = url)
                embed.add_embed_field(name = 'Product', value = product_name)
                embed.add_embed_field(name = 'Price', value = order_price)
                embed.set_footer(text = 'Queens CZ by @je_mi_to_burt#2604'.format(country.upper()), icon_url = 'https://i.imgur.com/sVNBL0b.png')
                webhook.add_embed(embed)
                response = webhook.execute()
                input()
                break
            else:
                print(Fore.RED + now.strftime(f"[%H:%M:%S - Queens CZ - TASK {i}]") + " - " + "Failed to checkout" + Fore.RESET)
                failed_checkouts += 1
                os.system('title "Vis IO 1.4 | Running: ' + str(len(tasks)) + ' tasks | Carts: ' + str(carts) + ' | Successful checkouts: ' + str(checkouts) + ' | Failed checkouts: ' + str(failed_checkouts) + ' | Monitor delay: ' + str(monitor_delay*1000).split('.')[0] + ' | Checkout delay: ' + str(checkout_delay*1000).split('.')[0] + ' | Selected proxy file: ' + proxy_file + '"')
                input()
                break
        except:
            print(Fore.RED + now.strftime(f"[%H:%M:%S - Queens CZ - TASK {i}]") + " - " + "Connection error,retrying..." + Fore.RESET)
            time.sleep(monitor_delay)

def run_tasks_queens(url, path, proxy_file, webhook_url, monitor_delay, checkout_delay, twocaptcha, i):
    url, size, first_name, last_name, zip_code, phone, email, city, country, address, house_number, mode = get_csv_data(url, i)
    item_id = url.split('/')[3].split('/')[0]
    size_pids, phpsessid, csrf, cart_cookie, currency_cookie, product_id, product_name, product_category, atc_id, product_price, csrf_token, i = get_product_info(url, i, monitor_delay, checkout_delay, path, proxy_file)
    carts = product_atc(size_pids, phpsessid, csrf, cart_cookie, currency_cookie, product_id, product_name, product_category, atc_id, product_price, item_id, size, csrf_token, i, monitor_delay, checkout_delay, path, proxy_file)
    queens_cz_checkout_country = get_cart(phpsessid, csrf, cart_cookie, currency_cookie, i, monitor_delay, checkout_delay, path, proxy_file)
    if mode == 'NORMAL':
        i = get_shipping(phpsessid, csrf, cart_cookie, currency_cookie, i, monitor_delay, checkout_delay, path, proxy_file)
        queens_cz_checkout_afternoon_delivery, queens_cz_checkout_payment, queens_cz_checkout_shipping, queens_cz_checkout_zasilkovna_branch_id, queens_cz_checkout_zasilkovna_branch_name, i = submit_shipping(phpsessid, csrf, cart_cookie, currency_cookie, csrf_token, i, monitor_delay, checkout_delay, path, proxy_file)
        i = get_billing_info(queens_cz_checkout_afternoon_delivery, queens_cz_checkout_payment, queens_cz_checkout_shipping, queens_cz_checkout_zasilkovna_branch_id, queens_cz_checkout_zasilkovna_branch_name, phpsessid, csrf, cart_cookie, currency_cookie, i, monitor_delay, checkout_delay, path, proxy_file)
        submit_billing(queens_cz_checkout_afternoon_delivery, queens_cz_checkout_payment, queens_cz_checkout_shipping, queens_cz_checkout_zasilkovna_branch_id, queens_cz_checkout_zasilkovna_branch_name, phpsessid, csrf, cart_cookie, currency_cookie, queens_cz_checkout_country, csrf_token, first_name, last_name, zip_code, phone, email, city, country, address, house_number, i, webhook_url, url, monitor_delay, path, proxy_file, carts, checkout_delay)
    elif mode == 'PICKUP':
        i = get_shipping_pickup(phpsessid, csrf, cart_cookie, currency_cookie, i, monitor_delay, checkout_delay, path, proxy_file)
        queens_cz_checkout_afternoon_delivery, queens_cz_checkout_payment, queens_cz_checkout_shipping, queens_cz_checkout_zasilkovna_branch_id, queens_cz_checkout_zasilkovna_branch_name, i = submit_shipping_pickup(phpsessid, csrf, cart_cookie, currency_cookie, csrf_token, i, monitor_delay, checkout_delay, path, proxy_file)
        i = get_billing_info(queens_cz_checkout_afternoon_delivery, queens_cz_checkout_payment, queens_cz_checkout_shipping, queens_cz_checkout_zasilkovna_branch_id, queens_cz_checkout_zasilkovna_branch_name, phpsessid, csrf, cart_cookie, currency_cookie, i, monitor_delay, checkout_delay, path, proxy_file)
        submit_billing_pickup(queens_cz_checkout_afternoon_delivery, queens_cz_checkout_payment, queens_cz_checkout_shipping, queens_cz_checkout_zasilkovna_branch_id, queens_cz_checkout_zasilkovna_branch_name, phpsessid, csrf, cart_cookie, currency_cookie, queens_cz_checkout_country, csrf_token, first_name, last_name, phone, email, country, i, webhook_url, url, monitor_delay, path, proxy_file, carts, checkout_delay)

def queens(url, csv_selected, path, proxy_file, webhook_url, monitor_delay, checkout_delay, twocaptcha):
    read_tasks(csv_selected, path)
    running_tasks = []
    os.system('title "Vis IO 1.4 | Running: ' + str(len(tasks)) + ' tasks | Carts: 0 | Successful checkouts: 0 | Failed checkouts: 0 | Monitor delay: ' + str(monitor_delay*1000).split('.')[0] + ' | Checkout delay: ' + str(checkout_delay*1000).split('.')[0] + ' | Selected proxy file: ' + proxy_file + '"')
    for i in range(len(tasks)):
        tasks_run = threading.Thread(target=run_tasks_queens, args=(url, path, proxy_file, webhook_url, monitor_delay, checkout_delay, twocaptcha, i))
        running_tasks.append(tasks_run)
    if len(tasks) > 10:
        for t in running_tasks:
            time.sleep(0.5)
            t.start()
        for t in running_tasks:
            time.sleep(0.5)
            t.join()
    else:
        for t in running_tasks:
            t.start()
        for t in running_tasks:
            t.join()
