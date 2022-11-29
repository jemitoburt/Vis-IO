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

stores_cz = {
    "Alza P3 - Flora":"970",
    "Alza P4 - Haje":"739",
    "Alza Showroom Praha 7 - Holesovice":"595",
    "Alza P4 - Pankrac":"715",
    "Alza P1 -  Mustek":"1004",
    "Alza P5 - Andel":"610",
    "Alza P9 - Horni Pocernice":"612",
    "Alza P9 - H. Pocernice (AlzaDrive)":"704",
    "Alza P6 - Dejvice":"925",
    "Alza Zdiby":"1013",
    "Alza P5 - Luziny":"599",
    "Alza P5 - Zlicin - Chrastany":"2924",
    "Alza P5 - Zlicin - Chrastany (AlzaDrive)":"2928",
    "Alza Uzice (Areal ProLogis Park)":"893",
    "Alza Kladno":"630",
    "Alza Melnik":"693",
    "Alza Benesov":"1853",
    "Alza Mlada Boleslav":"702",
    "Alza Kolin":"677",
    "Alza Pribram":"631",
    "Alza Usti nad Labem":"607",
    "Alza Tabor":"692",
    "Alza Most":"689",
    "Alza Decin":"732",
    "Alza Liberec":"609",
    "Alza Plzen":"738",
    "Alza Pardubice":"613",
    "Alza Chomutov":"723",
    "Alza Hradec Kralove":"601",
    "Alza Jihlava":"604",
    "Alza Karlovy Vary":"606",
    "Alza Ceske Budejovice":"611",
    "Alza Brno - Bystrc":"710",
    "Alza Brno - Liskovec":"711",
    "Alza Brno - stred":"598",
    "Alza Prostejov":"735",
    "Alza Olomouc":"608",
    "Alza Opava":"724",
    "Alza Zlin":"605",
    "Alza Ostrava":"603",
    "Alza Frydek-Mistek":"722"
}

stores_sk = {
    "Alza Bratislava - centrala":"684",
    "Alza Trencin":"625",
    "Alza Bratislava - Petrzalka":"721",
    "Alza Senec (GLP)":"921",
    "Alza Senec (GLP) - AlzaDrive":"1750",
    "Alza Trnava":"686",
    "Alza Zilina":"687",
    "Alza Nitra":"624",
    "Alza Prievidza":"706",
    "Alza Banska Bystrica":"703",
    "Alza Poprad":"740",
    "Alza Presov":"691",
    "Alza Kosice":"685"
}

stores_sk_address ={
    "Alza Bratislava - centrala":"Mlynské Nivy 19034/5a",
    "Alza Trencin":"Gen. M. R. Štefánika 426",
    "Alza Bratislava - Petrzalka":"Pajštúnska 3",
    "Alza Senec (GLP)":"Diaľničná cesta 5856",
    "Alza Senec (GLP) - AlzaDrive":"Diaľničná cesta 5856",
    "Alza Trnava":"Starohájska 9/A",
    "Alza Zilina":"Komenského 8933/63B",
    "Alza Nitra":"Akademická 1651/1A",
    "Alza Prievidza":"Bojnická cesta 20",
    "Alza Banska Bystrica":"Cesta na štadión 7",
    "Alza Poprad":"Jiřího Wolkera 4212/15",
    "Alza Presov":"Arm. gen. Svobodu 13832/21",
    "Alza Kosice":"Žriedlová 11"
}

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
        product_url = task['url']
    if '-d' in product_url:
        pid = product_url.split('-d')[1].split('.')[0]
    elif 'dq=' in product_url:
        pid = product_url.split('dq=')[1].split('.')[0]
    dummy_url = task['dummyUrl']
    if '-d' in dummy_url:
        dummy_pid = dummy_url.split('-d')[1].split('.')[0]
    elif 'dq=' in dummy_url:
        dummy_pid = dummy_url.split('dq=')[1].split('.')[0]
    first_name = task['firstName']
    last_name = task['lastName']
    zip_code = task['zip']
    city_checkout_sk = task['city'].split('Alza ')[1].split(' - ')[0]
    phone = task['phone']
    email = task['email']
    city = task['city']
    mode = task['mode']
    country = task['country'].lower()
    if country == 'cz':
        city = stores_cz[city]
        street_2 = None
    elif country == 'sk':
        city = stores_sk[city]
        street_1 = task['city']
        street_2 = stores_sk_address[street_1]
    return product_url, pid, dummy_url, dummy_pid, first_name, last_name, zip_code, city_checkout_sk, phone, email, city, street_2, i, country, mode

