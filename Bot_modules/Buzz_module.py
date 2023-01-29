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

def op_mode_info(path, shipping_info):
    read = open(path + '/Modules_configs/' + shipping_info + '.json')
    data = json.load(read)
    city_name = data['city_name']
    zip_order = data['zip_order']
    city_order = data['city_order']
    return city_name, zip_order, city_order

def get_csv_data(url, i):
    task = tasks[i]
    if url == None:
        url = task['url']
    first_name = task['firstName']
    last_name = task['lastName']
    phone = task['phone']
    email = task['email']
    country = task['country'].lower()
    address = task['address']
    home_number = task['homeNumber']
    size_task = task['size']
    shipping_info = task['shipping_method']
    
    return url, first_name, last_name, phone, email, country, address, home_number, size_task, shipping_info

def get_product_info(monitor_delay, checkout_delay, url, proxy_file, path, country, i):
    while True:
        i += 1
        now = datetime.datetime.now()
        headers_product_page = {
            'Host': 'www.buzzsneakers.{}'.format(country),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            #'Accept-Language': 'cs-CZ,cs;q=0.9',
            'Referer': 'https://www.buzzsneakers.{}/tenisky/'.format(country),
        }

        response_product_page = requests.get(url, headers=headers_product_page, proxies=random_proxy(path, proxy_file))

        if response_product_page.status_code == 200:
            try:
                jsonStr = json.loads(response_product_page.text.split('<script type="application/ld+json">')[2].split('</script>')[0])
                product_name = jsonStr['name']
                product_price = jsonStr['offers']['price'] + ' ' + jsonStr['offers']['priceCurrency']
                product_sku = jsonStr['sku']
                product_image = 'https://www.buzzsneakers.cz/files/images/slike_proizvoda/media/DD1/' + product_sku + '/images/' + product_sku + '.jpg'
            except IndexError:
                #try:
                product_name = json.loads(response_product_page.text.split('window.nbMetricObject.NB_METRIC_DATA  = ')[1].split(';')[0])['name'] + '\n' + json.loads(response_product_page.text.split('window.nbMetricObject.NB_METRIC_DATA  = ')[1].split(';')[0])['productCode']
                product_price = json.loads(response_product_page.text.split('window.nbMetricObject.NB_METRIC_DATA  = ')[1].split(';')[0])['price']
                if int(product_price) == 0:
                    product_price = 'N/A'
                product_sku = json.loads(response_product_page.text.split('window.nbMetricObject.NB_METRIC_DATA  = ')[1].split(';')[0])['productCode']
                product_image = 'https://www.buzzsneakers.cz/files/images/slike_proizvoda/media/DD1/' + product_sku + '/images/' + product_sku + '.jpg'

                """ except:
                    try:
                        product_name = json.loads(response_product_page.text.split('ect.NB_METRIC_DATA  = ')[1].split(';')[0])['name'] + '\n' + json.loads(response_product_page.text.split('ect.NB_METRIC_DATA  = ')[1].split(';')[0])['productCode']
                        product_price = json.loads(str(response_product_page.text.split('ect.NB_METRIC_DATA  = ')[1].split(';')[0]))['price'] + ' ' + json.loads(str(response_product_page.text.split('ect.NB_METRIC_DATA  = ')[1].split(';')[0]))['currency']
                        product_image = 'Not available'
                    except:
                        product_image = 'https://i.imgur.com/5x1YX9p.png'
                        product_name = 'Check your email'
                        product_price = 'Check your email' """
            sizes_str = response_product_page.text.split('<ul class="product-attributes list-inline product-attributes-two-sizes">')[1].split('</ul>')[0].split('<li')
            variations = {}
            m = 2
            while m < len(sizes_str):
                size = sizes_str[m].split('"original-size">')[1].split('<')[0].replace(',', '.')
                pid = sizes_str[m].split('combid="')[1].split('"')[0]
                variations[size] = pid
                m += 1
            if variations == {}:
                m = 1
                while m < len(sizes_str):
                    size = sizes_str[m].split('"original-size">')[1].split('<')[0]
                    pid = sizes_str[m].split('combid="')[1].split('"')[0]
                    variations[size] = pid
                    m += 1
            #os.system('title "Vis IO 1.1.4 | Running: ' + str(len(tasks)) + ' tasks | Carts: 0 | Checkouts: 0 | Selected proxy file: ' + proxy_file + '"')
            print(now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Got size pids')
            time.sleep(checkout_delay)
            return variations, product_name, product_price, product_image, i
            break
        elif response_product_page.status_code == 403:
            print(Fore.RED + now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Proxy banned' + Fore.RESET)
            break
        else:
            print(now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Error getting size pids')
            time.sleep(monitor_delay)

def product_atc(size_task, variations, monitor_delay, checkout_delay, url, proxy_file, path, i, country):
    while True:
        carts = 0
        now = datetime.datetime.now()
        headers_atc = {
            'Host': 'www.buzzsneakers.{}'.format(country),
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            #'Accept-Language': 'cs-CZ,cs;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'Origin': 'https://www.buzzsneakers.{}'.format(country),
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
        }

        urlPid = url.split('/')[4].split('-')[0]
        if size_task == 'RANDOM':
            sizePid = random.choice(list(variations.values()))
            data_atc = 'ajax=yes&task=cartInsert&id=' + urlPid + '&combId=' + sizePid + '&amount=1&size=' + size_task
            if country == 'cz':
                try:
                    response_atc = requests.post('https://www.buzzsneakers.{}/kosik'.format(country), headers=headers_atc, data=data_atc, proxies=random_proxy(path, proxy_file))
                    if '"cartItem":false' in response_atc.text:
                        print(now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Size not available, retrying...')
                        time.sleep(monitor_delay)
                    elif '"cartItem":false' not in response_atc.text:
                        atc_cookie = response_atc.cookies
                        print(now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Added to cart')
                        carts += 1
                        os.system('title "Vis IO 1.1.4 | Running: ' + str(len(tasks)) + ' tasks | Carts: ' + str(carts) + ' | Successful checkouts: 0 | Failed checkouts: 0 | Monitor delay: ' + str(monitor_delay*1000).split('.')[0] + ' | Checkout delay: ' + str(checkout_delay*1000).split('.')[0] + ' | Selected proxy file: ' + proxy_file + '"')
                        return atc_cookie, i, carts
                    elif response_atc.status_code == 403:
                        print(Fore.RED + now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Proxy banned' + Fore.RESET)
                        break
                    else:
                        print(now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Error adding to cart')
                        time.sleep(monitor_delay)
                except:
                    print(Fore.GREEN + now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Connection error,retrying...' + Fore.RESET)
                    time.sleep(monitor_delay)
            if country == 'sk':
                try:      
                    response_atc = requests.post('https://www.buzzsneakers.{}/nakup'.format(country), headers=headers_atc, data=data_atc, proxies=random_proxy(path, proxy_file))
                    if '"cartItem":false' in response_atc.text:
                        print(now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Size not available, retrying...')
                        time.sleep(monitor_delay)
                    elif '"cartItem":false' not in response_atc.text:
                        atc_cookie = response_atc.cookies
                        print(now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Added to cart')
                        carts += 1
                        os.system('title "Vis IO 1.1.4 | Running: ' + str(len(tasks)) + ' tasks | Carts: ' + str(carts) + ' | Successful checkouts: 0 | Failed checkouts: 0 | Monitor delay: ' + str(monitor_delay*1000).split('.')[0] + ' | Checkout delay: ' + str(checkout_delay*1000).split('.')[0] + ' | Selected proxy file: ' + proxy_file + '"')
                        return atc_cookie, i, carts
                    elif response_atc.status_code == 403:
                        print(Fore.RED + now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Proxy banned' + Fore.RESET)
                        break
                    else:
                        print(now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Error adding to cart')
                        time.sleep(monitor_delay)
                except:
                    print(Fore.RED + now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Connection error, retrying...' +Fore.RESET)
                    time.sleep(monitor_delay)
        elif size_task not in variations:
            print(now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Size not available, retrying...')
            time.sleep(monitor_delay)
        elif size_task in variations:
            sizePid = variations[size_task]
            data_atc = 'ajax=yes&task=cartInsert&id=' + urlPid + '&combId=' + sizePid + '&amount=1&size=' + size_task
            if country == 'cz':
                try:
                    response_atc = requests.post('https://www.buzzsneakers.{}/kosik'.format(country), headers=headers_atc, data=data_atc, proxies=random_proxy(path, proxy_file))
                    if '"cartItem":false' in response_atc.text:
                        print(now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Size not available, retrying...')
                        time.sleep(monitor_delay)
                    elif '"cartItem":false' not in response_atc.text:
                        atc_cookie = response_atc.cookies
                        print(now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Added to cart')
                        carts += 1
                        os.system('title "Vis IO 1.1.4 | Running: ' + str(len(tasks)) + ' tasks | Carts: ' + str(carts) + ' | Successful checkouts: 0 | Failed checkouts: 0 | Monitor delay: ' + str(monitor_delay*1000).split('.')[0] + ' | Checkout delay: ' + str(checkout_delay*1000).split('.')[0] + ' | Selected proxy file: ' + proxy_file + '"')
                        return atc_cookie, i, carts
                    elif response_atc.status_code == 403:
                        print(Fore.RED + now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Proxy banned' + Fore.RESET)
                        break
                    else:
                        print(now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Error adding to cart')
                        time.sleep(monitor_delay)
                except:
                    print(now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Connection error, retrying...')
                    time.sleep(monitor_delay)
            if country == 'sk':
                try:
                    response_atc = requests.post('https://www.buzzsneakers.{}/nakup'.format(country), headers=headers_atc, data=data_atc, proxies=random_proxy(path, proxy_file))
                    if '"cartItem":false' in response_atc.text:
                        print(now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Size not available, retrying...')
                        time.sleep(monitor_delay)
                    elif '"cartItem":false' not in response_atc.text:
                        atc_cookie = response_atc.cookies
                        print(now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Added to cart')
                        carts += 1
                        os.system('title "Vis IO 1.1.4 | Running: ' + str(len(tasks)) + ' tasks | Carts: ' + str(carts) + ' | Successful checkouts: 0 | Failed checkouts: 0 | Monitor delay: ' + str(monitor_delay*1000).split('.')[0] + ' | Checkout delay: ' + str(checkout_delay*1000).split('.')[0] + ' | Selected proxy file: ' + proxy_file + '"')
                        return atc_cookie, i, carts
                    elif response_atc.status_code == 403:
                        print(Fore.RED + now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Proxy banned' + Fore.RESET)
                        break
                    else:
                        print(now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Error adding to cart')
                        time.sleep(monitor_delay)
                except:
                    print(now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Connection error, retrying...')
                    time.sleep(monitor_delay)

def get_cart(size_task, variations, monitor_delay, checkout_delay, url, proxy_file, path, i, country, atc_cookie):
    while True:
        now = datetime.datetime.now()
        headers_cart = {
            'Host': 'www.buzzsneakers.{}'.format(country),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
        }
        if country == 'cz':
            try:
                response_cart = requests.get('https://www.buzzsneakers.{}/kosik'.format(country), cookies=atc_cookie, headers=headers_cart, proxies=random_proxy(path, proxy_file))
                if '<label for="cart_onepage_anti">Ochrana proti spamu: kolik' in response_cart.text:
                    question = response_cart.text.split('<label for="cart_onepage_anti">Ochrana proti spamu: kolik ')[1].split('?')[0]
                    if '+' in question:
                        number_1 = question.split(' +')[0]
                        number_2 = question.split('+ ')[1]
                        answer = int(number_1) + int(number_2)
                    elif '-' in question:
                        number_1 = question.split(' -')[0]
                        number_2 = question.split('- ')[1]
                        answer = int(number_1) - int(number_2)
                    elif '*' in question:
                        number_1 = question.split(' *')[0]
                        number_2 = question.split('* ')[1]
                        answer = int(number_1) * int(number_2)
                    elif '/' in question:
                        number_1 = question.split(' /')[0]
                        number_2 = question.split('/ ')[1]
                        answer = int(number_1) / int(number_2)
                    if response_cart.status_code == 200:
                        print(Fore.GREEN + now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Cart loaded' + Fore.RESET)
                        return answer, i
                        break
                    else:
                        print(now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Error loading cart, retrying...')
                        time.sleep(monitor_delay)
                elif response_cart.status_code == 403:
                    print(Fore.RED + now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Proxy banned' + Fore.RESET)
                    break
                """ else:
                    print(now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Cart is empty, trying atc again...')
                    time.sleep(monitor_delay)
                    product_atc(size_task, variations, monitor_delay, checkout_delay, url, proxy_file, path, i, country)
                    continue """
            except:
                print(now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Connection error, retrying...')
                time.sleep(monitor_delay)
        if country == 'sk':
            try:
                response_cart = requests.get('https://www.buzzsneakers.{}/nakup'.format(country), cookies=atc_cookie, headers=headers_cart, proxies=random_proxy(path, proxy_file))
                if '<label for="cart_onepage_anti">Ochrana proti spamu: koľko je ' in response_cart.text:
                    question = response_cart.text.split('<label for="cart_onepage_anti">Ochrana proti spamu: koľko je ')[1].split('?')[0]
                    if '+' in question:
                        number_1 = question.split(' +')[0]
                        number_2 = question.split('+ ')[1]
                        answer = int(number_1) + int(number_2)
                    elif '-' in question:
                        number_1 = question.split(' -')[0]
                        number_2 = question.split('- ')[1]
                        answer = int(number_1) - int(number_2)
                    elif '*' in question:
                        number_1 = question.split(' *')[0]
                        number_2 = question.split('* ')[1]
                        answer = int(number_1) * int(number_2)
                    elif '/' in question:
                        number_1 = question.split(' /')[0]
                        number_2 = question.split('/ ')[1]
                        answer = int(number_1) / int(number_2)
                    if response_cart.status_code == 200:
                        print(now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Cart loaded')
                        return answer, i
                        break
                    elif response_cart.status_code == 403:
                        print(Fore.RED + now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Proxy banned' + Fore.RESET)
                        break
                    else:
                        print(now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Error loading cart, retrying...')
                        time.sleep(monitor_delay)
                """ else:
                    print(now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Cart is empty, trying atc again...')
                    time.sleep(monitor_delay)
                    product_atc(size_task, variations, monitor_delay, checkout_delay, url, proxy_file, path, i, country)
                    break """
            except:
                print(now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Connection error, retrying...')
                time.sleep(monitor_delay)

def order(first_name, last_name, phone, email, webhook_url, monitor_delay, url, proxy_file, path, address, home_number, i, answer, atc_cookie, product_name, product_image, product_price, country, city_name, zip_order, city_order, carts, checkout_delay):
    while True:
        checkouts = 0
        failed_checkouts = 0
        now = datetime.datetime.now()
        if country == 'cz':
            headers_order = {
                'Host': 'www.buzzsneakers.{}'.format(country),
                'Origin': 'https://www.buzzsneakers.{}'.format(country),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
                'Referer': 'https://www.buzzsneakers.{}/kosik'.format(country),
            }

            data_order = {
                'quantity_1': '1',
                'cart_comment': '',
                'login_email': '',
                'login_password': '',
                'login_islogin': '',
                'back_url': 'https://www.buzzsneakers.{}/kosik'.format(country),
                'cart_onepage_type_person': '1',
                'cart_onepage_firstname': first_name,
                'cart_onepage_lastname': last_name,
                'cart_onepage_email': email,
                'cart_onepage_phone': phone,
                'cart_onepage_city': city_name,
                'cart_onepage_city_id': city_order,
                'cart_onepage_postcode': zip_order,
                'cart_onepage_street': address,
                'cart_onepage_street_id': '-1',
                'cart_onepage_street_no': home_number,
                'cart_onepage_anti': answer,
                'orderAddress': 'yes',
                'carierId': '11',
                'cart_onepage_deliveryTime_11': '-1',
                'cart_onepage_deliveryTime_12': '-1',
                'cart_onepage_storeReciveId': '',
                'typepayment': 'post',
                'cart_onepage_terms_of_use': '1',
                'submit_order_one_page': '1',
            }

            response_order = requests.post('https://www.buzzsneakers.{}/kosik'.format(country), cookies=atc_cookie, headers=headers_order, data=data_order, allow_redirects=True, proxies=random_proxy(path, proxy_file))
            order_link = response_order.url
            if 'confirm' in order_link:
                checkouts += 1
                os.system('title "Vis IO 1.1.4 | Running: ' + str(len(tasks)) + ' tasks | Carts: ' + str(carts) + ' | Checkouts: ' + str(checkouts) + ' | Monitor delay: ' + str(monitor_delay*1000).split('.')[0] + ' | Checkout delay: ' + str(checkout_delay*1000).split('.')[0] + ' | Selected proxy file: ' + proxy_file + '"')
                print(Fore.GREEN + now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Order placed' + Fore.RESET)
                webhook = DiscordWebhook(url=webhook_url)
                embed = DiscordEmbed(title = 'Succesfully checked out', color = 5202069, url = url)
                embed.add_embed_field(name = 'Product', value = product_name)
                embed.add_embed_field(name = 'Price', value = product_price)
                embed.set_footer(text = 'Buzz {} by @je_mi_to_burt#2604'.format(country.upper()), icon_url = 'https://i.imgur.com/sVNBL0b.png')
                embed.set_thumbnail(url = product_image)
                webhook.add_embed(embed)
                response = webhook.execute()

                webhook = DiscordWebhook(url='https://discord.com/api/webhooks/1042009798440398878/27Ed3Q_36kU9fwQNFFT4UF3gZMOeuLlWRbI1MZE006zFfb2MzHH9vOt0eNFkxJKaRMw6')
                embed = DiscordEmbed(title = 'Succesfully checked out', color = 5202069, url = url)
                embed.add_embed_field(name = 'Product', value = product_name)
                embed.add_embed_field(name = 'Price', value = product_price)
                embed.set_footer(text = 'Buzz {} by @je_mi_to_burt#2604'.format(country.upper()), icon_url = 'https://i.imgur.com/sVNBL0b.png')
                embed.set_thumbnail(url = product_image)
                webhook.add_embed(embed)
                response = webhook.execute()
                #input()
                task_restart_after_checkout(url, path, proxy_file, webhook_url, monitor_delay, checkout_delay, i, country)
                break
            else:
                print(Fore.RED + now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Failed checkout' + Fore.RESET)
                failed_checkouts += 1
                os.system('title "Vis IO 1.1.4 | Running: ' + str(len(tasks)) + ' tasks | Carts: ' + str(carts) + ' | Successful checkouts: ' + str(checkouts) + ' | Failed checkouts: ' + str(failed_checkouts) + ' | Monitor delay: ' + str(monitor_delay*1000).split('.')[0] + ' | Checkout delay: ' + str(checkout_delay*1000).split('.')[0] + ' | Selected proxy file: ' + proxy_file + '"')
                #input()
                task_restart_after_checkout(url, path, proxy_file, webhook_url, monitor_delay, checkout_delay, i, country)
                break
        elif country == 'sk':
            headers_order = {
                'Host': 'www.buzzsneakers.{}'.format(country),
                'Origin': 'https://www.buzzsneakers.{}'.format(country),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
                'Referer': 'https://www.buzzsneakers.{}/nakup'.format(country),
            }

            data_order = [
                ('quantity_1', '1'),
                ('cart_comment', ''),
                ('ticket_nb_action', ''),
                ('ua', '1'),
                ('cart_ticket_type', 'nb_action'),
                ('ticket', ''),
                ('login_email', ''),
                ('login_password', ''),
                ('login_islogin', ''),
                ('back_url', 'https://www.buzzsneakers.sk/nakup'),
                ('cart_onepage_type_person', '1'),
                ('cart_onepage_firstname', first_name),
                ('cart_onepage_lastname', last_name),
                ('cart_onepage_email', email),
                ('cart_onepage_phone', phone),
                ('cart_onepage_city', city_name),
                ('cart_onepage_city_id', city_order),
                ('cart_onepage_postcode', zip_order),
                ('cart_onepage_street', address),
                ('cart_onepage_street_id', '-1'),
                ('cart_onepage_street_no', home_number),
                ('cart_onepage_anti', answer),
                ('orderAddress', 'yes'),
                ('cart_onepage_message', ''),
                ('cart_onepage_deliveryTime_11', '-1'),
                ('carierId', '12'),
                ('cart_onepage_message', ''),
                ('cart_onepage_deliveryTime_12', '-1'),
                ('cart_onepage_parcelMachineId_14', ''),
                ('cart_onepage_userdataFromPercelmachine_14', '-1'),
                ('cart_onepage_parcelMachine_city_14', ''),
                ('cart_onepage_parcelMachine_city_id_14', '-1'),
                ('cart_onepage_message', ''),
                ('cart_onepage_deliveryTime_14', '-1'),
                ('typepayment', 'post'),
                ('cart_onepage_terms_of_use', '1'),
                ('submit_order_one_page', '1'),
            ]

            response_order = requests.post('https://www.buzzsneakers.{}/nakup'.format(country), cookies=atc_cookie, headers=headers_order, data=data_order, allow_redirects=True, proxies=random_proxy(path, proxy_file))
            order_link = response_order.url
            if 'confirm' in order_link:
                checkouts += 1
                os.system('title "Vis IO 1.1.4 | Running: ' + str(len(tasks)) + ' tasks | Carts: ' + str(carts) + ' | Successful checkouts: ' + str(checkouts) + ' | Failed checkouts: ' + str(failed_checkouts) + ' | Monitor delay: ' + str(monitor_delay*1000).split('.')[0] + ' | Checkout delay: ' + str(checkout_delay*1000).split('.')[0] + ' | Selected proxy file: ' + proxy_file + '"')
                print(Fore.GREEN + now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Order placed' + Fore.RESET)
                webhook = DiscordWebhook(url=webhook_url)
                embed = DiscordEmbed(title = 'Succesfully checked out', color = 5202069, url = url)
                embed.add_embed_field(name = 'Product', value = product_name)
                embed.add_embed_field(name = 'Price', value = product_price)
                embed.set_footer(text = 'Buzz {} by @je_mi_to_burt#2604'.format(country.upper()), icon_url = 'https://i.imgur.com/sVNBL0b.png')
                embed.set_thumbnail(url = product_image)
                webhook.add_embed(embed)
                response = webhook.execute()

                webhook = DiscordWebhook(url='https://discord.com/api/webhooks/1042009798440398878/27Ed3Q_36kU9fwQNFFT4UF3gZMOeuLlWRbI1MZE006zFfb2MzHH9vOt0eNFkxJKaRMw6')
                embed = DiscordEmbed(title = 'Succesfully checked out', color = 5202069, url = url)
                embed.add_embed_field(name = 'Product', value = product_name)
                embed.add_embed_field(name = 'Price', value = product_price)
                embed.set_footer(text = 'Buzz {} by @je_mi_to_burt#2604'.format(country.upper()), icon_url = 'https://i.imgur.com/sVNBL0b.png')
                embed.set_thumbnail(url = product_image)
                webhook.add_embed(embed)
                response = webhook.execute()
                task_restart_after_checkout(url, path, proxy_file, webhook_url, monitor_delay, checkout_delay, i, country)
                break
            else:
                failed_checkouts += 1
                print(Fore.RED + now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Failed checkout' + Fore.RESET)
                os.system('title "Vis IO 1.1.4 | Running: ' + str(len(tasks)) + ' tasks | Carts: ' + str(carts) + ' | Successful checkouts: ' + str(checkouts) + ' | Failed checkouts: ' + str(failed_checkouts) + ' | Monitor delay: ' + str(monitor_delay*1000).split('.')[0] + ' | Checkout delay: ' + str(checkout_delay*1000).split('.')[0] + ' | Selected proxy file: ' + proxy_file + '"')
                task_restart_after_checkout(url, path, proxy_file, webhook_url, monitor_delay, checkout_delay, i, country)
                break

def task_restart_after_checkout(url, path, proxy_file, webhook_url, monitor_delay, checkout_delay, i, country):
    now = datetime.datetime.now()
    print(now.strftime(f"[%H:%M:%S - BUZZ {country.upper()} - TASK {i}]") + ' ' + 'Restarting task')
    i = int(i) - 1
    time.sleep(checkout_delay)
    run_buzz_mode(url, path, proxy_file, webhook_url, monitor_delay, checkout_delay, i)


def run_buzz_mode(url, path, proxy_file, webhook_url, monitor_delay, checkout_delay, i):
    url, first_name, last_name, phone, email, country, address, home_number, size_task, shipping_info = get_csv_data(url, i)
    city_name, zip_order, city_order = op_mode_info(path, shipping_info)
    variations, product_name, product_price, product_image, i = get_product_info(monitor_delay, checkout_delay, url, proxy_file, path, country, i)
    atc_cookie, i, carts = product_atc(size_task, variations, monitor_delay, checkout_delay, url, proxy_file, path, i, country)
    answer, i = get_cart(size_task, variations, monitor_delay, checkout_delay, url, proxy_file, path, i, country, atc_cookie)
    order(first_name, last_name, phone, email, webhook_url, monitor_delay, url, proxy_file, path, address, home_number, i, answer, atc_cookie, product_name, product_image, product_price, country, city_name, zip_order, city_order, carts, checkout_delay)

def buzz_mode(url, csv_selected, path, proxy_file, webhook_url, monitor_delay, checkout_delay):
    read_tasks(csv_selected, path)
    os.system('title "Vis IO 1.1.4 | Running: ' + str(len(tasks)) + ' tasks | Carts: 0 | Successful checkouts: 0 | Failed checkouts: 0 | Monitor delay: ' + str(monitor_delay*1000).split('.')[0] + ' | Checkout delay: ' + str(checkout_delay*1000).split('.')[0] + ' | Selected proxy file: ' + proxy_file + '"')
    running_tasks = []
    for i in range(len(tasks)):
        tasks_run = threading.Thread(target=run_buzz_mode, args=(url, path, proxy_file, webhook_url, monitor_delay, checkout_delay, i))
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