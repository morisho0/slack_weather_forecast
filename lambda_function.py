#!/usr/bin/env python

import time # for sleep
import os   # for path
import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import requests
import commands
from PIL import Image
from io import BytesIO

def lambda_handler(event, context):
    main()

def set_font():
    os.environ['HOME'] = os.environ['LAMBDA_TASK_ROOT']

def get_weather():
    url = 'http://www.jma.go.jp/jp/yoho/319.html'
    user_agent = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36")

    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = user_agent
    dcap["phantomjs.page.settings.javascriptEnabled"] = True

    browser = webdriver.PhantomJS(service_log_path=os.path.devnull, executable_path="/var/task/phantomjs", service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any'], desired_capabilities=dcap)
    browser.set_window_size(600, 300)
    browser.get(url)
    browser.execute_script('window.scrollTo(10, 380);')
    time.sleep(1)
    browser.save_screenshot('/tmp/weather.png')
    browser.quit()

def crop_image():
    data = open('/tmp/weather.png', 'rb').read()
    Image.open(BytesIO(data)).crop((13, 264, 611, 545)).save('/tmp/weather.png')

def post_to_slack(token, channel):
    data = open('/tmp/weather.png', 'rb').read()
    files = {'file': ('weather.png', data, 'image/png')}
    params = {'token':token, 'channels':channel, 'text': '天気予報です'}
    res = requests.post("https://slack.com/api/files.upload", files=files, params=params)

def main():
    set_font()
    get_weather()
    crop_image()
    token = os.environ['SLACK_API_TOKEN']
    channel = os.environ['SLACK_CHANNEL_ID']
    post_to_slack(token, channel)

if __name__ == '__main__':
    main()
