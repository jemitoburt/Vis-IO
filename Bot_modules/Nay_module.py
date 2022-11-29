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

stores_checkout = {
   "Banska Bystrica":178,
   "Bardejov":1239,
   "Bratislava Aupark":160,
   "Bratislava Avion":199,
   "Bratislava Bory Mall":202,
   "Bratislava Central":198,
   "Bratislava Danubia":159,
   "Bratislava Nivy":24710,
   "Bratislava Zlate Piesky":2,
   "Cadca":177,
   "Dunajska Streda":264,
   "Humenne":270,
   "Komarno":173,
   "Kosice Pri pracharni":185,
   "Kosice Trolejbusova 1B":197,
   "Levice":172,
   "Liptovsky Mikulas":176,
   "Lucenec":180,
   "Malacky OC NEO ZONA":288,
   "Martin":175,
   "Michalovce":187,
   "Nitra":170,
   "Nove Zamky":171,
   "Piestany":10531,
   "Poprad":183,
   "Povazska Bystrica":169,
   "Presov Kosicka":181,
   "Presov Lubotice":10425,
   "Prievidza":168,
   "Rimavská Sobota":272,
   "Skalica":166,
   "Spiaska Nova Ves":188,
   "Stara Lubovna":184,
   "Trebisov":268,
   "Trencin":167,
   "Trnava":164,
   "Vranov nad Toplou":266,
   "Zilina":174,
   "Zvolen":179
}