def get_home_page(twocaptcha, country, i, path, proxy_file, monitor_delay, checkout_delay):
    while True:
        i += 1
        now = datetime.datetime.now()
        headers_home_page = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Host': 'www.alza.{}'.format(country),
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'Referer': 'https://www.alza.{}/'.format(country),
            'Connection': 'keep-alive',
        }
        try:
            response_home_page = requests.get('https://www.alza.{}'.format(country), headers=headers_home_page, proxies=random_proxy(path, proxy_file), allow_redirects=True)
            if response_home_page.status_code == 200:
                if 'captcha' not in response_home_page.url:
                    print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "No captcha on homepage")
                    time.sleep(checkout_delay)
                    return i

                elif 'captcha' in response_home_page.url:
                    print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Captcha on homepage")
                    captcha_token = response_home_page.text.split('data-sitekey=')[1].split(' data-callback')[0]
                    url_captcha = requests.get('http://2captcha.com/in.php?key=' + twocaptcha + '&method=userrecaptcha&googlekey=' + captcha_token + '&pageurl=' + response_home_page.url).text.split('|')[1]
                    captcha_solved = requests.get('http://2captcha.com/res.php?key=' + twocaptcha + '&action=get&id=' + url_captcha).text
                    
                    while 'CAPCHA_NOT_READY' in captcha_solved:
                        now = datetime.datetime.now()
                        time.sleep(monitor_delay)
                        captcha_solved = requests.get('http://2captcha.com/res.php?key=' + twocaptcha + '&action=get&id=' + url_captcha).text
                        if 'OK' in captcha_solved:
                            print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Captcha solved")
                            captcha_solved_token = captcha_solved.split('|')[1]
                            break
                        else:
                            print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Waiting for captcha")
                    
                    headers_captcha = {
                        'Host': 'www.alza.{}'.format(country),
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
                        'referer': response_home_page.url,
                    }

                    response_solved = requests.get('https://www.alza.{country}/captcha/verify?solution={captcha_solved_token}&ssa={url_page}'.format(country=country, captcha_solved_token=captcha_solved_token, url_page='https://www.alza.{}'.format(country)), headers=headers_captcha, proxies=random_proxy(path, proxy_file), allow_redirects=True)
                    if response_solved.status_code == 200:
                        print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Got home page")
                        time.sleep(checkout_delay)
                        return i
        except:
            print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Connection error,retrying...")
            time.sleep(checkout_delay)

def get_product_info(country, path, proxy_file, product_url, checkout_delay, monitor_delay, i):
    while True:
        now = datetime.datetime.now()
        headers_product_info = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Host': 'www.alza.{}'.format(country),
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'Referer': 'https://www.alza.{}/'.format(country),
            'Connection': 'keep-alive',
        }
        try:
            response_product_info = requests.get(product_url, headers=headers_product_info, proxies=random_proxy(path, proxy_file), allow_redirects=False)
            if response_product_info.status_code == 200:
                if 'InStock' in response_product_info.text:
                    print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Got product info")
                    response_product_info.encoding = response_product_info.apparent_encoding
                    response_product_info_encode = response_product_info.text
                    if "window.dataLayer.push(" not in response_product_info_encode:
                        product_info_str = json.loads(response_product_info_encode.split('"application/ld+json">')[2].split('</script>')[0])
                        product_name = product_info_str['name']
                        product_price = product_info_str['offers']['price'] + product_info_str['offers']['priceCurrency']
                        product_image = product_info_str['image']
                        time.sleep(checkout_delay)
                        return i, product_name, product_price, product_image
                    elif "window.dataLayer.push(" in response_product_info_encode:
                        product_info_str = json.loads(response_product_info_encode.split('window.dataLayer.push(')[1].split(', {"crto":{"email":""')[0])
                        product_name = product_info_str['itemName']
                        product_price = 'NA'
                        product_image = 'https://cdn.alza.sk/ImgW.ashx?fd=f3&cd=' + product_info_str['itemID']
                        time.sleep(checkout_delay)
                        return i, product_name, product_price, product_image
                else:
                    print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Product out of stock")
                    time.sleep(monitor_delay)
            elif response_product_info.status_code == 302:
                print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Product page is not live, retrying...")
                time.sleep(monitor_delay)
            else:
                print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Failed getting product page, retrying...")
                time.sleep(monitor_delay)
        except:
            print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Connection error,retrying...")
            time.sleep(checkout_delay)

