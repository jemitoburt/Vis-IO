import os
from csv import DictReader
import time
import json
import requests
from Bot_modules.Nay_module import nay_instore_mode, nay_normal_mode
from Bot_modules.Buzz_module import buzz_mode
from Bot_modules.Alza_module import alza_normal_mode
from Bot_modules.TheStreets_module import the_streets
from Bot_modules.Queens_module import queens
from Bot_modules.Popname_module import popname
from pypresence import Presence

try:
    start_time = time.time()
    RPC = Presence('1041623162934267934')
    RPC.connect()
    RPC.update(details='Shhhh',large_image='vis_io_logo',start=start_time)
except BaseException:
    pass



path = os.getcwd()
files = os.listdir(path)

def info_check(path):
    read = open(path + '/config.json')
    settingsJson = json.load(read)
    webhook_url = settingsJson['webhook_url']
    if webhook_url == '':
        print('Please fill webhook_url in config.json')
        time.sleep(5)
        exit()
    monitor_delay = int(settingsJson['monitor_delay'])/1000
    if monitor_delay == '':
        print('Please fill monitor_delay in config.json')
        time.sleep(5)
        exit()
    checkout_delay = int(settingsJson['checkout_delay'])/1000
    if checkout_delay == '':
        print('Please fill checkout_delay in config.json')
        time.sleep(5)
        exit()
    twocaptcha = settingsJson['2captcha_key']
    if twocaptcha == '':
        print('Please fill 2captcha_key in config.json')
        time.sleep(5)
        exit()
    license_key = settingsJson['license_key']
    if license_key == '':
        print('Please fill license_key in config.json')
        time.sleep(5)
        exit()
    return webhook_url, monitor_delay, checkout_delay, twocaptcha, license_key

webhook_url, monitor_delay, checkout_delay, twocaptcha, license_key = info_check(path)

os.system('title "Vis IO 1.1.4 | Running: 0 tasks | Carts: 0 | Successful checkouts: 0 | Failed checkouts: 0 | Monitor delay: ' + str(monitor_delay*1000).split('.')[0] + ' | Checkout delay: ' + str(checkout_delay*1000).split('.')[0] + '"')



def validate_key(license_key):
    url = "https://api.whop.com/api/v1/licenses/{}/validate".format(license_key)
    payload = {"metadata": {}}
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "Bearer OWVlMmQ3NzY1MzdlMjg5MjY3OTU3ZDI2ZGM0OGY0OGRhODhmOWJmZTg4OjdMWUJZSzluenZicWVKYWlTbGZzeU1IdVYySEZUZTRqU2ZhWnpKbVZRVk0="
    }
    response = requests.post(url, json=payload, headers=headers).text
    if 'Please reset your key to use on a new machine' in response:
        print('Please reset your key to use on a new machine!')
        input('Press enter to exit')
    else:
        key_valid = json.loads(response)['valid']
        if key_valid == True:
            status = True
            return status
        elif key_valid == False:
            status = False
            return status

status = validate_key(license_key)

if status == False:
    exit()
