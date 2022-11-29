def normal_mode(webhook_url, monitor_delay, checkout_delay, i, path, proxy_file, twocaptcha):
    global street_2
    global pid
    task = tasks[i]
    store = task['store']
    mode = task['mode']
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
    country = task['country'].lower()
    if country == 'cz':
        city = stores_cz[city]
        street_2 = None
    elif country == 'sk':
        city = stores_sk[city]
        street_1 = task['city']
        street_2 = stores_sk_address[street_1]
    if mode == 'NORMAL':
        get_home_page(store, mode, phone, email, city, product_url, pid, i, webhook_url, monitor_delay, checkout_delay, proxy_file, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk, twocaptcha)
    elif mode == 'PRELOAD':
        get_home_page_dummy(store, mode, phone, email, city, product_url, pid, i, webhook_url, monitor_delay, checkout_delay, proxy_file, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk, twocaptcha, dummy_pid, dummy_url)

def get_home_page(store, mode, phone, email, city, product_url, pid, i, webhook_url, monitor_delay, checkout_delay, proxy_file, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk, twocaptcha):
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

        response_home_page = requests.get('https://www.alza.{}'.format(country), headers=headers_home_page, proxies=random_proxy(path, proxy_file), allow_redirects=True)
        if response_home_page.status_code == 200:
            if 'captcha' not in response_home_page.url:
                print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "No captcha on homepage")
                get_product_info(store, mode, phone, email, city, product_url, pid, i, webhook_url, monitor_delay, checkout_delay, proxy_file, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk, twocaptcha)
                break

            elif 'captcha' in response_home_page.url:
                print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Captcha on homepage")
                captcha_token = response_home_page.text.split('data-sitekey=')[1].split(' data-callback')[0]
                url_captcha = requests.get('http://2captcha.com/in.php?key=' + twocaptcha + '&method=userrecaptcha&googlekey=' + captcha_token + '&pageurl=' + response_home_page.url).text.split('|')[1]
                captcha_solved = requests.get('http://2captcha.com/res.php?key=' + twocaptcha + '&action=get&id=' + url_captcha).text
                
                while 'CAPCHA_NOT_READY' in captcha_solved:
                    now = datetime.datetime.now()
                    time.sleep(monitor_delay)
                    captcha_solved = requests.get('http://2captcha.com/res.php?key=' + twocaptcha + '&action=get&id=' + url_captcha).text
                    if 'OK' in captcha_solved:
                        print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Captcha solved")
                        captcha_solved_token = captcha_solved.split('|')[1]
                        break
                    else:
                        print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Waiting for captcha")
                
                headers_captcha = {
                    'Host': 'www.alza.{}'.format(country),
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
                    'referer': response_home_page.url,
                }

                response_solved = requests.get('https://www.alza.{country}/captcha/verify?solution={captcha_solved_token}&ssa={url_page}'.format(country=country, captcha_solved_token=captcha_solved_token, url_page='https://www.alza.{}'.format(country)), headers=headers_captcha, proxies=random_proxy(path, proxy_file), allow_redirects=True)
                if response_solved.status_code == 200:
                    print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Got home page")
                    get_product_info(store, mode, phone, email, city, product_url, pid, i, webhook_url, monitor_delay, checkout_delay, proxy_file, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk, twocaptcha)
                    break

