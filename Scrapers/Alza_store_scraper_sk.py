import requests
import json

headers = {
    'Host': 'www.alza.sk',
    'accept': 'application/json, text/plain, */*',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'accept-language': 'sk-SK',
    'referer': 'https://www.alza.sk/Order2.htm',
}

response = json.loads(requests.get('https://www.alza.sk/api/personalPickup/v1/places?types[0]=2&latitude=50.0766&longitude=14.5148&orderId=1494414844&groupId=145966348&ordering=0&radius=1000000&limit=20&offset=0', headers=headers).text)['pickupPlaces']['value']

stores = {}
for i in response:
    stores[i['name']] = i['addressText'].split(',')[0]

    

print(stores)
