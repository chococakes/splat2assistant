import os
import json
import requests
import time
import webbrowser
import logging

headers = {
    'Host': 'app.splatoon2.nintendo.net',
    'x-unique-id': '32449507786579989234',
    'x-requested-with': 'XMLHttpRequest',
    'x-timezone-offset': '0',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 7.1.2; Pixel Build/NJH47D; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/59.0.3071.125 Mobile Safari/537.36',
    'Accept': '*/*',
    'Referer': 'https://app.splatoon2.nintendo.net/home',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US'
}

def buy_merchandise(cookie, id):
    head = {
       'Host': 'app.splatoon2.nintendo.net',
       'User-Agent': 'Mozilla/5.0 (Linux; Android 7.1.2; Pixel Build/NJH47D; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/59.0.3071.125 Mobile Safari/537.36',
       'Accept': '*/*',
       'x-requested-with': 'XMLHttpRequest',
       'Referer': 'https://app.splatoon2.nintendo.net/home',
       'x-unique-id': '14054327066438149574',
       'x-timezone-offset': '0',
       'Accept-Encoding': 'gzip, deflate',
       'Accept-Language': 'en-US'
    }
    r = requests.post('https://app.splatoon2.nintendo.net/api/onlineshop/order/{0}'.format(str(id)), headers=head, cookies=dict(iksm_session=cookie), data={'override': '1'})
    return json.loads(r.text)

def get_battle_data(cookie):
    logger = logging.getLogger('splathelper')
    url = "https://app.splatoon2.nintendo.net/api/results"
    results = requests.get(url, headers=headers, cookies=dict(iksm_session=cookie))
    try:
        # If this fails with a KeyError, the iksm_session is expired.
        data = json.loads(results.text)['results']
    except KeyError:
        logger.error('Cookie is invalid or expired.')
        cookie = get_cookie()
    return json.loads(results.text)

def get_individual_battle_data(cookie, number):
    url = "https://app.splatoon2.nintendo.net/api/results/{0}".format(str(number))
    results = requests.get(url, headers=headers, cookies=dict(iksm_session=cookie))
    return json.loads(results.text)