else:
    print('License is valid, build 1.1.4\n')

    csvs = {}
    i = 1
    for file in files:
        if file.endswith(".csv"):
            csvs[i] = file
            print(str(i) +' - '+ file)
            i += 1

    csv_select = int(input("Select a csv file you want to run: "))
    csv_selected = csvs[csv_select]
    with open (path + "/" + csv_selected, "r") as read_obj:
            csv_dict_reader = DictReader(read_obj)
            for row in csv_dict_reader:
                store_selected = str(row['store'])
                proxy_file = str(row['proxy_file'])
                if store_selected == "NAY":
                    run_tasks = int(input('1 - Start tasks\n2 - Overwrite url in csv\nSelect option: '))
                    if run_tasks == 1:
                        url = None
                        with open (path + "/" + csv_selected, "r") as read_mode:
                            csv_dict_reader = DictReader(read_mode)
                            for row in csv_dict_reader:
                                mode_selected = row['mode']
                            if mode_selected == "INSTORE":
                                print('Starting INSTORE MODE')
                                nay_instore_mode(url, csv_selected, path, proxy_file, webhook_url, monitor_delay, checkout_delay)
                            elif mode_selected == "NORMAL":
                                print('Starting NORMAL MODE')
                                nay_normal_mode(url, csv_selected, path, proxy_file, webhook_url, monitor_delay, checkout_delay)
                            elif mode_selected != "INSTORE" or mode_selected != "NORMAL":
                                print('Selected mode doesnt exit')
                            
                    elif run_tasks == 2:
                        url = input('Enter url: ')
                        with open (path + "/" + csv_selected, "r") as read_mode:
                            csv_dict_reader = DictReader(read_mode)
                            for row in csv_dict_reader:
                                mode_selected = row['mode']
                            if mode_selected == "INSTORE":
                                print('Starting INSTORE MODE')
                                nay_instore_mode(url, csv_selected, path, proxy_file, webhook_url, monitor_delay, checkout_delay)
                            elif mode_selected == "NORMAL":
                                print('Starting NORMAL MODE')
                                nay_normal_mode(url, csv_selected, path, proxy_file, webhook_url, monitor_delay, checkout_delay)
                            elif mode_selected != "INSTORE" or mode_selected != "NORMAL":
                                print('Selected mode doesnt exit')


                if store_selected == "BUZZ":
                    run_tasks = int(input('1 - Start tasks\n2 - Overwrite url in csv\nSelect option: '))
                    if run_tasks == 1:
                        url = None
                        with open (path + "/" + csv_selected, "r") as read_mode:
                            csv_dict_reader = DictReader(read_mode)
                            for row in csv_dict_reader:
                                mode_selected = row['mode']
                            if mode_selected == "NORMAL":
                                print('Starting NORMAL MODE')
                                buzz_mode(url, csv_selected, path, proxy_file, webhook_url, monitor_delay, checkout_delay)
                            elif mode_selected != "NORMAL":
                                print('Selected mode doesnt exit')
                                

                    elif run_tasks == 2:
                        url = input('Enter url: ')
                        with open (path + "/" + csv_selected, "r") as read_mode:
                            csv_dict_reader = DictReader(read_mode)
                            for row in csv_dict_reader:
                                mode_selected = row['mode']
                            if mode_selected == "NORMAL":
                                print('Starting NORMAL MODE')
                                buzz_mode(url, csv_selected, path, proxy_file, webhook_url, monitor_delay, checkout_delay)
                            elif mode_selected != "NORMAL":
                                print('Selected mode doesnt exit')
                            
                if store_selected == "ALZA":
                    run_tasks = int(input('1 - Start tasks\n2 - Overwrite url in csv\nSelect option: '))
                    if run_tasks == 1:
                        url = None
                        with open (path + "/" + csv_selected, "r") as read_mode:
                            csv_dict_reader = DictReader(read_mode)
                            for row in csv_dict_reader:
                                mode_selected = row['mode']
                            if mode_selected == "NORMAL":
                                print('Starting NORMAL MODE')
                                alza_normal_mode(url, csv_selected, path, proxy_file, webhook_url, monitor_delay, checkout_delay, twocaptcha)
                            elif mode_selected == "PRELOAD":
                                print('Starting PRELOAD MODE')
                                alza_normal_mode(url, csv_selected, path, proxy_file, webhook_url, monitor_delay, checkout_delay, twocaptcha)
                            elif mode_selected != "NORMAL" or mode_selected != "PRELOAD":
                                print('Selected mode doesnt exit')

                    elif run_tasks == 2:
                        url = input('Enter url: ')
                        with open (path + "/" + csv_selected, "r") as read_mode:
                            csv_dict_reader = DictReader(read_mode)
                            for row in csv_dict_reader:
                                mode_selected = row['mode']
                            if mode_selected == "NORMAL":
                                print('Starting NORMAL MODE')
                                alza_normal_mode(url, csv_selected, path, proxy_file, webhook_url, monitor_delay, checkout_delay, twocaptcha)
                            elif mode_selected == "PRELOAD":
                                print('Starting PRELOAD MODE')
                                alza_normal_mode(url, csv_selected, path, proxy_file, webhook_url, monitor_delay, checkout_delay, twocaptcha)
                            elif mode_selected != "NORMAL" or mode_selected != "PRELOAD":
                                print('Selected mode doesnt exit')
                
                if store_selected == "THESTREETS":
                    run_tasks = int(input('1 - Start tasks\n2 - Overwrite url in csv\nSelect option: '))
                    if run_tasks == 1:
                        url = None
                        with open (path + "/" + csv_selected, "r") as read_mode:
                            csv_dict_reader = DictReader(read_mode)
                            for row in csv_dict_reader:
                                mode_selected = row['mode']
                            if mode_selected == "NORMAL":
                                print('Starting NORMAL MODE')
                                the_streets(url, csv_selected, path, proxy_file, webhook_url, monitor_delay, checkout_delay, twocaptcha)
                            elif mode_selected != "NORMAL":
                                print('Selected mode doesnt exit')
                    
                    elif run_tasks == 2:
                        url = input('Enter url: ')
                        with open (path + "/" + csv_selected, "r") as read_mode:
                            csv_dict_reader = DictReader(read_mode)
                            for row in csv_dict_reader:
                                mode_selected = row['mode']
                            if mode_selected == "NORMAL":
                                print('Starting NORMAL MODE')
                                the_streets(url ,csv_selected, path, proxy_file, webhook_url, monitor_delay, checkout_delay, twocaptcha)
                            elif mode_selected != "NORMAL":
                                print('Selected mode doesnt exit')
                
                if store_selected == "QUEENS":
                    run_tasks = int(input('1 - Start tasks\n2 - Overwrite url in csv\nSelect option: '))
                    if run_tasks == 1:
                        url = None
                        with open (path + "/" + csv_selected, "r") as read_mode:
                            csv_dict_reader = DictReader(read_mode)
                            for row in csv_dict_reader:
                                mode_selected = row['mode']
                            if mode_selected == "NORMAL":
                                print('Starting NORMAL MODE')
                                queens(url, csv_selected, path, proxy_file, webhook_url, monitor_delay, checkout_delay, twocaptcha)
                            elif mode_selected == "PICKUP":
                                print('Starting PICKUP MODE')
                                queens(url, csv_selected, path, proxy_file, webhook_url, monitor_delay, checkout_delay, twocaptcha)
                            elif mode_selected != "NORMAL" or mode_selected != "PICKUP":
                                print('Selected mode doesnt exit')
                    
                    elif run_tasks == 2:
                        checkout_delay = 0
                        monitor_delay = 0
                        url = input('Enter url: ')
                        with open (path + "/" + csv_selected, "r") as read_mode:
                            csv_dict_reader = DictReader(read_mode)
                            for row in csv_dict_reader:
                                mode_selected = row['mode']
                            if mode_selected == "NORMAL":
                                print('Starting NORMAL MODE')
                                queens(url, csv_selected, path, proxy_file, webhook_url, monitor_delay, checkout_delay, twocaptcha)
                            elif mode_selected == "PICKUP":
                                print('Starting PICKUP MODE')
                                queens(url, csv_selected, path, proxy_file, webhook_url, monitor_delay, checkout_delay, twocaptcha)
                            elif mode_selected != "NORMAL" or mode_selected != "PICKUP":
                                print('Selected mode doesnt exit')
                
                if store_selected == "POPNAME":
                    run_tasks = int(input('1 - Start tasks\nSelect option: '))
                    if run_tasks == 1:
                        url = None
                        with open (path + "/" + csv_selected, "r") as read_mode:
                            csv_dict_reader = DictReader(read_mode)
                            for row in csv_dict_reader:
                                mode_selected = row['mode']
                            if mode_selected == "RAFFLE":
                                print('Starting RAFFLE MODE')
                                popname(url, csv_selected, path, proxy_file, webhook_url, monitor_delay, checkout_delay, twocaptcha)
                    
