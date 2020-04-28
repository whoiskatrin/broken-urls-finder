import json
import os
import ssl
import traceback
import urllib
from urllib.parse import urlparse, urlsplit
from urllib.request import urlopen

import requests
import validators as validators
from bs4 import BeautifulSoup

brokenLinks = {}
slack_alert_webhook = os.environ.get('SLACK_WEBHOOK')


def send_slack_notification(msg):
    try:
        requests.post(
            slack_alert_webhook,
            data=json.dumps({'text': msg}),
            headers={'Content-Type': 'application/json'}
        )
    except Exception as e:
        print("type error: " + str(e))
        print(traceback.format_exc())


def checkKeyValuePairExistence(dic, key, value):
    try:
        return dic[key] == value
    except KeyError:
        return False


def uri_validator(x):
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc, result.path])
    except:
        return False


def crawl(args):
    for arg in args:
        links = []
        ssl._create_default_https_context = ssl._create_unverified_context
        html_page = urllib.request.urlopen(arg)
        soup = BeautifulSoup(html_page, features="html.parser")
        for link in soup.findAll("a"):
            href = link.get("href")
            if href is None:
                continue
            if 'https' in href:
                links.append(href)
                continue
            if 'http' in href:
                links.append(href)
                continue
            if href.startswith("/"):
                base_url = "{0.scheme}://{0.netloc}".format(urlsplit(arg))
                links.append(base_url + href)
                continue
        links = list(dict.fromkeys(links))
        for link in links:
            valid = validators.url(link)
            if valid is False:
                links.remove(link)

        final_links = []
        for img in soup.findAll("img"):
            src = img.get("src")
            final_links.append(src)
        for data in final_links:
            if 'data' in data:
                continue
            links.append(data)
        for script in soup.findAll("script"):
            script_src = script.get("src")
            if script_src is not None:
                links.append(script_src)
        for link in soup.findAll("link"):
            href = link.get("href")
            link.append(href)
        for link in links:
            try:
                response = requests.get(link)
                status = response.status_code
                if status != 200 and status != 999 and status != 403 and checkKeyValuePairExistence(brokenLinks,
                                                                                                    arg,
                                                                                                    link) is False:
                    brokenLinks[arg] = link
                    send_slack_notification(f'Status code: [{status}] {link} found on {arg}')
            except requests.exceptions.MissingSchema:
                # skip if not a normal image file
                continue
    if brokenLinks:
        send_slack_notification('Please, create bugs in Jira for all the issues in the morning!')
    else:
        send_slack_notification('We don\'t have any broken links. What a day folks! :champagne:')

crawl(["https://github.com/whoiskatrin"])
