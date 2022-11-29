from twocaptcha import TwoCaptcha
import os
import requests
import time

twocaptcha_key = '39cbcc4131c32b08ac498b27baf6bb63'

url_page = 'https://www.alza.sk/'

response_page= requests.get(url_page, allow_redirects=True)
print(response_page.url)
if 'captcha' in response_page.url:
    
    captcha_token = response_page.text.split('data-sitekey=')[1].split(' data-callback')[0]
    print('"' + captcha_token + '"')



    url_captcha = requests.get('http://2captcha.com/in.php?key=' + twocaptcha_key + '&method=userrecaptcha&googlekey=' + captcha_token + '&pageurl=' + response_page.url).text.split('|')[1]

    captcha_solved = requests.get('http://2captcha.com/res.php?key=' + twocaptcha_key + '&action=get&id=' + url_captcha).text

    
    while 'CAPCHA_NOT_READY' in captcha_solved:
        time.sleep(5)
        captcha_solved = requests.get('http://2captcha.com/res.php?key=' + twocaptcha_key + '&action=get&id=' + url_captcha).text
        if 'OK' in captcha_solved:
            print('Captcha solved')
            captcha_solved_token = captcha_solved.split('|')[1]
            print(captcha_solved_token)
            break
        else:
            print('Waiting for captcha')

    headers = {
        'Host': 'www.alza.sk',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
        'accept-language': 'cs',
        'referer': response_page.url,
    }

    response = requests.get("https://www.alza.sk/captcha/verify?solution={}&ssa=https://www.alza.sk/".format(captcha_solved_token), headers=headers, allow_redirects=True)
    print(response.url)
    print('Got product page')
    export = open('Test.txt', 'w')
    export.write(response.text)
    export.close()

else:
    print('No captcha')

#https://www.alza.sk/captcha/verify?solution=03AEkXODC3g2gbh8IH2ZjwVJu8SHgRTyMuPerYjpMchPoxscUIPvBmpVIa4eZuX_KBW3E-RFewCcI6PIW_fncz4Q4DLeW4scacFF_rUkuAXYZgBOFwXJSvUQQjkL8vge0biovjPUCYGojT99Pf_yMK39LWUCxgJaU3SX51idBgS9kui5HMM3PpM9wcR6Nmv2ya1meWRpXB1B0rwVyXflJH5j5GHqdaMlY4Y5x952tWZoljdWNcpPQIuHWdQazeyL8kKranSb5DLJ914ucPrh9ijP8RPniWBj8IlzdnRDDOuWOIWrj1WtLKqwgr7xh8DzN9fO8sMK_lBC6bmtGNrxR24YcLX36GMNFlPOD4BFdItc366KlAndRqLSYd1Jf19mUUwXTLKtSEKG1sGtOjevX69SitygF64eK4tXfkgtsHohJHVjvfZS1hojLmBqQIUj7IqBprvIQetUEjANqEZEsKtpNii4R_f6oQtQI_3G46Kdv_azhXdBanUc27sN4i-tkW7r04bVc3rNESf930ragcolAx5ubWN_EtIA&ssa=https%253A%252F%252Fwww.alza.sk%252F

#http://2captcha.com/in.php?key=39cbcc4131c32b08ac498b27baf6bb63&method=userrecaptcha&googlekey=6Lcnh7QZAAAAALnwVTDDYkKRqfeApOwhdtlN4NYh&pageurl=https://www.alza.cz/captcha/captcha?ssa=https%3A%2F%2Fwww.alza.cz%2Fphilips-hue-lightstrip-plus-v4-lightstrip-plus-v4-extension-d7471010.htm&ssb=c4f9d5587bad518c00f6ba8ecc8ca8a304dae7e5&ssc=ZjVlMjMzNDlhYjExLTA0ZGEtMzJmNC05M2NhLTE0YWQxMTY2#

#http://2captcha.com/res.php?key=39cbcc4131c32b08ac498b27baf6bb63&action=get&id=72038803206