def get_home_page_dummy(store, mode, phone, email, city, product_url, pid, i, webhook_url, monitor_delay, checkout_delay, proxy_file, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk, twocaptcha, dummy_pid, dummy_url):
    while True:
        i += 1
        now = datetime.datetime.now()
        if country == 'cz':
            response_home_page_dummy = requests.get('https://www.alza.cz/', proxies=random_proxy(path, proxy_file), allow_redirects=True)
        elif country == 'sk':
            response_home_page_dummy = requests.get('https://www.alza.sk/', proxies=random_proxy(path, proxy_file), allow_redirects=True)
        if response_home_page_dummy.status_code == 200:
            if 'captcha' not in response_home_page_dummy.url:
                print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "No captcha on homepage")
                time.sleep(checkout_delay)
                dummy_atc(store, mode, phone, email, city, product_url, pid, i, webhook_url, monitor_delay, checkout_delay, proxy_file, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk, twocaptcha, dummy_pid, dummy_url)
                break

            elif 'captcha' in response_home_page_dummy.url:
                print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Captcha on homepage")
                captcha_token = response_home_page_dummy.text.split('data-sitekey=')[1].split(' data-callback')[0]
                
                url_captcha = requests.get('http://2captcha.com/in.php?key=' + twocaptcha + '&method=userrecaptcha&googlekey=' + captcha_token + '&pageurl=' + response_home_page_dummy.url).text.split('|')[1]
                captcha_solved = requests.get('http://2captcha.com/res.php?key=' + twocaptcha + '&action=get&id=' + url_captcha).text

                while 'CAPCHA_NOT_READY' in captcha_solved:
                    now = datetime.datetime.now()
                    time.sleep(monitor_delay)
                    captcha_solved = requests.get('http://2captcha.com/res.php?key=' + twocaptcha + '&action=get&id=' + url_captcha).text
                    if 'OK' in captcha_solved:
                        print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Captcha solved")
                        captcha_solved_token = captcha_solved.split('|')[1]
                        break
                    elif 'OK' not in captcha_solved:
                        print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Waiting for captcha")
                        captcha_solved = requests.get('http://2captcha.com/res.php?key=' + twocaptcha + '&action=get&id=' + url_captcha).text
                
                
                if country == 'cz':
                    headers_captcha = {
                        'Host': 'www.alza.cz',
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
                        'accept-language': 'cs',
                        'referer': response_home_page_dummy.url,
                    }
                    response_solved = requests.get('https://www.alza.cz/captcha/verify?solution={}&ssa=https://www.alza.cz/'.format(captcha_solved_token), headers=headers_captcha, proxies=random_proxy(path, proxy_file), allow_redirects=True)

                elif country == 'sk':
                    headers_captcha = {
                        'Host': 'www.alza.sk',
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
                        'accept-language': 'cs',
                        'referer': response_home_page_dummy.url,
                    }
                    response_solved = requests.get('https://www.alza.sk/captcha/verify?solution={}&ssa=https://www.alza.sk/'.format(captcha_solved_token), headers=headers_captcha, proxies=random_proxy(path, proxy_file), allow_redirects=True)

                if response_solved.status_code == 200:
                    print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Got home page")
                    dummy_atc(store, mode, phone, email, city, product_url, pid, i, webhook_url, monitor_delay, checkout_delay, proxy_file, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk, twocaptcha, dummy_pid, dummy_url)
                    break


def get_product_info(store, mode, phone, email, city, product_url, pid, i, webhook_url, monitor_delay, checkout_delay, proxy_file, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk, twocaptcha):
    while True:
        now = datetime.datetime.now()
        headers_product_info = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Host': 'www.alza.{}'.format(country),
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'Referer': 'https://www.alza.{}/'.format(country),
            'Connection': 'keep-alive',
        }

        response_product_info = requests.get(product_url, headers=headers_product_info, proxies=random_proxy(path, proxy_file), allow_redirects=False)
        
        if response_product_info.status_code == 200:
            #if 'captcha' not in response_product_info.url:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Got product info")
            response_product_info.encoding = response_product_info.apparent_encoding
            response_product_info_encode = response_product_info.text
            if "window.dataLayer.push(" not in response_product_info_encode:
                product_info_str = json.loads(response_product_info_encode.split('"application/ld+json">')[2].split('</script>')[0])
                product_name = product_info_str['name']
                product_price = product_info_str['offers']['price'] + product_info_str['offers']['priceCurrency']
                product_image = product_info_str['image']
                time.sleep(checkout_delay)
                get_product_availability(store, mode, phone, email, city, product_url, pid, i, webhook_url, monitor_delay, checkout_delay, product_name, product_price, product_image, proxy_file, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk)
                break
            elif "window.dataLayer.push(" in response_product_info_encode:
                product_info_str = json.loads(response_product_info_encode.split('window.dataLayer.push(')[1].split(', {"crto":{"email":""')[0])
                product_name = product_info_str['itemName']
                product_price = 'NA'
                product_image = 'https://cdn.alza.sk/ImgW.ashx?fd=f3&cd=' + product_info_str['itemID']
                time.sleep(checkout_delay)
                get_product_availability(store, mode, phone, email, city, product_url, pid, i, webhook_url, monitor_delay, checkout_delay, product_name, product_price, product_image, proxy_file, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk)
                break
        elif response_product_info.status_code == 302:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Product page is not live, retrying...")
            time.sleep(monitor_delay)
        else:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Failed getting product page, retrying...")
            time.sleep(monitor_delay)

