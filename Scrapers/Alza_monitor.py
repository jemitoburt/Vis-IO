import requests
import json
import unicodedata
import time
from discord_webhook import DiscordWebhook, DiscordEmbed
from colorama import Fore, init
init(convert=True)
from datetime import datetime
import threading

country_list = ['cz', 'sk']

def get_initial_info(country):
    initial_info = []
    headers = {
        'accept': '*/*',
        'content-type': 'application/json',
        'country': '{}'.format(country),
        'user-agent': 'Alza/105.0 (cz.juicymo.contracts.ios.Alza-01; build:202211011057; iOS 16.1.1) Alamofire/5.2.1',
    }

    params = {
        'country': '{}'.format(country),
        'density': '2.0',
    }
    data = '{"filterParameters":{"typeId":0,"producers":[],"wearType":0,"id":"18876712","availabilityType":0,"sendPrices":true,"params":[],"type":"CATEGORY","page":1,"orderBy":0,"newsOnly":false}}'
    response = json.loads(requests.post('https://www.alza.{}/Services/RestService.svc/v2/products'.format(country), headers=headers, params=params, data=data).text)['data']
    for data in response:
        product_availabitily = unicodedata.normalize("NFKD",data['avail'])
        product_price = str(data['price'])
        if product_price == 'None':
            product_price = '0 Kč'
        product_price_clean = unicodedata.normalize("NFKD", product_price)
        product_image = data['img']
        product_name = data['name']
        product_url = data['url']
    
        initial_append = product_name + ' - ' + product_image + ' - ' + product_url + ' - ' + product_availabitily + ' - ' + product_price_clean
        initial_info.append(initial_append)
    return initial_info

def monitor_info(initial_info, country):
    while True:
        now = datetime.now()
        monitor_info = []
        headers = {
            'accept': '*/*',
            'content-type': 'application/json',
            'country': '{}'.format(country),
            'user-agent': 'Alza/105.0 (cz.juicymo.contracts.ios.Alza-01; build:202211011057; iOS 16.1.1) Alamofire/5.2.1',
        }

        params = {
            'country': '{}'.format(country),
            'density': '2.0',
        }
        data = '{"filterParameters":{"typeId":0,"producers":[],"wearType":0,"id":"18876712","availabilityType":0,"sendPrices":true,"params":[],"type":"CATEGORY","page":1,"orderBy":0,"newsOnly":false}}'
        response = json.loads(requests.post('https://www.alza.{}/Services/RestService.svc/v2/products'.format(country), headers=headers, params=params, data=data).text)['data']
        for data in response:
            product_availabitily = unicodedata.normalize("NFKD",data['avail'])
            product_price = str(data['price'])
            if product_price == 'None':
                product_price = '0 Kč'
            product_price_clean = unicodedata.normalize("NFKD", product_price)
            product_image = data['img']
            product_name = data['name']
            product_url = data['url']

            monitor_append = product_name + ' - ' + product_image + ' - ' + product_url + ' - ' + product_availabitily + ' - ' + product_price_clean
            monitor_info.append(monitor_append)
        

        if monitor_info != initial_info:
            for data in monitor_info:
                if data not in initial_info:
                    print(Fore.GREEN + now.strftime("[%H:%M:%S]") + ' Site changed' + Fore.RESET)
                    product_image = data.split(' - ')[1].split(' - ')[0]
                    product_url = data.split(' - ')[2].split(' - ')[0]
                    product_availabitily = data.split(' - ')[3].split(' - ')[0]
                    product_price = data.split(' - ')[4].split(' - ')[0]
                    product_name = data.split(' - ')[0]
                    webhook = DiscordWebhook(url = 'https://discord.com/api/webhooks/871162998507589632/9lDYhpCYjVwJcG0Yfc5Q1lEU445zYmaGBVYpoJNIGPglfhAo9owZxCDf7YJC08CxidUn')
                    embed = DiscordEmbed(title = product_name, color = 000000, url = product_url)
                    embed.add_embed_field(name = 'Availability', value = product_availabitily)
                    embed.add_embed_field(name = 'Price', value = product_price)
                    embed.add_embed_field(name = 'Country', value = country.upper())
                    embed.set_thumbnail(url = product_image)
                    webhook.add_embed(embed)
                    response = webhook.execute()
                    initial_info = monitor_info
                    print('Initial info - ' + str(initial_info))
                    time.sleep(15)
            
        else:
            print(now.strftime("[%H:%M:%S]") + ' Alza {} - '.format(country.upper()) + 'Waiting for change')
            time.sleep(15)

def monitor(country):
    initial_info = get_initial_info(country)
    monitor_info(initial_info, country)


def run_monitor():
    running_tasks = []
    for country in country_list:
        tasks_run = threading.Thread(target=monitor, args=(country,))
        running_tasks.append(tasks_run)
    for task in running_tasks:
        task.start()
    for task in running_tasks:
        task.join()
    
run_monitor()