def product_atc(i, country, product_url, pid, path, proxy_file, checkout_delay, monitor_delay):
    while True:
        carts = 0
        now = datetime.datetime.now()
        headers_atc = {
            'Host': 'www.alza.{}'.format(country),
            'content-type': 'application/json; charset=utf-8',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'x-requested-with': 'XMLHttpRequest',
            'cache-control': 'no-cache',
            #'accept-language': 'cs-CZ',
            'origin': 'https://www.alza.{}'.format(country),
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'referer': product_url,
        }

        json_data = {
            'id': pid,
            'count': 1,
            'warranty': None,
            'insurance': None,
            'replacement': None,
            'hooks': None,
            'src': 0,
            'url': product_url,
            'additionalitems': [],
            'isGiftOrder': False,
            'tretinka': False,
            'discountCode': None,
            'isBuyOnInstallments': False,
            'pageType': 0,
            'pageId': pid,
            'referrerPageType': 2,
            'referrerPageId': None,
        }

        try:
            response_atc = requests.post('https://www.alza.{}/Services/EShopService.svc/OrderCommodity'.format(country), headers=headers_atc, json=json_data, proxies=random_proxy(path, proxy_file))
            if 'nil' in response_atc.text:
                print(Fore.RED + now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Change proxies, stopping task..." + Fore.RESET)
                break
            elif 'nil' not in response_atc.text:
                if response_atc.status_code == 200:
                    cookies_idox = response_atc.cookies['IDOX']
                    cookies_cart = str(json.loads(response_atc.text)['d']['Id'])
                    cart_price = json.loads(response_atc.text)['d']['Basket']
                    print(Fore.GREEN + now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Added to cart" + Fore.RESET)
                    carts += 1
                    os.system('title "Vis IO 1.4 | Running: ' + str(len(tasks)) + ' tasks | Carts: ' + str(carts) + ' | Successful checkouts: 0 | Failed checkouts: 0 | Monitor delay: ' + str(monitor_delay*1000).split('.')[0] + ' | Checkout delay: ' + str(checkout_delay*1000).split('.')[0] + ' | Selected proxy file: ' + proxy_file + '"')
                    time.sleep(checkout_delay)
                    return i, cookies_idox, cookies_cart, cart_price, carts
                else:
                    print(Fore.RED + now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Failed to add to cart, retrying..." + Fore.RESET)
                    time.sleep(monitor_delay)
        except:
            print(Fore.RED + now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Connection error,retrying..." + Fore.RESET)
            time.sleep(checkout_delay)

def dummy_atc(i, country, dummy_url, dummy_pid, path, proxy_file, checkout_delay, monitor_delay):
    while True:
        now = datetime.datetime.now()
        headers_atc = {
            'Host': 'www.alza.{}'.format(country),
            'content-type': 'application/json; charset=utf-8',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'x-requested-with': 'XMLHttpRequest',
            'cache-control': 'no-cache',
            #'accept-language': 'cs-CZ',
            'origin': 'https://www.alza.{}'.format(country),
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'referer': dummy_url,
        }

        json_data = {
            'id': dummy_pid,
            'count': 1,
            'warranty': None,
            'insurance': None,
            'replacement': None,
            'hooks': None,
            'src': 0,
            'url': dummy_url,
            'additionalitems': [],
            'isGiftOrder': False,
            'tretinka': False,
            'discountCode': None,
            'isBuyOnInstallments': False,
            'pageType': 0,
            'pageId': dummy_pid,
            'referrerPageType': 2,
            'referrerPageId': None,
        }
        try:
            response_atc = requests.post('https://www.alza.{}/Services/EShopService.svc/OrderCommodity'.format(country), headers=headers_atc, json=json_data, proxies=random_proxy(path, proxy_file))
            if 'nil' in response_atc.text:
                print(Fore.RED + now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Change proxies, stopping task..." + Fore.RESET)
                break
            elif 'nil' not in response_atc.text:
                if response_atc.status_code == 200:
                    cookies_idox = response_atc.cookies['IDOX']
                    cookies_cart = str(json.loads(response_atc.text)['d']['Id'])
                    cart_price = json.loads(response_atc.text)['d']['Basket']
                    print(Fore.GREEN + now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Dummy added to cart" + Fore.RESET)
                    time.sleep(checkout_delay)
                    return i, cookies_idox, cookies_cart, cart_price
                else:
                    print(Fore.RED + now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Failed to add dummy to cart, retrying..." + Fore.RESET)
                    time.sleep(monitor_delay)
        except:
            print(Fore.RED + now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Connection error,retrying..." + Fore.RESET)
            time.sleep(checkout_delay)

def main_atc(i, country, pid, product_url, cookies_idox, path, proxy_file, monitor_delay, checkout_delay):
    while True:
        carts = 0
        now = datetime.datetime.now()
        try:
            check_if_page_is_up = requests.get(product_url)
            if check_if_page_is_up.url != 'https://www.alza.sk/gaming/herne-konzoly-playstation-5/18876712.htm' or check_if_page_is_up.url != 'https://www.alza.cz/gaming/herni-konzole-playstation-5/18876712.htm':
                cookies_product_atc_dummy = {
                    'IDOX': cookies_idox,
                }

                headers_atc_dummy_2 = {
                    'Host': 'www.alza.{}'.format(country),
                    'content-type': 'application/json; charset=utf-8',
                    'accept': 'application/json, text/javascript, */*; q=0.01',
                    'x-requested-with': 'XMLHttpRequest',
                    'cache-control': 'no-cache',
                    'origin': 'https://www.alza.{}'.format(country),
                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
                    'referer': product_url,
                }

                json_data_dummy_2 = {
                    'id': pid,
                    'count': 1,
                    'warranty': None,
                    'insurance': None,
                    'replacement': None,
                    'hooks': None,
                    'src': 0,
                    'url': product_url,
                    'additionalitems': [],
                    'isGiftOrder': False,
                    'tretinka': False,
                    'discountCode': None,
                    'isBuyOnInstallments': False,
                    'pageType': 0,
                    'pageId': pid,
                    'referrerPageType': 2,
                    'referrerPageId': None,
                }
                try:
                    response_atc_dummy_2 = requests.post('https://www.alza.{}/Services/EShopService.svc/OrderCommodity'.format(country), headers=headers_atc_dummy_2, json=json_data_dummy_2, cookies=cookies_product_atc_dummy, proxies=random_proxy(path, proxy_file))
                    if response_atc_dummy_2.status_code == 500 or response_atc_dummy_2.status_code == 430:
                        print(Fore.RED + now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Site dead, waiting 10 seconds" + Fore.RESET)
                        time.sleep(10)
                    elif response_atc_dummy_2.status_code !=500:
                        if '"ErrorLevel":1' not in response_atc_dummy_2.text and 'nil' not in response_atc_dummy_2.text:
                            print(Fore.GREEN + now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Main product added to cart, continuing in checking out" + Fore.RESET)
                            carts += 1
                            os.system('title "Vis IO 1.4 | Running: ' + str(len(tasks)) + ' tasks | Carts: ' + str(carts) + ' | Successful checkouts: 0 | Failed checkouts: 0 | Monitor delay: ' + str(monitor_delay*1000).split('.')[0] + ' | Checkout delay: ' + str(checkout_delay*1000).split('.')[0] + ' | Selected proxy file: ' + proxy_file + '"')
                            return i, carts
                        else:
                            print(Fore.RED + now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Main product is oos, retrying..." + Fore.RESET)
                            time.sleep(monitor_delay)
                except:
                    print(Fore.RED + now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Connection error, retrying..." + Fore.RESET)
                    time.sleep(monitor_delay)
            elif check_if_page_is_up.status_code == 302:
                print(Fore.RED + now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Main product page is not loaded, retrying..." + Fore.RESET)
                time.sleep(monitor_delay)
        except:
            print(Fore.RED + now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Connection error, retrying..." + Fore.RESET)
            time.sleep(monitor_delay)

def get_cart(cookies_idox, country, i, path, proxy_file, monitor_delay, checkout_delay):
    while True:
        now = datetime.datetime.now()
        cookies_group_id = {
            'IDOX': cookies_idox,
        }

        headers_group_id = {
            'Host': 'www.alza.{}'.format(country),
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
        }

        try:
            response_group_id = requests.get('https://www.alza.{}/Order2.htm'.format(country), cookies=cookies_group_id, headers=headers_group_id, proxies=random_proxy(path, proxy_file))
            
            if response_group_id.status_code == 200:
                group_id = str(response_group_id.text.split('"groupId":')[1].split(',')[0])
                order_id = str(response_group_id.text.split('"orderId":')[1].split(',')[0])
                print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Got cart")
                time.sleep(checkout_delay)
                return i, group_id, order_id
            else:
                print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Failed to get cart, retrying...")
                time.sleep(monitor_delay)
        except:
            print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Connection error, retrying...")
            time.sleep(monitor_delay)

def checkout_1_8(cookies_idox, country, group_id, city, path, proxy_file, monitor_delay, checkout_delay, i):
    while True:
        now = datetime.datetime.now()
        cookies_shipping_method = {
            'IDOX': cookies_idox,
        }

        headers_shipping_method = {
            'Host': 'www.alza.{}'.format(country),
            'content-type': 'application/json; charset=utf-8',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'x-requested-with': 'XMLHttpRequest',
            'cache-control': 'no-cache',
            #'accept-language': 'cs-CZ',
            'origin': 'https://www.alza.{}'.format(country),
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'referer': 'https://www.alza.{}/Order2.htm'.format(country),
        }

        json_data_shipping_method = {
            'selectedDeliveryForGroup': {
                'groupId': int(group_id),
                'deliveryId': str(city),
                'parcelShopId': 0,
            },
            'selectedDeliveriesForGroups': [],
            'selectedDeliveryAccesoriesIds': [],
            'selectedDeliveryZipId': 0,
            'deliveryAddressId': None,
        }

        try:
            response_shipping_method = requests.post('https://www.alza.{}/Services/EShopService.svc/GetOrder2DeliveryInfo'.format(country), cookies=cookies_shipping_method, headers=headers_shipping_method, json=json_data_shipping_method, proxies=random_proxy(path, proxy_file))
            if response_shipping_method.status_code == 200:
                print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Got shipping method")
                time.sleep(checkout_delay)
                return i
            else:
                print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Failed to get shipping method, retrying...")
                time.sleep(monitor_delay)
        except:
            print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Connection error, retrying...")
            time.sleep(monitor_delay)

def checkout_2_8(cookies_idox, country, city, group_id, path, proxy_file, monitor_delay, checkout_delay, i):
    while True:
        now = datetime.datetime.now()
        cookies_payment = {
            'IDOX': cookies_idox,
        }

        headers_payment = {
            'Host': 'www.alza.{}'.format(country),
            'content-type': 'application/json; charset=utf-8',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'x-requested-with': 'XMLHttpRequest',
            'cache-control': 'no-cache',
            #'accept-language': 'cs-CZ',
            'origin': 'https://www.alza.{}'.format(country),
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'referer': 'https://www.alza.{}/Order2.htm'.format(country),
        }

        if country == 'cz':
            payment_method = '101'
        elif country == 'sk':
            payment_method = '104'

        json_data_payment = {
            'paymentId': int(payment_method),
            'selectedDeliveriesForGroups': [
                {
                    'deliveryId': int(city),
                    'groupId': int(group_id),
                    'deliveryTimeFrameId': None,
                    'deliveryTimeSlotId': None,
                    'carDeliveryVehicleId': None,
                    'parcelShopId': None,
                },
            ],
            'selectedDeliveryAccesoriesIds': [],
            'selectedDeliveryZipId': 0,
            'deliveryAddressId': None,
        }

        try:
            response_payment = requests.post('https://www.alza.{}/Services/EShopService.svc/GetOrder2PaymentInfo'.format(country), cookies=cookies_payment, headers=headers_payment, json=json_data_payment, proxies=random_proxy(path, proxy_file))
            if response_payment.status_code == 200:
                print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Got payment method")
                time.sleep(checkout_delay)
                return i
            else:
                print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Failed to get payment method, retrying...")
                time.sleep(monitor_delay)
        except:
            print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Connection error, retrying...")
            time.sleep(monitor_delay)

def checkout_3_8(cookies_idox, country, city, group_id, path, proxy_file, monitor_delay, checkout_delay, i):
    while True:
        now = datetime.datetime.now()
        cookies_payment_delivery = {
            'IDOX': cookies_idox,
        }

        headers_payment_delivery = {
            'Host': 'www.alza.{}'.format(country),
            'content-type': 'application/json; charset=utf-8',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'x-requested-with': 'XMLHttpRequest',
            'cache-control': 'no-cache',
            #'accept-language': 'cs-CZ',
            'origin': 'https://www.alza.{}'.format(country),
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'referer': 'https://www.alza.{}/Order2.htm'.format(country),
        }

        if country == 'cz':
            payment_method = '101'
        elif country == 'sk':
            payment_method = '104'

        json_data_payment_delivery = {
            'selectedDeliveriesForGroups': [
                {
                    'deliveryId': int(city),
                    'groupId': int(group_id),
                    'deliveryTimeFrameId': None,
                    'deliveryTimeSlotId': None,
                    'carDeliveryVehicleId': None,
                    'parcelShopId': None,
                },
            ],
            'paymentId': int(payment_method),
            'deliveryZipId': 0,
            'paymentCardId': 0,
            'deliveryAccesoriesIds': '',
            'homeBoxInfo': None,
            'deliveryAddressId': None,
        }

        try:
            response_payment_delivery = requests.post('https://www.alza.{}/Services/EShopService.svc/SaveOrder2'.format(country), cookies=cookies_payment_delivery, headers=headers_payment_delivery, json=json_data_payment_delivery, proxies=random_proxy(path, proxy_file))
            if response_payment_delivery.status_code == 200:
                print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Saving order info 1/5")
                time.sleep(checkout_delay)
                return i
            else:
                print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Failed to save order info 1/5, retrying...")
                time.sleep(monitor_delay)
        except:
            print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Connection error, retrying...")
            time.sleep(monitor_delay)

def checkout_4_8(cookies_idox, country, path, proxy_file, monitor_delay, checkout_delay, i):
    while True:
        now = datetime.datetime.now()
        cookies_test = {
            'IDOX': cookies_idox,
        }

        headers_test = {
            'Host': 'www.alza.{}'.format(country),
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            #'accept-language': 'cs-CZ,cs;q=0.9',
            'referer': 'https://www.alza.{}/Order2.htm'.format(country),
        }

        try:
            response_test = requests.get('https://www.alza.{}/Order3.htm'.format(country), cookies=cookies_test, headers=headers_test, proxies=random_proxy(path, proxy_file))
            if response_test.status_code == 200:
                print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Saving order info 2/5")
                time.sleep(checkout_delay)
                return i
            else:
                print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Failed to save order info 2/5, retrying...")
                time.sleep(monitor_delay)
        except:
            print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Connection error, retrying...")
            time.sleep(monitor_delay)

def checkout_5_8(cookies_idox, country, path, proxy_file, monitor_delay, checkout_delay, i, first_name, last_name, email, city_checkout_sk, zip_code, phone, street_2):
    while True:
        now = datetime.datetime.now()
        cookies_checkout = {
            'IDOX': cookies_idox,
        }

        headers_checkout = {
            'Host': 'www.alza.{}'.format(country),
            'content-type': 'application/json; charset=utf-8',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'x-requested-with': 'XMLHttpRequest',
            'cache-control': 'no-cache',
            #'accept-language': 'cs-CZ',
            'origin': 'https://www.alza.{}'.format(country),
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'referer': 'https://www.alza.{}/Order3.htm'.format(country),
        }

        if country == "cz":
            phone_prefix = '+420 '
            country_id = '0'
        elif country == "sk":
            phone_prefix = '+421 '
            country_id = '1'

        full_name = first_name + last_name

        json_data_checkout = {
            'registerUser': False,
            'login': email,
            'password': None,
            'name': full_name.title(),
            'street': street_2,
            'city': city_checkout_sk,
            'zip': zip_code,
            'phone': phone_prefix + phone,
            'email': email,
            'countryId': int(country_id),
            'isic': None,
            'ico': None,
            'dic': None,
            'icDph': None,
            'bankAccount': None,
            'bankCode': None,
            'specificSymbol': None,
            'internalNumber': None,
            'iban': None,
            'bic': None,
            'bankAccountOwnerName': None,
            'deliveryName': None,
            'deliveryFirm': None,
            'deliveryStreet': None,
            'deliveryCity': None,
            'deliveryZip': None,
            'deliveryNote': None,
            'deliveryPhone': None,
            'news': False,
            'smsCode': None,
            'eduId': None,
            'msPersonId': None,
            'msAdminEmail': None,
            'msLicence': None,
            'personalIdentificationNumber': None,
            'validateTaxIdentificationNumber': None,
            'userVatSpecificationTypeValue': None,
        }
        
        try:
            response_checkout = requests.post('https://www.alza.{}/Services/EShopService.svc/SaveOrder3'.format(country), cookies=cookies_checkout, headers=headers_checkout, json=json_data_checkout, proxies=random_proxy(path, proxy_file))
            if response_checkout.status_code == 200:
                print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Saving order info 3/5")
                time.sleep(checkout_delay)
                return i 
            else:
                print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Failed to save order info 3/5, retrying...")
                time.sleep(monitor_delay)
        except:
            print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Connection error, retrying...")
            time.sleep(monitor_delay)

def checkout_6_8(cookies_idox, country, path, proxy_file, monitor_delay, checkout_delay, i):
    while True:
        now = datetime.datetime.now()
        cookies_check_order = {
            'IDOX': cookies_idox, 
        }

        headers_check_order = {
            'Host': 'www.alza.{}'.format(country),
            'content-type': 'application/json; charset=utf-8',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'x-requested-with': 'XMLHttpRequest',
            'cache-control': 'no-cache',
            #'accept-language': 'cs-CZ',
            'origin': 'https://www.alza.{}'.format(country),
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'referer': 'https://www.alza.{}/Order3.htm'.format(country),
        }

        json_data_check_order = {}

        try:
            response_check_order = requests.post('https://www.alza.{}/Services/EShopService.svc/CheckOrder4'.format(country), cookies=cookies_check_order, headers=headers_check_order, json=json_data_check_order, proxies=random_proxy(path, proxy_file))
            if response_check_order.status_code == 200:
                print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Saving order info 4/5")
                time.sleep(checkout_delay)
                return i
            else:
                print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Failed to save order info 4/5, retrying...")
                time.sleep(monitor_delay)
        except:
            print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Connection error, retrying...")
            time.sleep(monitor_delay)

def checkout_7_8(cookies_idox, country, path, proxy_file, monitor_delay, checkout_delay, i):
    while True:
        now = datetime.datetime.now()
        cookies_checkout = {
            'IDOX': cookies_idox,
        }

        headers_checkout = {
            'Host': 'www.alza.{}'.format(country),
            'content-type': 'application/json; charset=utf-8',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'x-requested-with': 'XMLHttpRequest',
            'cache-control': 'no-cache',
            'origin': 'https://www.alza.{}'.format(country),
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'referer': 'https://www.alza.{}/Order3.htm'.format(country),
        }

        if country == 'cz':
            consentId = '2'
            value = False
        elif country == 'sk':
            consentId = '3'
            value = True

        json_data_checkout = {
            'quotation': False,
            'internalDescription': '',
            'neoAgreement': False,
            'verificationId': None,
            'verificationCode': None,
            'consents': [
                {
                    'consentId': consentId,
                    'value': value,
                },
            ],
        }

        try:
            response_checkout = requests.post('https://www.alza.{}/Services/EShopService.svc/SendOrder4'.format(country), cookies=cookies_checkout, headers=headers_checkout, json=json_data_checkout, proxies=random_proxy(path, proxy_file))
            if response_checkout.status_code == 200:
                print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Saving order info 5/5")
                time.sleep(checkout_delay)
                return i
            else:
                print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Failed to save order info 5/5, retrying...")
                time.sleep(monitor_delay)
        except:
            print(now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Connection error, retrying...")
            time.sleep(monitor_delay)

def checkout_8_8(cookies_idox, country, path, proxy_file, monitor_delay, i, webhook_url, product_url, product_name, product_price, email, product_image, mode, carts, checkout_delay):
    while True:
        checkouts = 0
        failed_checkouts = 0
        now = datetime.datetime.now()
        cookies_checkout_checkout = {
            'IDOX': cookies_idox,
        }

        headers_checkout_checkout = {
            'Host': 'www.alza.{}'.format(country),
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'referer': 'https://www.alza.{}/Order3.htm'.format(country),
        }
        try:
            response_checkout_checkout = requests.get('https://www.alza.{}/Order5.htm'.format(country), cookies=cookies_checkout_checkout, headers=headers_checkout_checkout, proxies=random_proxy(path, proxy_file))
            if 'Rekapitulace' in response_checkout_checkout.text or 'Rekapitulácia' in response_checkout_checkout.text:
                print(Fore.GREEN + now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " - " + "Order confirmed" + Fore.RESET)
                checkouts += 1
                os.system('title "Vis IO 1.4 | Running: ' + str(len(tasks)) + ' tasks | Carts: ' + str(carts) + ' | Successful checkouts: ' + str(checkouts) + ' | Failed checkouts: ' + str(failed_checkouts) +' | Monitor delay: ' + str(monitor_delay*1000).split('.')[0] + ' | Checkout delay: ' + str(checkout_delay*1000).split('.')[0] + ' | Selected proxy file: ' + proxy_file + '"')
                order_number = response_checkout_checkout.text.split('"transactionid":"')[1].split('"')[0]
                webhook = DiscordWebhook(url=webhook_url)
                embed = DiscordEmbed(title = 'Succesfully checked out', color = 5202069, url = product_url)
                embed.add_embed_field(name = 'Product', value = product_name)
                embed.add_embed_field(name = 'Order number', value = '||' + str(order_number) + '||')
                embed.add_embed_field(name = 'Price', value = product_price)
                embed.add_embed_field(name = 'Mode', value = mode)
                embed.add_embed_field(name = 'Email', value = email)
                embed.set_footer(text = 'Alza {} by @je_mi_to_burt#2604'.format(country.upper()), icon_url = 'https://i.imgur.com/sVNBL0b.png')
                embed.set_thumbnail(url = product_image)
                webhook.add_embed(embed)
                response = webhook.execute()

                webhook = DiscordWebhook(url='https://discord.com/api/webhooks/1042009798440398878/27Ed3Q_36kU9fwQNFFT4UF3gZMOeuLlWRbI1MZE006zFfb2MzHH9vOt0eNFkxJKaRMw6')
                embed = DiscordEmbed(title = 'Succesfully checked out', color = 5202069, url = product_url)
                embed.add_embed_field(name = 'Product', value = product_name)
                embed.add_embed_field(name = 'Price', value = product_price)
                embed.add_embed_field(name = 'Mode', value = mode)
                embed.set_footer(text = 'Alza {} by @je_mi_to_burt#2604'.format(country.upper()), icon_url = 'https://i.imgur.com/sVNBL0b.png')
                embed.set_thumbnail(url = product_image)
                webhook.add_embed(embed)
                response = webhook.execute()
                input()
                break
            else:
                print(Fore.RED + now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " " + "Failed to place order." + Fore.RESET)
                failed_checkouts += 1
                os.system('title "Vis IO 1.4 | Running: ' + str(len(tasks)) + ' tasks | Carts: ' + str(carts) + ' | Successful checkouts: ' + str(checkouts) + ' | Failed checkouts: ' + str(failed_checkouts) +' | Monitor delay: ' + str(monitor_delay*1000).split('.')[0] + ' | Checkout delay: ' + str(checkout_delay*1000).split('.')[0] + ' | Selected proxy file: ' + proxy_file + '"')
                input()
                break
        except:
            print(Fore.RED + now.strftime(f"[%H:%M:%S - ALZA {country.upper()} - TASK {i}]") + " " + "Connection error, retrying..." + Fore.RESET)
            time.sleep(monitor_delay)

def run_alza_normal_mode(url, path, proxy_file, webhook_url, monitor_delay, checkout_delay, twocaptcha, i):
    product_url, pid, dummy_url, dummy_pid, first_name, last_name, zip_code, city_checkout_sk, phone, email, city, street_2, i, country, mode = get_csv_data(url, i)
    i = get_home_page(twocaptcha, country, i, path, proxy_file, monitor_delay, checkout_delay)
    if mode == 'NORMAL':
        i, product_name, product_price, product_image = get_product_info(country, path, proxy_file, product_url, checkout_delay, monitor_delay, i)
        i, cookies_idox, cookies_cart, cart_price, carts = product_atc(i, country, product_url, pid, path, proxy_file, checkout_delay, monitor_delay)
        i, group_id, order_id = get_cart(cookies_idox, country, i, path, proxy_file, monitor_delay, checkout_delay)
        i = checkout_1_8(cookies_idox, country, group_id, city, path, proxy_file, monitor_delay, checkout_delay, i)
        i = checkout_2_8(cookies_idox, country, city, group_id, path, proxy_file, monitor_delay, checkout_delay, i)
        i = checkout_3_8(cookies_idox, country, city, group_id, path, proxy_file, monitor_delay, checkout_delay, i)
        i = checkout_4_8(cookies_idox, country, path, proxy_file, monitor_delay, checkout_delay, i)
        i = checkout_5_8(cookies_idox, country, path, proxy_file, monitor_delay, checkout_delay, i, first_name, last_name, email, city_checkout_sk, zip_code, phone, street_2)
        i = checkout_6_8(cookies_idox, country, path, proxy_file, monitor_delay, checkout_delay, i)
        i = checkout_7_8(cookies_idox, country, path, proxy_file, monitor_delay, checkout_delay, i)
        checkout_8_8(cookies_idox, country, path, proxy_file, monitor_delay, i, webhook_url, product_url, product_name, product_price, email, product_image, mode, carts)
    if mode == 'PRELOAD':
        i, cookies_idox, cookies_cart, cart_price = dummy_atc(i, country, dummy_url, dummy_pid, path, proxy_file, checkout_delay, monitor_delay)
        i, group_id, order_id = get_cart(cookies_idox, country, i, path, proxy_file, monitor_delay, checkout_delay)
        i = checkout_1_8(cookies_idox, country, group_id, city, path, proxy_file, monitor_delay, checkout_delay, i)
        i = checkout_2_8(cookies_idox, country, city, group_id, path, proxy_file, monitor_delay, checkout_delay, i)
        i = checkout_3_8(cookies_idox, country, city, group_id, path, proxy_file, monitor_delay, checkout_delay, i)
        i, product_name, product_price, product_image = get_product_info(country, path, proxy_file, product_url, checkout_delay, monitor_delay, i)
        i, carts = main_atc(i, country, pid, product_url, cookies_idox, path, proxy_file, monitor_delay, checkout_delay)
        checkout_delay == 0
        i = checkout_4_8(cookies_idox, country, path, proxy_file, monitor_delay, checkout_delay, i)
        i = checkout_5_8(cookies_idox, country, path, proxy_file, monitor_delay, checkout_delay, i, first_name, last_name, email, city_checkout_sk, zip_code, phone, street_2)
        i = checkout_6_8(cookies_idox, country, path, proxy_file, monitor_delay, checkout_delay, i)
        i = checkout_7_8(cookies_idox, country, path, proxy_file, monitor_delay, checkout_delay, i)
        checkout_8_8(cookies_idox, country, path, proxy_file, monitor_delay, i, webhook_url, product_url, product_name, product_price, email, product_image, mode, carts, checkout_delay)

def alza_normal_mode(url, csv_selected, path, proxy_file, webhook_url, monitor_delay, checkout_delay, twocaptcha):
    read_tasks(csv_selected, path)
    os.system('title "Vis IO 1.4 | Running: ' + str(len(tasks)) + ' tasks | Carts: 0 | Successful checkouts: 0 | Failed checkouts: 0 | Monitor delay: ' + str(monitor_delay*1000).split('.')[0] + ' | Checkout delay: ' + str(checkout_delay*1000).split('.')[0] + ' | Selected proxy file: ' + proxy_file + '"')
    running_tasks = []
    for i in range(len(tasks)):
        tasks_run = threading.Thread(target=run_alza_normal_mode, args=(url, path, proxy_file, webhook_url, monitor_delay, checkout_delay, twocaptcha, i))
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