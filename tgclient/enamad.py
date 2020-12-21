# -*- coding: utf-8 -*-
from client import *
import redis
import re
import urllib.request as ur
import json
import urllib
import random
from bs4 import BeautifulSoup
import requests
import sys

r = redis.StrictRedis(host='localhost', port=6379, db=3, decode_responses=True)
token = "563331913:AAHeyQNhYKv58w37BPwswWxRW6n9zI2PJaU"
bot = TelegramBot(token, True)
sudo = [463152143]


def enamad(website):
    header = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"
    }
    cookies = requests.get('https://enamad.ir', headers=header)

    soup = BeautifulSoup(cookies.content, 'html.parser')
    token = soup.find('input', {'name': '__RequestVerificationToken'})['value']
    req = requests.post("https://enamad.ir/Home/GetData", headers=header,
                        data={'domain': website, '__RequestVerificationToken': token}, cookies=cookies.cookies)
    return req.text


def info(website):
    header = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"
    }
    site = requests.get('http://{}'.format(website), headers=header)
    soup2 = BeautifulSoup(site.content, 'html.parser')
    e = soup2.find('img', {'style': 'cursor:pointer'})['onclick'].split('window.open("')[1].split('", "Popup"')[0]
    header2 = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0',
        'Referer': 'https://www.{}/'.format(website)
    }
    req3 = requests.get(e, headers=header2)
    soup3 = BeautifulSoup(req3.content, 'html.parser')
    address = soup3.find('td', {'id': 'td_address'}).get_text()
    tel = soup3.find('td', {'id': 'td_tel'}).get_text()
    email = soup3.find('td', {'id': 'td_email'}).get_text()

    data = {
        'address': address,
        'tel': tel,
        'email': email
    }
    return data


@bot.command(r'^/start$')
def start_message(message):
    chat_id = message['chat']['id']
    r.sadd('enamadbot', chat_id)
    msg = '''سلام دوست عزیز 👋🏻

به ربات وبسایت نماد اعتماد الكترونیكی خوش آمدید🙏🏻

این ربات جهت نمایش اطلاعات نماد سایت ها میباشد و مستقیما از سایت e نماد اطلاعات را دریافت میکند

📍این ربات به سفارش وبسایت تلسکم نوشته شده است(telescam.info)
👨‍💻برنامه نویس : SeYeD :) @ITMKH

برای ادامه کار اسم وبسایت را وارد کنید...


'''
    bot.sendMessage(chat_id, msg)


@bot.message('text')
def message_text(message):
    chat_id = message['chat']['id']
    text = message['text']
    start = re.compile('start')
    if not start.search(text):
        try:
            urls = text.split("//")[-1].split("www.")[-1].split("/")[0].split(":")[0].split('?')[0]
            links = re.findall("[a-z-A-Z-0-9]*\.[a-z-A-Z-0-9]*", urls)
            for x in links:
                data = json.loads(enamad(x))
                if data['domain'] == None:
                    r.sadd('scan_bad', x)
                    bot.sendMessage(chat_id, 'دامنه در e نماد یافت نشد ❌')
                else:
                    r.sadd('scan_good', x)
                    msg = '''
🌐 مشخصات دامنه {} به شرح زیر است :

📝 عنوان : {}

🗓 تاریخ شروع : {}

📆 تاریخ انقضاء : {}

🏘 استان : {}

🏡 شهر : {}

🔖 ایدی وبسایت : {}


👤مشخصات کاربر :

📝نام : {}

🔖ایدی کاربری : {}

✏️نام کاربری : {}


این وبسایت دارای نماد اعتماد الكترونیكی {} ستاره است
'''.format(data['domain'], data['nameper'], data['approvedate'], data['expdate'],
           data['stateTitle'], data['cityTitle'], data['id'], data['nameUser'], data['userid'],
           data['userText'], int(data['logolevel']) * '🌟')
                    bot.sendMessage(chat_id, msg, reply_markup={
            'inline_keyboard': [
                [
                    {'text': '💡 اطلاعات بیشتر', 'callback_data': '/info {}'.format(text)}
                ]
            ]
        })
        except Exception as e:
            print(e)


@bot.command(r'^/stats')
def statsbot(message):
    if message['from']['id'] in sudo:
        text = '''👥 تعداد اعضا : {}

✅ سایت های ثبت شده : {}

❌ سایت های ثبت نشده : {}
'''.format(r.scard('enamadbot'), r.scard('scan_good'), r.scard('scan_bad'))
        bot.sendMessage(message['chat']['id'], text)


@bot.callback_query()
def call(message):
    chat_id = message['message']['chat']['id']
    site = message['data'].replace('/info ', '')
    data = info(site)
    msg = '''🏘 آدرس : {}

📞 تلفن : {}

📧 ایمیل : {}
'''.format(data['address'], data['tel'], data['email'])
    bot.sendMessage(chat_id, msg)


bot.run(False)