stores_reservation = {
    "Bratislava Danubia":242,
    "Bratislava Aupark":244,
    "Bratislava Central":298,
    "Bratislava Bory-Mall":302,
    "Malacky OC NEO ZONA":318,
    "Trnava":248,
    "Dunajska Streda":250,
    "Skalica":252,
    "NAY Trencin":254,
    "Prievidza":256,
    "Povazska Bystrica":258,
    "Nitra":260,
    "Nove Zamky":262,
    "Levice":264,
    "Komarno":266,
    "Zilina":268,
    "Martin":270,
    "Liptovsky Mikulas":272,
    "Cadca":274,
    "Banska Bystrica":276,
    "Zvolen":278,
    "Lucenec":280,
    "Presov Kosicka 2/C":282,
    "Poprad":286,
    "Stara Lubovna":288,
    "Kosice Pri pracharni":290,
    "Michalovce":292,
    "Spisská Nova Ves":294,
    "Bratislava Avion":296,
    "Kosice Trolejbusova 1/B":300,
    "Vranov nad Toplou":304,
    "Trebisov":306,
    "Humenne":308,
    "Rimavska Sobota":310,
    "Bardejov":1255,
    "Presov Lubotice":10411,
    "Bratislava Zlate Piesky":240,
    "Piestany":10499,
    "Bratislava Nivy":24689
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
        url = task['url']
    firstName = task['firstName']
    lastName = task['lastName']
    phone = task['phone']
    email = task['email']
    city = task['city']
    storeId = stores_checkout[city]
    storeId_reservation = stores_reservation[city]
    return url, firstName, lastName, phone, email, storeId, storeId_reservation

def get_cart_token(url, i, monitor_delay, checkout_delay, path, proxy_file):
    i += 1
    while True:
        now = datetime.datetime.now()
        headers_cart_token = {
            'Host': 'www.nay.sk',
            'accept': 'application/json, text/plain, */*',
            'x-client-version': 'v22.11.03.2',
            'accept-language': 'sk-SK',
            'origin': 'https://www.nay.sk',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'referer': url,
            'x-pd-googleanalytics': 'GA1.2.1944539633.1667466327',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        try:
            response_cart_token = requests.post('https://www.nay.sk/api/eshop/baskets', headers=headers_cart_token, proxies=random_proxy(path, proxy_file))
            if response_cart_token.status_code == 200:
                jsonCartToken = json.loads(response_cart_token.text)
                cartToken = jsonCartToken['hash']
                print(now.strftime(f"[%H:%M:%S - NAY SK - TASK {i}]") + ' ' + 'Got cart token')
                time.sleep(checkout_delay)
                return cartToken, i
            else:
                print(Fore.RED + now.strftime(f"[%H:%M:%S - NAY SK - TASK {i}]") + ' ' + 'Failed to get cart token, retrying...' + Fore.RESET)
                time.sleep(monitor_delay)
        except:
            print(Fore.RED + now.strftime(f"[%H:%M:%S - NAY SK - TASK {i}]") + ' ' + 'Connection error, retrying...' + Fore.RESET)
            time.sleep(monitor_delay)

def get_product_id(url, i, monitor_delay, checkout_delay, path, proxy_file):
    urlApi = url.split('/')[3]
    while True:
        now = datetime.datetime.now()
        headers_product_page = {
            'Host': 'www.nay.sk',
            'accept': 'application/json, text/plain, */*',
            'x-client-version': 'v22.11.03.2',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'accept-language': 'cs-CZ,cs;q=0.9',
            'referer': url,
        }
        try:
            response_product_page = requests.get('https://www.nay.sk/api/eshop/router/' + urlApi, headers=headers_product_page,proxies=random_proxy(path, proxy_file))
            if response_product_page.status_code == 200:
                json_product_page = json.loads(response_product_page.text)
                pid = json_product_page['mainId']
                print(now.strftime(f"[%H:%M:%S - NAY SK - TASK {i}]") + ' ' + 'Got PID')
                time.sleep(checkout_delay)
                return pid, i
            elif response_product_page.status_code == 404:
                print(now.strftime(f"[%H:%M:%S - NAY SK - TASK {i}]") + ' ' + 'Product not found, retrying...')
                time.sleep(monitor_delay)
        except:
            print(Fore.RED + now.strftime(f"[%H:%M:%S MONITORING TASK]") + ' ' + 'Connection error, retrying...' + Fore.RESET)
            time.sleep(monitor_delay)

def product_atc(cartToken, url, pid, checkout_delay, monitor_delay, i, path, proxy_file):
    while True:
        now = datetime.datetime.now()
        headers_atc = {
            'Host': 'www.nay.sk',
            'content-type': 'application/json;charset=utf-8',
            'accept': 'application/json, text/plain, */*',
            'x-basket': cartToken,
            'x-client-version': 'v22.11.03.2',
            'accept-language': 'sk-SK',
            'origin': 'https://www.nay.sk',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'x-pd-googleanalytics': 'GA1.2.398612545.1667463293',
            'referer': url,
        }

        json_data_atc = {
            'productId': pid,
            'quantity': 1,
            'services': [],
            'gifts': [],
        }

        try:
            response_atc = requests.post('https://www.nay.sk/api/eshop/baskets/' + cartToken + '/products', headers=headers_atc, json=json_data_atc,proxies=random_proxy(path, proxy_file))
            if response_atc.status_code == 200:
                print(Fore.GREEN + now.strftime(f"[%H:%M:%S - NAY SK - TASK {i}]") + ' ' + 'Succesfully added to cart' + Fore.RESET)
                time.sleep(checkout_delay)
                return i
            else:
                print(Fore.RED + now.strftime(f"[%H:%M:%S - NAY SK - TASK {i}]") + ' ' + 'Failed to add to cart, retrying...' + Fore.RESET)
                time.sleep(monitor_delay)
        except:
            print(Fore.RED + now.strftime(f"[%H:%M:%S - NAY SK - TASK {i}]") + ' ' + 'Connection error, retrying...' + Fore.RESET)
            time.sleep(monitor_delay)

def get_cart(cartToken, url, checkout_delay, monitor_delay, i, path, proxy_file):
    while True:
        now = datetime.datetime.now()
        headers_get_cart = {
            'Host': 'www.nay.sk',
            'accept': 'application/json, text/plain, */*',
            'x-client-version': 'v22.11.03.2',
            'referer': url,
            'x-pd-googleanalytics': 'GA1.2.1944539633.1667466327',
            'x-basket': cartToken,
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'accept-language': 'sk-SK',
        }
        try:
            response_get_cart = requests.get('https://www.nay.sk/api/eshop/baskets/' + cartToken, headers=headers_get_cart,proxies=random_proxy(path, proxy_file))
            if response_get_cart.status_code == 200:
                print(now.strftime(f"[%H:%M:%S - NAY SK - TASK {i}]") + ' ' + 'Got cart')
                time.sleep(checkout_delay)
                return i
            else:
                print(now.strftime(f"[%H:%M:%S - NAY SK - TASK {i}]") + ' ' + 'Failed to get cart, retrying...')
                time.sleep(monitor_delay)
        except:
            print(Fore.RED + now.strftime(f"[%H:%M:%S - NAY SK - TASK {i}]") + ' ' + 'Connection error, retrying...' + Fore.RESET)
            time.sleep(monitor_delay)

def sumbit_address(cartToken, checkout_delay, monitor_delay, i, storeId, path, proxy_file):
    while True:
        now = datetime.datetime.now()
        headers_submit_addy = {
            'Host': 'www.nay.sk',
            'content-type': 'application/json;charset=utf-8',
            'accept': 'application/json, text/plain, */*',
            'x-basket': cartToken,
            'x-client-version': 'v22.11.03.2',
            'accept-language': 'sk-SK',
            'origin': 'https://www.nay.sk',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'x-pd-googleanalytics': 'GA1.2.1944539633.1667466327',
            'referer': 'https://www.nay.sk/objednavka-doprava-a-platba',
        }

        json_data_submit_addy = {
            'deliveryMethodId': storeId,
            'zip': None,
        }
        try:
            response_submit_addy = requests.post('https://www.nay.sk/api/eshop/baskets/' + cartToken + '/delivery-method', headers=headers_submit_addy, json=json_data_submit_addy,proxies=random_proxy(path, proxy_file))
            if response_submit_addy.status_code == 200:
                print(now.strftime(f"[%H:%M:%S - NAY SK - TASK {i}]") + ' ' + 'Submitted addy')
                time.sleep(checkout_delay)
                return i
            else:
                print(now.strftime(f"[%H:%M:%S - NAY SK - TASK {i}]") + ' ' + 'Failed to submit addy, retrying...')
                time.sleep(monitor_delay)
        except:
            print(Fore.RED + now.strftime(f"[%H:%M:%S - NAY SK - TASK {i}]") + ' ' + 'Connection error, retrying...' + Fore.RESET)
            time.sleep(monitor_delay)

def submit_payment(cartToken, checkout_delay, monitor_delay, i, path, proxy_file):
    while True:
        now = datetime.datetime.now()
        headers_payment = {
            'Host': 'www.nay.sk',
            'content-type': 'application/json;charset=utf-8',
            'accept': 'application/json, text/plain, */*',
            'x-basket': cartToken,
            'x-client-version': 'v22.11.03.2',
            'accept-language': 'sk-SK',
            'origin': 'https://www.nay.sk',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'x-pd-googleanalytics': 'GA1.2.1944539633.1667466327',
            'referer': 'https://www.nay.sk/objednavka-doprava-a-platba',
        }

        json_data_payment = {
            'payMethodId': 8,
        }

        try:
            response_payment = requests.post('https://www.nay.sk/api/eshop/baskets/' + cartToken + '/pay-method', headers=headers_payment, json=json_data_payment,proxies=random_proxy(path, proxy_file))
            if response_payment.status_code == 200:
                print(now.strftime(f"[%H:%M:%S - NAY SK - TASK {i}]") + ' ' + 'Submitted payment')
                time.sleep(checkout_delay)
                return i
            else:
                print(now.strftime(f"[%H:%M:%S - NAY SK - TASK {i}]") + ' ' + 'Payment failed, retrying')
                time.sleep(monitor_delay)
        except:
            print(Fore.RED + now.strftime(f"[%H:%M:%S - NAY SK - TASK {i}]") + ' ' + 'Connection error, retrying...' + Fore.RESET)
            time.sleep(monitor_delay)

def submit_order(cartToken, i, firstName, lastName, phone, email, pid, url, webhook_url, path, proxy_file):
    while True:
        now = datetime.datetime.now()
        headers_submit_order = {
            'Host': 'www.nay.sk',
            'content-type': 'application/json;charset=utf-8',
            'accept': 'application/json, text/plain, */*',
            'x-basket': cartToken,
            'x-client-version': 'v22.11.03.2',
            'accept-language': 'sk-SK',
            'origin': 'https://www.nay.sk',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'x-pd-googleanalytics': 'GA1.2.1944539633.1667466327',
            'referer': 'https://www.nay.sk/informace-o-vas',
        }

        json_data_submit_order = {
            'customer': {
                'firstName': firstName,
                'lastName': lastName,
                'phone': '+421' + phone,
                'email': email,
                'billingAddress': None,
                'companyInfo': None,
                'deliveryAddress': None,
            },
            'orderNote': None,
            'consents': [
                'general_terms_condition',
            ],
            'basketHash': cartToken,
        }

        response_submit_order = requests.post('https://www.nay.sk/api/eshop/orders', headers=headers_submit_order, json=json_data_submit_order,proxies=random_proxy(path, proxy_file))
 
        if response_submit_order.status_code == 200:
            print(Fore.GREEN + now.strftime(f"[%H:%M:%S - NAY SK - TASK {i}]") + ' ' + 'Succesfully checked out' + Fore.RESET)
            orderInfoJson = json.loads(response_submit_order.text)['order']
            orderNumber = orderInfoJson['number']
            price = orderInfoJson['totalSum']
            nameOrder = orderInfoJson['customerInfo']['firstName'] + ' ' + orderInfoJson['customerInfo']['lastName']
            emailOrder = orderInfoJson['customerInfo']['email']
            deliveryShop_raw = orderInfoJson['deliveryMethod']['childName']
            encoded = deliveryShop_raw.encode("UTF-8")
            deliveryShop_raw_decoded = encoded.decode("UTF-8")
            for data in orderInfoJson['products']:
                productName = data['name']

            webhook = DiscordWebhook(url = 'https://discord.com/api/webhooks/1042009798440398878/27Ed3Q_36kU9fwQNFFT4UF3gZMOeuLlWRbI1MZE006zFfb2MzHH9vOt0eNFkxJKaRMw6')
            embed = DiscordEmbed(title = 'Succesfully checked out', color = 5202069, url = url)
            embed.add_embed_field(name = 'Product', value = productName)
            embed.add_embed_field(name = 'Price', value = price)
            embed.set_footer(text = 'Nay SK @je_mi_to_burt#2604', icon_url = 'https://i.imgur.com/sVNBL0b.png')
            webhook.add_embed(embed)
            response = webhook.execute()
            
            webhook = DiscordWebhook(url = webhook_url)
            embed = DiscordEmbed(title = 'Succesfully checked out', color = 5202069, url = url)
            embed.add_embed_field(name = 'Product', value = productName)
            embed.add_embed_field(name = 'Order number', value = '||' + str(orderNumber) + '||')
            embed.add_embed_field(name = 'Price', value = price,)
            embed.add_embed_field(name = 'Name on order', value = nameOrder)
            embed.add_embed_field(name = 'Email', value = emailOrder,)
            embed.add_embed_field(name = 'Delivery shop', value = deliveryShop_raw_decoded)
            embed.set_footer(text = 'Nay SK by @je_mi_to_burt#2604', icon_url = 'https://i.imgur.com/sVNBL0b.png')
            webhook.add_embed(embed)
            response = webhook.execute()
            time.sleep(20)
            break
        else:
            print(Fore.RED + now.strftime(f"[%H:%M:%S - NAY SK - TASK {i}]") + ' ' + 'Checkout failed' + Fore.RESET)
            webhook = DiscordWebhook(url = webhook_url)
            embed = DiscordEmbed(title = 'Checkout failed', color = 8388640, url = url)
            embed.set_footer(text = 'Nay SK module by @je_mi_to_burt#2604', icon_url = 'https://i.imgur.com/sVNBL0b.png')
            webhook.add_embed(embed)
            response = webhook.execute()
            break

def submit_instore_reservation(cartToken, url, phone, email, pid, storeId_reservation, i, path, proxy_file, webhook_url, monitor_delay):
    while True:
        now = datetime.datetime.now()
        headers_instore_reservation = {
            'Host': 'www.nay.sk',
            'content-type': 'application/json;charset=utf-8',
            'accept': 'application/json, text/plain, */*',
            'x-basket': cartToken,
            'x-client-version': 'v22.11.08.1',
            'accept-language': 'sk-SK',
            'origin': 'https://www.nay.sk',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'x-pd-googleanalytics': 'GA1.2.398612545.1667463293',
            'referer': url,
        }

        json_data_instore_reservation = {
            'phone': '+421' + phone,
            'email': email,
            'customerInfo': None,
            'product': {
                'productId': pid,
                'quantity': 1,
                'gifts': [],
            },
            'warehouseId': storeId_reservation,
            'agreedDisplayedProduct': False,
            'agreedMissingGifts': False,
        }

        try:
            response_instore_reservation = requests.post('https://www.nay.sk/api/eshop/reservations', headers=headers_instore_reservation, json=json_data_instore_reservation, proxies=random_proxy(path, proxy_file))
            if response_instore_reservation.status_code == 200:
                print(Fore.GREEN + now.strftime(f"[%H:%M:%S - NAY SK - TASK {i}]") + ' ' + 'Instore reservation success' + Fore.RESET)
                json_checkout = json.loads(response_instore_reservation.text)['reservation']
                reservationId = json_checkout['number']
                email = json_checkout['email']
                phone = json_checkout['phone']
                deliveryShop_raw = json_checkout['store']['name']
                encoded = deliveryShop_raw.encode("UTF-8")
                deliveryShop_raw_decoded = encoded.decode("UTF-8")
                price = json_checkout['totalSum']
                for data in json_checkout['products']:
                    productName = data['name']            
                
                webhook = DiscordWebhook(url = webhook_url)
                embed = DiscordEmbed(title = 'Succesfully reserved instore', color = 5202069, url = url)
                embed.add_embed_field(name = 'Product', value = productName)
                embed.add_embed_field(name = 'Order number', value = '||' + str(reservationId) + '||', inline = False)
                embed.add_embed_field(name = 'Price', value = price, inline = True)
                embed.add_embed_field(name = 'Name on order', value = email, inline = True)
                embed.add_embed_field(name = 'Delivery shop', value = deliveryShop_raw_decoded, inline = True)
                embed.set_footer(text = 'Nay SK module by @je_mi_to_burt#2604', icon_url = 'https://i.imgur.com/sVNBL0b.png')
                webhook.add_embed(embed)
                response = webhook.execute()

                webhook = DiscordWebhook(url = 'https://discord.com/api/webhooks/1037737034367897681/zJYBtou7g61wnjK97XN0eZBT15sxe3lb5HGsib4oGKsS2zRPf2uTQJDFlgPAzmCuGruV')
                embed = DiscordEmbed(title = 'Succesfully reserved instore', color = 5202069, url = url)
                embed.add_embed_field(name = 'Product', value = productName)
                embed.add_embed_field(name = 'Price', value = price, inline = True)
                embed.set_footer(text = 'Nay SK module by @je_mi_to_burt#2604', icon_url = 'https://i.imgur.com/sVNBL0b.png')
                webhook.add_embed(embed)
                response = webhook.execute()
                time.sleep(20)
                break

            if response_instore_reservation.status_code == 412:
                print(now.strftime(f"[%H:%M:%S - NAY SK - TASK {i}]") + ' ' + 'Product is not available in this city, retrying...')
                time.sleep(monitor_delay)
            else:
                print(now.strftime(f"[%H:%M:%S - NAY SK - TASK {i}]") + ' ' + 'Instore reservation failed, retrying...')
                time.sleep(monitor_delay)
        except:
            print(now.strftime(f"[%H:%M:%S - NAY SK - TASK {i}]") + ' ' + 'Connection error, retrying...')
            time.sleep(monitor_delay)

def run_nay_normal_mode(url, path, proxy_file, webhook_url, monitor_delay, checkout_delay, i):
    url, firstName, lastName, phone, email, storeId, storeId_reservation = get_csv_data(url, i)
    cartToken, i = get_cart_token(url, i, monitor_delay, checkout_delay, path, proxy_file)
    pid, i = get_product_id(url, i, monitor_delay, checkout_delay, path, proxy_file)
    i = product_atc(cartToken, url, pid, checkout_delay, monitor_delay, i, path, proxy_file)
    i = get_cart(cartToken, url, checkout_delay, monitor_delay, i, path, proxy_file)
    i = sumbit_address(cartToken, checkout_delay, monitor_delay, i, storeId, path, proxy_file)
    i = submit_payment(cartToken, checkout_delay, monitor_delay, i, path, proxy_file)
    submit_order(cartToken, i, firstName, lastName, phone, email, pid, url, webhook_url, path, proxy_file)

def nay_normal_mode(url, csv_selected, path, proxy_file, webhook_url, monitor_delay, checkout_delay):
    read_tasks(csv_selected, path)
    running_tasks = []
    for i in range(len(tasks)):
        tasks_run = threading.Thread(target=run_nay_normal_mode, args=(url, path, proxy_file, webhook_url, monitor_delay, checkout_delay, i))
        running_tasks.append(tasks_run)
    if len(tasks) > 20:
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
 
def run_nay_instore_mode(url, path, proxy_file, webhook_url, monitor_delay, checkout_delay, i):
    url, firstName, lastName, phone, email, storeId, storeId_reservation = get_csv_data(url, i)
    cartToken, i = get_cart_token(url, i, monitor_delay, checkout_delay, path, proxy_file)
    pid, i = get_product_id(url, i, monitor_delay, checkout_delay, path, proxy_file)
    submit_instore_reservation(cartToken, url, phone, email, pid, storeId_reservation, i, path, proxy_file, webhook_url, monitor_delay)

def nay_instore_mode(url, csv_selected, path, proxy_file, webhook_url, monitor_delay, checkout_delay):
    read_tasks(csv_selected, path)
    running_tasks = []
    for i in range(len(tasks)):
        tasks_run = threading.Thread(target=run_nay_instore_mode, args=(url, path, proxy_file, webhook_url, monitor_delay, checkout_delay, i))
        running_tasks.append(tasks_run)
    if len(tasks) > 20:
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