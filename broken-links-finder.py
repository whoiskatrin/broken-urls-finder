import json
import os
import ssl
import traceback
import urllib
from urllib.parse import urlparse, urlsplit, urljoin
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


def check_key_value_pair_existence(dic, key, value):
    try:
        return dic[key] == value
    except KeyError:
        return False


def uri_validator(x):
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc, result.path])
    except Exception as e:
        print("type error: " + str(e))
        print(traceback.format_exc())
        return False
    
def get_all_website_links(url):
    """
    Returns all URLs that is found on `url` in which it belongs to the same website
    """
    # all URLs of `url`
    urls = set()
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    tags = soup.findAll("a")
    for a_tag in tags:
        href = a_tag.attrs.get("href")
        if href == "" or href is None:
            # href empty tag
            continue
        # join the URL if it's relative (not absolute link)
        href = urljoin(url, href)
        if not uri_validator(href):
            # not a valid URL
            continue
        if 'https' in href:
            urls.add(href)
            continue
        if 'http' in href:
            urls.add(href)
            continue
        if href.startswith("/"):
            base_url = "{0.scheme}://{0.netloc}".format(urlsplit(url))
            urls.add(base_url + href)
            continue
        urls.add(href)
    return urls




def crawl(args):
    for arg in args:
        ssl._create_default_https_context = ssl._create_unverified_context
        html_page = urllib.request.urlopen(arg)
        soup = BeautifulSoup(html_page, features="html.parser")
        links = get_all_website_links(arg)
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
               if status not in codes_to_ignore and check_key_value_pair_existence(brokenLinks,
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
