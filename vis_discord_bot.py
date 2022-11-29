import requests
import discord
import json
from discord import SelectOption, option
import datetime, colorama
from colorama import Fore, init
init(convert=True)
import random
import os
import dateutil.parser as dp

###############################################
#       / ___/ _ \| \ | |  ___|_ _/ ___|      #
#      | |  | | | |  \| | |_   | | |  _       #
#      | |__| |_| | |\  |  _|  | | |_| |      #
#       \____\___/|_| \_|_|   |___\____|      #
###############################################

bot_token = "MTA0MTYyMzE2MjkzNDI2NzkzNA.GEEKBj.h6MI0NFgdK_Tn0y4rnnMMBxGBqJyEkZpuOAB8k"
#server_whitelist = 1041623067710984243,781901610753982504
banner = (f'''{Fore.RED}
  _____                _       
 |  __ \              | |      
 | |__) |___  __ _  __| |_   _ 
 |  _  // _ \/ _` |/ _` | | | |
 | | \ \  __/ (_| | (_| | |_| |
 |_|  \_\___|\__,_|\__,_|\__, |
                          __/ |
                         |___/ 

{Fore.RESET}
{Fore.GREEN}
SNKRS Destroy
{Fore.RESET}''')

###############################################

client = discord.Bot()

@client.event
async def on_ready():
    print(banner)

""" BUZZ OP MODE SEARCH CITY """
@client.slash_command(description="Buzz OP MODE SEARCH CITY")
@option('country', description = 'Select country', choices = ['CZ', 'SK'])
@option('city', description = 'Enter city')
@option('zip', description = 'Enter zip code')
async def buzz_op_mode_search_city(ctx: discord.ApplicationContext, country: str, city: str, zip:str):
    if country == 'CZ':
        headers = {
            'Host': 'www.buzzsneakers.cz',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'Referer': 'https://www.buzzsneakers.cz/kosik',
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
        
        url = 'https://www.buzzsneakers.cz/kosik'

        if ' ' in zip:
            zip = zip.replace(' ', '')
        response_str = requests.get(url, params=params, headers=headers).text
        json_str = json.loads(response_str)['list']
        for data in json_str:
            if zip in data['postCode']:
                await ctx.respond('**Enter this values to `Buzz_config.json`**\n\ncity_name: ' + '`' + data['name'] + '`\nzip_order :' + '`' + data['postCode'] + '`\ncity_order :' + '`' + data['cityId'] + '`')

    if country == 'SK': 
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
        for data in response_str:
            if zip in data['postCode']:
                await ctx.respond('**Enter this values to `Buzz_config.json`**\n\ncity_name: ' + '`' + data['name'] + '`\nzip_order :' + '`' + data['postCode'] + '`\ncity_order :' + '`' + data['cityId'] + '`')

""" BUZZ SIZE CHECKER """
@client.slash_command(description="Buzz size checker")
@option('product_url', description = 'Enter product url')
async def buzz_size_checker(ctx: discord.ApplicationContext, product_url: str):
    response = requests.get(product_url)
    sizes_str = response.text.split('<ul class="product-attributes list-inline product-attributes-two-sizes">')[1].split('</ul>')[0].split('<li')
    size = ''
    m = 2
    while m < len(sizes_str):
        size += sizes_str[m].split('"original-size">')[1].split('<')[0] + '\n'
        m += 1
    if size == '':
        m = 1
        while m < len(sizes_str):
            size += sizes_str[m].split('"original-size">')[1].split('<')[0] + '\n'
            m += 1

    await ctx.respond('**Available sizes:**\n\n' + size)

client.run(bot_token)