def get_product_availability(store, mode, phone, email, city, product_url, pid, i, webhook_url, monitor_delay, checkout_delay, product_name, product_price, product_image, proxy_file, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk):
    while True:
        now = datetime.datetime.now()
        headers_product_availability = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Host': 'www.alza.{}'.format(country),
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'Referer': 'https://www.alza.{}/'.format(country),
            'Connection': 'keep-alive',
        }

        response_product_availability = requests.get(product_url, headers=headers_product_availability, proxies=random_proxy(path, proxy_file))
        
        if 'InStock' in response_product_availability.text:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " +  "Product is in stock")
            time.sleep(checkout_delay)
            product_atc(store, mode, phone, email, city, product_url, pid, i, webhook_url, monitor_delay, checkout_delay, product_name, product_price, product_image, proxy_file, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk)
            break
        else:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Product is out of stock, retrying...")
            time.sleep(monitor_delay)

def dummy_atc(store, mode, phone, email, city, product_url, pid, i, webhook_url, monitor_delay, checkout_delay, proxy_file, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk, twocaptcha, dummy_pid, dummy_url):
    while True:
        now = datetime.datetime.now()
        headers_atc_dummy = {
            'Host': 'www.alza.{}'.format(country),
            'content-type': 'application/json; charset=utf-8',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'x-requested-with': 'XMLHttpRequest',
            'cache-control': 'no-cache',
            'origin': 'https://www.alza.{}'.format(country),
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'referer': dummy_url,
        }
        json_data_dummy = {
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
        response_atc_dummy = requests.post('https://www.alza.{}/Services/EShopService.svc/OrderCommodity'.format(country), headers=headers_atc_dummy, json=json_data_dummy, proxies=random_proxy(path, proxy_file))
        if response_atc_dummy.status_code == 200:
            cookies_idox = response_atc_dummy.cookies['IDOX']
            print(Fore.GREEN + now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Dummy added to cart" + Fore.RESET)
            time.sleep(checkout_delay)
            get_dummy_cart(store, mode, phone, email, city, product_url, i, webhook_url, monitor_delay, checkout_delay, proxy_file, cookies_idox, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk, dummy_pid, dummy_url, pid)
            break
        else:
            print(Fore.RED + now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Failed to add dummy to cart, retrying..." + Fore.RESET)
            time.sleep(monitor_delay)

def get_dummy_cart(store, mode, phone, email, city, product_url, i, webhook_url, monitor_delay, checkout_delay, proxy_file, cookies_idox, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk, dummy_pid, dummy_url, pid):
    while True:
        now = datetime.datetime.now()
        cookies_group_id_dummy = {
            'IDOX': cookies_idox,
        }

        headers_group_id_dummy = {
            'Host': 'www.alza.{}'.format(country),
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
        }

        response_group_id_dummy = requests.get('https://www.alza.{}/Order2.htm'.format(country), cookies=cookies_group_id_dummy, headers=headers_group_id_dummy, proxies=random_proxy(path, proxy_file))
        
        if response_group_id_dummy.status_code == 200:
            group_id_dummy = str(response_group_id_dummy.text.split('"groupId":')[1].split(',')[0])
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Got cart")
            time.sleep(checkout_delay)
            get_shipping_dummy(store, mode, phone, email, city, product_url, i, webhook_url, monitor_delay, checkout_delay, proxy_file, cookies_idox, group_id_dummy, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk, pid)
            break
        else:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Failed to get cart, retrying...")
            time.sleep(monitor_delay)

def get_shipping_dummy(store, mode, phone, email, city, product_url, i, webhook_url, monitor_delay, checkout_delay, proxy_file, cookies_idox, group_id_dummy, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk, pid):
    while True:
        now = datetime.datetime.now()
        cookies_shipping_method_dummy = {
            'IDOX': cookies_idox,
        }

        headers_shipping_method_dummy = {
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

        json_data_shipping_method_dummy = {
            'selectedDeliveryForGroup': {
                'groupId': int(group_id_dummy),
                'deliveryId': str(city),
                'parcelShopId': 0,
            },
            'selectedDeliveriesForGroups': [],
            'selectedDeliveryAccesoriesIds': [],
            'selectedDeliveryZipId': 0,
            'deliveryAddressId': None,
        }

        response_shipping_method_dummy = requests.post('https://www.alza.{}/Services/EShopService.svc/GetOrder2DeliveryInfo'.format(country), cookies=cookies_shipping_method_dummy, headers=headers_shipping_method_dummy, json=json_data_shipping_method_dummy, proxies=random_proxy(path, proxy_file))
        if response_shipping_method_dummy.status_code == 200:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Got shipping method")
            time.sleep(checkout_delay)
            get_dummy_billing(store, mode, phone, email, city, product_url, i, webhook_url, monitor_delay, checkout_delay, proxy_file, cookies_idox, group_id_dummy, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk, pid)
            break
        else:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Failed to get shipping method, retrying...")
            time.sleep(monitor_delay)

def get_dummy_billing(store, mode, phone, email, city, product_url, i, webhook_url, monitor_delay, checkout_delay, proxy_file, cookies_idox, group_id_dummy, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk, pid):
    while True:
        now = datetime.datetime.now()
        cookies_payment_dummy = {
            'IDOX': cookies_idox,
        }

        headers_payment_dummy = {
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
            payment_method_dummy = '101'
        elif country == 'sk':
            payment_method_dummy = '104'

        json_data_payment = {
            'paymentId': int(payment_method_dummy),
            'selectedDeliveriesForGroups': [
                {
                    'deliveryId': int(city),
                    'groupId': int(group_id_dummy),
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

        response_payment_dummy = requests.post('https://www.alza.{}/Services/EShopService.svc/GetOrder2PaymentInfo'.format(country), cookies=cookies_payment_dummy, headers=headers_payment_dummy, json=json_data_payment, proxies=random_proxy(path, proxy_file))
        if response_payment_dummy.status_code == 200:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Got payment method")
            time.sleep(checkout_delay)
            get_dummy_order(store, mode, phone, email, city, product_url, i, webhook_url, monitor_delay, checkout_delay, proxy_file, cookies_idox, group_id_dummy, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk, pid)
            break
        else:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Failed to get payment method, retrying...")
            time.sleep(monitor_delay)

def get_dummy_order(store, mode, phone, email, city, product_url, i, webhook_url, monitor_delay, checkout_delay, proxy_file, cookies_idox, group_id_dummy, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk, pid):
    while True:
        now = datetime.datetime.now()
        cookies_payment_delivery_dummy = {
            'IDOX': cookies_idox,
        }

        headers_payment_delivery_dummy = {
            'Host': 'www.alza.{}'.format(country),
            'content-type': 'application/json; charset=utf-8',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'x-requested-with': 'XMLHttpRequest',
            'cache-control': 'no-cache',
            'origin': 'https://www.alza.{}'.format(country),
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'referer': 'https://www.alza.{}/Order2.htm'.format(country),
        }

        if country == 'cz':
            payment_method_dummy = '101'
        elif country == 'sk':
            payment_method_dummy = '104'

        json_data_payment_delivery = {
            'selectedDeliveriesForGroups': [
                {
                    'deliveryId': int(city),
                    'groupId': int(group_id_dummy),
                    'deliveryTimeFrameId': None,
                    'deliveryTimeSlotId': None,
                    'carDeliveryVehicleId': None,
                    'parcelShopId': None,
                },
            ],
            'paymentId': int(payment_method_dummy),
            'deliveryZipId': 0,
            'paymentCardId': 0,
            'deliveryAccesoriesIds': '',
            'homeBoxInfo': None,
            'deliveryAddressId': None,
        }

        response_payment_delivery_dummy = requests.post('https://www.alza.{}/Services/EShopService.svc/SaveOrder2'.format(country), cookies=cookies_payment_delivery_dummy, headers=headers_payment_delivery_dummy, json=json_data_payment_delivery, proxies=random_proxy(path, proxy_file))
        if response_payment_delivery_dummy.status_code == 200:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Saving order info 1/5")
            time.sleep(checkout_delay)
            get_dummy_info(store, mode, phone, email, product_url, i, webhook_url, monitor_delay, checkout_delay, proxy_file, cookies_idox, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk, pid)
            break
        else:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Failed to save order info 1/5, retrying...")
            time.sleep(monitor_delay)

def get_dummy_info(store, mode, phone, email, product_url, i, webhook_url, monitor_delay, checkout_delay, proxy_file, cookies_idox, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk, pid):
    while True:
        now = datetime.datetime.now()
        cookies_test_dummy = {
            'IDOX': cookies_idox,
        }
        headers_test_dummy = {
            'Host': 'www.alza.{}'.format(country),
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'referer': 'https://www.alza.{}/Order2.htm'.format(country),
        }

        response_test_dummy = requests.get('https://www.alza.{}/Order3.htm'.format(country), cookies=cookies_test_dummy, headers=headers_test_dummy, proxies=random_proxy(path, proxy_file))
        if response_test_dummy.status_code == 200:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Saving order info 2/5, carting main product")
            time.sleep(checkout_delay)
            product_atc_dummy(store, mode, phone, email, product_url, i, webhook_url, monitor_delay, checkout_delay, proxy_file, cookies_idox, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk, pid)
            break
        else:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Failed to save order info 2/5, retrying...")
            time.sleep(monitor_delay)

def product_atc_dummy(store, mode, phone, email, product_url, i, webhook_url, monitor_delay, checkout_delay, proxy_file, cookies_idox, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk, pid):
    while True:
        now = datetime.datetime.now()
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

            response_atc_dummy_2 = requests.post('https://www.alza.{}/Services/EShopService.svc/OrderCommodity'.format(country), headers=headers_atc_dummy_2, json=json_data_dummy_2, cookies=cookies_product_atc_dummy, proxies=random_proxy(path, proxy_file))
            print(response_atc_dummy_2.text)
            if '"ErrorLevel":1' not in response_atc_dummy_2.text:
                print(Fore.GREEN + now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Main product added to cart, continuing in checking out" + Fore.RESET)
                get_dummy_confirmation_1(store, mode, phone, email, product_url, i, webhook_url, monitor_delay, checkout_delay, proxy_file, cookies_idox, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk, pid)
                break
            else:
                print(Fore.RED + now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Main product is oos, retrying..." + Fore.RESET)
                time.sleep(monitor_delay)
        elif check_if_page_is_up.status_code == 302:
            print(Fore.RED + now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Main product page is not loaded, retrying..." + Fore.RESET)
            time.sleep(monitor_delay)

def get_dummy_confirmation_1(store, mode, phone, email, product_url, i, webhook_url, monitor_delay, checkout_delay, proxy_file, cookies_idox, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk, pid):
    while True:
        now = datetime.datetime.now()
        cookies_checkout_dummy = {
            'IDOX': cookies_idox,
        }

        headers_checkout_dummy = {
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
            phone_prefix_dummy = '+420 '
            country_id_dummy = '0'
        elif country == "sk":
            phone_prefix_dummy = '+421 '
            country_id_dummy = '1'

        full_name = first_name + last_name

        json_data_checkout = {
            'registerUser': False,
            'login': email,
            'password': None,
            'name': full_name.title(),
            'street': street_2,
            'city': city_checkout_sk,
            'zip': zip_code,
            'phone': phone_prefix_dummy + phone,
            'email': email,
            'countryId': int(country_id_dummy),
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
        
        response_checkout_dummy = requests.post('https://www.alza.{}/Services/EShopService.svc/SaveOrder3'.format(country), cookies=cookies_checkout_dummy, headers=headers_checkout_dummy, json=json_data_checkout, proxies=random_proxy(path, proxy_file))
        print(response_checkout_dummy.text)
        if response_checkout_dummy.status_code == 200:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Saving order info 3/5")
            get_dummy_order_1(store, mode, email, product_url, i, webhook_url, monitor_delay, checkout_delay, proxy_file, cookies_idox, path, country, pid)
            break
        else:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Failed to save order info 3/5, retrying...")
            time.sleep(monitor_delay)

def get_dummy_order_1(store, mode, email, product_url, i, webhook_url, monitor_delay, checkout_delay, proxy_file, cookies_idox, path, country, pid):
    while True:
        now = datetime.datetime.now()
        cookies_check_order_dummy = {
            'IDOX': cookies_idox, 
        }

        headers_check_order_dummy = {
            'Host': 'www.alza.{}'.format(country),
            'content-type': 'application/json; charset=utf-8',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'x-requested-with': 'XMLHttpRequest',
            'cache-control': 'no-cache',
            'origin': 'https://www.alza.{}'.format(country),
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'referer': 'https://www.alza.{}/Order3.htm'.format(country),
        }

        json_data_check_order_dummy = {}

        response_check_order_dummy = requests.post('https://www.alza.{}/Services/EShopService.svc/CheckOrder4'.format(country), cookies=cookies_check_order_dummy, headers=headers_check_order_dummy, json=json_data_check_order_dummy, proxies=random_proxy(path, proxy_file))
        print(response_check_order_dummy.text)
        if response_check_order_dummy.status_code == 200:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Saving order info 4/5")
            get_dummy_payment(store, mode, email, product_url, i, webhook_url, monitor_delay, checkout_delay, proxy_file, cookies_idox, path, country, pid)
            break
        else:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Failed to save order info 4/5, retrying...")
            time.sleep(monitor_delay)

def get_dummy_payment(store, mode, email, product_url, i, webhook_url, monitor_delay, checkout_delay, proxy_file, cookies_idox, path, country, pid):
    while True:
        now = datetime.datetime.now()
        cookies_checkout_dummy = {
            'IDOX': cookies_idox,
        }

        headers_checkout_dummy = {
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

        if country == 'cz':
            consentId_dummy = '2'
            value_dummy = False
        elif country == 'sk':
            consentId_dummy = '3'
            value_dummy = True

        json_data_checkout = {
            'quotation': False,
            'internalDescription': '',
            'neoAgreement': False,
            'verificationId': None,
            'verificationCode': None,
            'consents': [
                {
                    'consentId': consentId_dummy,
                    'value': value_dummy,
                },
            ],
        }

        response_checkout_dummy = requests.post('https://www.alza.{}/Services/EShopService.svc/SendOrder4'.format(country), cookies=cookies_checkout_dummy, headers=headers_checkout_dummy, json=json_data_checkout, proxies=random_proxy(path, proxy_file))
        print(response_checkout_dummy.text)
        if response_checkout_dummy.status_code == 200:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Saving order info 5/5")
            checkout(store, mode, email, product_url, i, webhook_url, monitor_delay, proxy_file, cookies_idox, path, country)
            break
        else:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Failed to save order info 5/5, retrying...")
            time.sleep(monitor_delay)



def checkout(store, mode, email, product_url, i, webhook_url, monitor_delay, proxy_file, cookies_idox, path, country):
    while True:
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

        response_checkout_checkout = requests.get('https://www.alza.{}/Order5.htm'.format(country), cookies=cookies_checkout_checkout, headers=headers_checkout_checkout, proxies=random_proxy(path, proxy_file))
        if 'Rekapitulace' in response_checkout_checkout.text or 'Rekapitulácia' in response_checkout_checkout.text:
            print(Fore.GREEN + now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Order confirmed" + Fore.RESET)

            jsonStr_checkout = json.loads(response_checkout_checkout.text.split('window.dataLayer.push(')[1].split(', {')[0])
            order_price = jsonStr_checkout['value'] + jsonStr_checkout['currency']
            order_number = response_checkout_checkout.text.split('"transactionid":"')[1].split('"')[0]
            order_product_id = response_checkout_checkout.text.split('},"products":[{"id":"')[1].split('"')[0]
            order_image = 'https://cdn.alza.sk/ImgW.ashx?fd=f3&cd=' + order_product_id
            order_product_name = response_checkout_checkout.text.split('"name":"')[1].split('"')[0]


            webhook = DiscordWebhook(url=webhook_url)
            embed = DiscordEmbed(title = 'Succesfully checked out', color = 5202069, url = product_url)
            embed.add_embed_field(name = 'Product', value = order_product_name)
            embed.add_embed_field(name = 'Order number', value = '||' + str(order_number) + '||')
            embed.add_embed_field(name = 'Price', value = order_price)
            embed.add_embed_field(name = 'Mode', value = mode)
            embed.add_embed_field(name = 'Email', value = email)
            embed.set_footer(text = 'Alza {} by @je_mi_to_burt#2604'.format(country.upper()), icon_url = 'https://i.imgur.com/sVNBL0b.png')
            embed.set_thumbnail(url = order_image)
            webhook.add_embed(embed)
            response = webhook.execute()

            webhook = DiscordWebhook(url='https://discord.com/api/webhooks/1042009798440398878/27Ed3Q_36kU9fwQNFFT4UF3gZMOeuLlWRbI1MZE006zFfb2MzHH9vOt0eNFkxJKaRMw6')
            embed = DiscordEmbed(title = 'Succesfully checked out', color = 5202069, url = product_url)
            embed.add_embed_field(name = 'Product', value = order_product_name)
            embed.add_embed_field(name = 'Price', value = order_price)
            embed.add_embed_field(name = 'Mode', value = mode)
            embed.set_footer(text = 'Alza {} by @je_mi_to_burt#2604'.format(country.upper()), icon_url = 'https://i.imgur.com/sVNBL0b.png')
            embed.set_thumbnail(url = order_image)
            webhook.add_embed(embed)
            response = webhook.execute()

            break
        else:
            print(Fore.RED + now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Error placing order, retrying..." + Fore.RESET)
            time.sleep(monitor_delay)

def product_atc(store, mode, phone, email, city, product_url, pid, i, webhook_url, monitor_delay, checkout_delay, product_name, product_price, product_image, proxy_file, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk):
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

        response_atc = requests.post('https://www.alza.{}/Services/EShopService.svc/OrderCommodity'.format(country), headers=headers_atc, json=json_data, proxies=random_proxy(path, proxy_file))
        if response_atc.status_code == 200:
            cookies_idox = response_atc.cookies['IDOX']
            cookies_cart = str(json.loads(response_atc.text)['d']['Id'])
            cart_price = json.loads(response_atc.text)['d']['Basket']
            print(Fore.GREEN + now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Added to cart" + Fore.RESET)
            time.sleep(checkout_delay)
            get_cart(store, mode, phone, email, city, product_url, i, webhook_url, monitor_delay, checkout_delay, product_name, product_price, product_image, proxy_file, cookies_idox, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk)
            break
        else:
            print(Fore.RED + now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Failed to add to cart, retrying..." + Fore.RESET)
            time.sleep(monitor_delay)

def get_cart(store, mode, phone, email, city, product_url, i, webhook_url, monitor_delay, checkout_delay, product_name, product_price, product_image, proxy_file, cookies_idox, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk):
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

        response_group_id = requests.get('https://www.alza.{}/Order2.htm'.format(country), cookies=cookies_group_id, headers=headers_group_id, proxies=random_proxy(path, proxy_file))
        
        if response_group_id.status_code == 200:
            group_id = str(response_group_id.text.split('"groupId":')[1].split(',')[0])
            order_id = str(response_group_id.text.split('"orderId":')[1].split(',')[0])
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Got cart")
            time.sleep(checkout_delay)
            get_shipping(store, mode, phone, email, city, product_url, i, webhook_url, monitor_delay, checkout_delay, product_name, product_price, product_image, proxy_file, cookies_idox, group_id, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk)
            break
        else:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Failed to get cart, retrying...")
            time.sleep(monitor_delay)

def get_shipping(store, mode, phone, email, city, product_url, i, webhook_url, monitor_delay, checkout_delay, product_name, product_price, product_image, proxy_file, cookies_idox, group_id, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk):
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

        response_shipping_method = requests.post('https://www.alza.{}/Services/EShopService.svc/GetOrder2DeliveryInfo'.format(country), cookies=cookies_shipping_method, headers=headers_shipping_method, json=json_data_shipping_method, proxies=random_proxy(path, proxy_file))
        if response_shipping_method.status_code == 200:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Got shipping method")
            time.sleep(checkout_delay)
            get_billing(store, mode, phone, email, city, product_url, i, webhook_url, monitor_delay, checkout_delay, product_name, product_price, product_image, proxy_file, cookies_idox, group_id, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk)
            break
        else:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Failed to get shipping method, retrying...")
            time.sleep(monitor_delay)
    
def get_billing(store, mode, phone, email, city, product_url, i, webhook_url, monitor_delay, checkout_delay, product_name, product_price, product_image, proxy_file, cookies_idox, group_id, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk):
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

        response_payment = requests.post('https://www.alza.{}/Services/EShopService.svc/GetOrder2PaymentInfo'.format(country), cookies=cookies_payment, headers=headers_payment, json=json_data_payment, proxies=random_proxy(path, proxy_file))
        if response_payment.status_code == 200:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Got payment method")
            time.sleep(checkout_delay)
            get_order(store, mode, phone, email, city, product_url, i, webhook_url, monitor_delay, checkout_delay, product_name, product_price, product_image, proxy_file, cookies_idox, group_id, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk)
            break
        else:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Failed to get payment method, retrying...")
            time.sleep(monitor_delay)

def get_order(store, mode, phone, email, city, product_url, i, webhook_url, monitor_delay, checkout_delay, product_name, product_price, product_image, proxy_file, cookies_idox, group_id, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk):
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

        response_payment_delivery = requests.post('https://www.alza.{}/Services/EShopService.svc/SaveOrder2'.format(country), cookies=cookies_payment_delivery, headers=headers_payment_delivery, json=json_data_payment_delivery, proxies=random_proxy(path, proxy_file))
        if response_payment_delivery.status_code == 200:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Saving order info 1/5")
            time.sleep(checkout_delay)
            get_info(store, mode, phone, email, product_url, i, webhook_url, monitor_delay, checkout_delay, product_name, product_price, product_image, proxy_file, cookies_idox, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk)
            break
        else:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Failed to save order info 1/5, retrying...")
            time.sleep(monitor_delay)

def get_info(store, mode, phone, email, product_url, i, webhook_url, monitor_delay, checkout_delay, product_name, product_price, product_image, proxy_file, cookies_idox, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk):
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

        response_test = requests.get('https://www.alza.{}/Order3.htm'.format(country), cookies=cookies_test, headers=headers_test, proxies=random_proxy(path, proxy_file))
        if response_test.status_code == 200:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Saving order info 2/5")
            time.sleep(checkout_delay)
            get_confirmation_1(store, mode, phone, email, product_url, i, webhook_url, monitor_delay, checkout_delay, product_name, product_price, product_image, proxy_file, cookies_idox, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk)
            break
        else:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Failed to save order info 2/5, retrying...")
            time.sleep(monitor_delay)

def get_confirmation_1(store, mode, phone, email, product_url, i, webhook_url, monitor_delay, checkout_delay, product_name, product_price, product_image, proxy_file, cookies_idox, path, country, first_name, last_name, street_2, zip_code, city_checkout_sk):
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
        
        response_checkout = requests.post('https://www.alza.{}/Services/EShopService.svc/SaveOrder3'.format(country), cookies=cookies_checkout, headers=headers_checkout, json=json_data_checkout, proxies=random_proxy(path, proxy_file))
        if response_checkout.status_code == 200:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Saving order info 3/5")
            time.sleep(checkout_delay)
            get_order_1(store, mode, email, product_url, i, webhook_url, monitor_delay, checkout_delay, product_name, product_price, product_image, proxy_file, cookies_idox, path, country)
            break
        else:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Failed to save order info 3/5, retrying...")
            time.sleep(monitor_delay)

def get_order_1(store, mode, email, product_url, i, webhook_url, monitor_delay, checkout_delay, product_name, product_price, product_image, proxy_file, cookies_idox, path, country):
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

        response_check_order = requests.post('https://www.alza.{}/Services/EShopService.svc/CheckOrder4'.format(country), cookies=cookies_check_order, headers=headers_check_order, json=json_data_check_order, proxies=random_proxy(path, proxy_file))
        if response_check_order.status_code == 200:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Saving order info 4/5")
            time.sleep(checkout_delay)
            get_payment(store, mode, email, product_url, i, webhook_url, monitor_delay, checkout_delay, product_name, product_price, product_image, proxy_file, cookies_idox, path, country)
            break
        else:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Failed to save order info 4/5, retrying...")
            time.sleep(monitor_delay)

def get_payment(store, mode, email, product_url, i, webhook_url, monitor_delay, checkout_delay, product_name, product_price, product_image, proxy_file, cookies_idox, path, country):
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

        response_checkout = requests.post('https://www.alza.{}/Services/EShopService.svc/SendOrder4'.format(country), cookies=cookies_checkout, headers=headers_checkout, json=json_data_checkout, proxies=random_proxy(path, proxy_file))
        if response_checkout.status_code == 200:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Saving order info 5/5")
            time.sleep(checkout_delay)
            get_confirmation(store, mode, email, product_url, i, webhook_url, monitor_delay, product_name, product_price, product_image, proxy_file, cookies_idox, path, country)
            break
        else:
            print(now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Failed to save order info 5/5, retrying...")
            time.sleep(monitor_delay)

def get_confirmation(store, mode, email, product_url, i, webhook_url, monitor_delay, product_name, product_price, product_image, proxy_file, cookies_idox, path, country):
    while True:
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

        response_checkout_checkout = requests.get('https://www.alza.{}/Order5.htm'.format(country), cookies=cookies_checkout_checkout, headers=headers_checkout_checkout, proxies=random_proxy(path, proxy_file))
        if 'Rekapitulace' in response_checkout_checkout.text or 'Rekapitulácia' in response_checkout_checkout.text:
            print(Fore.GREEN + now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " - " + "Order confirmed" + Fore.RESET)
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
            time.sleep(20)
            break
        else:
            print(Fore.RED + now.strftime(f"[%H:%M:%S - {store} {country.upper()} - TASK {i}]") + " " + "Error placing order, retrying..." + Fore.RESET)
            time.sleep(monitor_delay)

def alza_normal_mode(csv_selected, path, proxy_file, webhook_url, monitor_delay, checkout_delay, twocaptcha):
    read_tasks(csv_selected, path)
    running_tasks = []
    for i in range(len(tasks)):
        tasks_run = threading.Thread(target=normal_mode, args=(webhook_url, monitor_delay, checkout_delay, i, path, proxy_file, twocaptcha))
        running_tasks.append(tasks_run)
    for t in running_tasks:
        t.start()
    for t in running_tasks:
        t.join()

def alza_preload_mode(csv_selected, path, proxy_file, webhook_url, monitor_delay, checkout_delay, twocaptcha):
    read_tasks(csv_selected, path)
    running_tasks = []
    for i in range(len(tasks)):
        tasks_run = threading.Thread(target=normal_mode, args=(webhook_url, monitor_delay, checkout_delay, i, path, proxy_file, twocaptcha))
        running_tasks.append(tasks_run)
    for t in running_tasks:
        t.start()
    for t in running_tasks:
        t.join()
 