import json
import math
import os
import time
from os.path import exists
from uuid import uuid4

import requests
from bs4 import BeautifulSoup

from utils.errors import TooManyRequestException
from utils.pretty_printer import print_warning, print_danger, print_success


def save_json(file_name, data):
    with open(file_name, 'a') as f:
        json.dump(data, f)


def save_json_overwrite(file_name: str, data, with_backup_failsafe=True):
    if with_backup_failsafe:
        if os.path.exists(file_name):
            os.rename(file_name, file_name + ".bak")

    with open(file_name, 'w') as f:
        json.dump(data, f, indent=4)

    if with_backup_failsafe:
        if os.path.exists(file_name + ".bak"):
            os.remove(file_name + ".bak")


# Function to open json file
def load_json(file_name, if_not_exist_return_this=None):
    try:
        return json.load(open(file_name, encoding='utf-8'))
    except FileNotFoundError:
        if if_not_exist_return_this is not None:
            return if_not_exist_return_this
        raise FileNotFoundError


def get_multiple_cached(cache_folder, group, key):
    if group == "*" or group == '"':
        group = "other"

    filename = f"{cache_folder}{group}.json"
    if not exists(filename):
        return False
    cache = load_json(filename)
    if key in cache:
        return cache[key]
    return False


def remove_multiple_cache(cache_folder):
    for file_name in os.listdir(cache_folder):
        filename = f"{cache_folder}{file_name}"
        if os.path.isfile(filename):
            os.remove(filename)


def get_all_multiple_cache(cache_folder):
    try:
        result = {}
        for file_name in os.listdir(cache_folder):
            filename = f"{cache_folder}{file_name}"
            if 'json' in filename:
                cache_raw = load_json(filename)
                result.update(cache_raw)
        return result
    except FileNotFoundError:
        os.mkdir(cache_folder)
        return {}


def do_multiple_cache(cache_folder: str, group: str, key: str, value):
    if group == "*" or group == '"':
        group = "other"

    group = slugify(group)

    filename = f"{cache_folder}{group}.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    if not exists(filename):
        save_json_overwrite(filename, {
            key: value
        }, with_backup_failsafe=False)
    else:
        existing_cache = load_json(filename)
        existing_cache[key] = value
        save_json_overwrite(filename, existing_cache)


def slugify(text: str):
    spaced = text.replace("/", " ")
    spaced = ''.join(e for e in spaced if e.isalnum() or e == " ")
    spaced = spaced.strip()
    return spaced.replace(" ", "_")


def fetch_page(url, returnIsRedirected=False):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/39.0.2171.95 Safari/537.36 '
    }
    page = requests.get(url, headers=headers)

    if page.status_code == 429:
        raise TooManyRequestException("Too Many Request")

    soup = BeautifulSoup(page.content, "html.parser")

    if returnIsRedirected:
        return page.url, soup.find("html")

    return soup.find("html")


def do_fetch_json(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/39.0.2171.95 Safari/537.36 '
    }
    page = requests.get(url, headers=headers)

    if page.status_code == 429:
        raise TooManyRequestException("Too Many Request")

    return page


def fetch_json(url, sleep_timer=1.5):
    retry = 0
    while True:
        try:
            print_warning("Fetching {JSON}", url)
            result_json = do_fetch_json(url)
            if result_json is None:
                continue
            time.sleep(sleep_timer)
            break
        except TooManyRequestException:
            print_danger("Error", "429, sleeping for 10 mins")
            time.sleep(600)
        except requests.exceptions.ConnectionError:
            print_danger("Error", f"requests.exceptions.ConnectionError, retrying... ({retry + 1})")
            retry += 1
            time.sleep(3)

    print_success("Fetched {JSON}", url)
    return result_json


def fetch_until_success(url: str, sleep_timer=1.5, return_true_url=False):
    while True:
        try:
            print_warning("Fetching", url)
            true_url, result_htmls = fetch_page(url, returnIsRedirected=True)
            if result_htmls is None:
                continue
            time.sleep(sleep_timer)
            break
        except TooManyRequestException:
            print_danger("Error", "429, sleeping for 10 mins")
            time.sleep(600)

    print_success("Fetched", url)
    if return_true_url:
        return true_url, result_htmls
    return result_htmls


def fetch_with_cache(url: str):
    print_warning("Fetching with Cache", url)

    filename = slugify(url)
    filepath = f"cache/htmls/{filename}.html"
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            filedata = f.read()
        return url, BeautifulSoup(filedata, 'html.parser')

    true_url, soup = fetch_until_success(url, return_true_url=True)
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(str(soup))

    return true_url, soup


def print_json(variable):
    print(
        json.dumps(variable, sort_keys=True, indent=2)
    )


def recursive_replace(target, to_replaced, replacer) -> dict:
    if isinstance(target, dict):
        for key, value in target.items():
            target[key] = recursive_replace(value, to_replaced, replacer)
    elif isinstance(target, str):
        target = target.replace(to_replaced, replacer)
    elif isinstance(target, list):
        for idx, value in enumerate(target):
            target[idx] = recursive_replace(value, to_replaced, replacer)

    return target


def safely_replace(target):
    target = recursive_replace(target, "&amp;", "&")
    target = recursive_replace(target, "&apos;", "'")

    return target


def get_next_data_from_soup(soup):
    script_soup = soup.find("script", {'id': '__NEXT_DATA__'})
    process_id = uuid4()
    filename = f'cache/{process_id}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(script_soup.text)

    result = load_json(filename)

    os.remove(filename)

    return result


def get_schema_org_data_from_soup(soup):
    script_soups = soup.find_all("script", {'type': 'application/ld+json'})
    for script_soup in script_soups:
        process_id = uuid4()
        filename = f'cache/{process_id}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(script_soup.text)

        result = load_json(filename)

        os.remove(filename)

        if 'schema.org' in result['@context']:
            return result

    return False
