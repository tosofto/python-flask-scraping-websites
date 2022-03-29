from http import client as statuses
from urllib.parse import quote
from bs4 import BeautifulSoup
from urllib.request import urlopen
import undetected_chromedriver as webdriver
from selenium.webdriver.chrome.options import Options

from pymongo import MongoClient, ReturnDocument

from backend import celery, logger
from backend.constants import (JWT_FETCH_URL, JWT_HEADER_KEY, MONGODB_HOST,
                               MONGODB_PORT, MONGODB_DATABASE_NAME, MONGODB_COLLECTION_NAME, STORE_KEY, RESULT_KEY, USER_AGENT,
                               MONGODB_USER, MONGODB_PASSWORD, STATUS_KEY, ERROR_KEY, OPEN_RESTAURANTS_URL, COOKIE,
                               TAKEAWAY_RESTAURANTS_URL, CLOSED_RESTAURANTS_URL, STORE_MENU_FETCH_URLS,
                               STORE_INFO_FETCH_URL, DOMAIN_KEY, FOODY_DOMAIN_VALUE,STORE_URL, 
                               WOLT_STORE_INFO_FETCH_URL, DELIVEROO_STORE_MENU_FETCH_URL, EFOOD_OPTIONGROUP_FETCH_URL,
                               WOLT_STORE_MENU_FETCH_URL, EFOOD_STORE_MENU_FETCH_URL)
from backend.mapping import StoreInfo, Result, set_locale
from backend.messages import (INTERNAL_SERVER_ERROR_MESSAGE, JWT_TOKEN_FETCH_ERROR, STORE_NOT_FOUND,
                              PROCESS_COMPLETED, PROCESS_FAILED, PROCESS_IN_PROGRESS)

import requests
import re
from bs4 import BeautifulSoup
import json
import time

def efood_scrapping(store_key):

    shop_id = fetch_shop_id(store_key)
    response = requests.get(EFOOD_STORE_MENU_FETCH_URL.format(shop_id=shop_id)) 
    response.raise_for_status()
    if response.status_code == 200:
        json_object = response.json()
        menu_data = json_object["data"]
        store_info = {}
        option_groups = []
        categories = categories_Efood(menu_data)
        store_info = store_Info_Efood(menu_data)
        option_groups = optionGroup_Efood(menu_data, shop_id)
        result = {"categories": categories, "storeInfo": store_info, "optionGroups": option_groups}
        return result

    else:
        return None

def optionGroup_Efood(menu_data, shop_id):
    optiongroups = []
    optiongroups_origin = menu_data["menu"]["categories"]
    for optiongroup_origin in optiongroups_origin:
        for item in optiongroup_origin["items"]:
            optiongroups.append(optionGroup_for_offer_Efood(shop_id, item["code"]))
    return optiongroups
    
    
def optionGroup_for_offer_Efood(shop_id, item_code):
    response = requests.get(EFOOD_OPTIONGROUP_FETCH_URL.format(shop_id=shop_id, item_code=item_code)) 
    response.raise_for_status()
    if response.status_code == 200:
        json_object = response.json()
        optionGroups_All = json_object["data"]["tiers"]
        optiongroups_result = []
        for optionGroup in optionGroups_All:
            options = []
            for option in optionGroup["options"]:
                options.append({
                    "name": {
                        "translations": [
                            {
                                "locale": "en",
                                "value": option["name"]
                            },
                            {
                                "locale": "el",
                                "value": option["name"]
                            }
                        ]
                    },
                    "price": option["price"],
                    "shortDescription": {
                        "translations": []
                    }
                })
            item = {
                "allowMultipleSelections": 'true' if optionGroup["maximum_selections"] > 1 else 'false',
                "identifier": optionGroup["code"],
                "maxCardinality": optionGroup["maximum_selections"],
                "minCardinality": 1,
                "name": {
                    "translations": [
                        {
                            "locale": "en",
                            "value": optionGroup["name"]
                        },
                        {
                            "locale": "el",
                            "value": optionGroup["name"]
                        }
                    ]
                },
                "options": options
            }
            optiongroups_result.append(item)
        return optiongroups_result

def fetch_shop_id(store_key) -> str:
    chrome_options = Options()
    driver = webdriver. Chrome(options=chrome_options)
    driver.get(store_key)
    time.sleep(10)
    data = driver.page_source.encode('utf8').decode('ascii', 'ignore')
    search_result = re.search(r'[^�]*\"shopID\"\: ([\d]+)[^�]*',data )
    driver.close()
    
    return search_result.group(1)

def categories_Efood(menu_data):
    categories = []
    categories_origin = menu_data["menu"]["categories"]
    
    for menu_category_and_items in categories_origin:
        category = {}
        name = {}
        offers = []
        offer = {}
        name = {
            "translations": [
                {
                    "locale": "en",
                    "value": menu_category_and_items["name"]
                },
                {
                    "locale": "nl",
                    "value": menu_category_and_items["name"]
                }
            ]
        }
        for menu_item in menu_category_and_items["items"]:
            menu_item["option_codes"]
            offer = {
                "name": {
                    "translations": [
                        {
                            "locale": "en",
                            "value": menu_item["name"]
                        },
                        {
                            "locale": "nl",
                            "value": menu_item["name"]
                        }
                    ]
                },
                "optionGroupIdentifiers": get_groupIdentifiers_from_Option_Code(menu_item["option_codes"]),
                "price": menu_item["price"],
                "shortDescription": {
                    "translations": [
                        {
                            "locale": "en",
                            "value": menu_item["description"]
                        },
                        {
                            "locale": "nl",
                            "value": menu_item["description"]
                        }
                    ]
            }}
            offers.append(offer)
        category = {"name": name, "offers":offers}
        categories.append(category)

    return categories

def store_Info_Efood(menu_data):

    address = menu_data["information"]
    return {
        "address": {
            "city": address["address"]["area"]["name"],
            "line1": address["address"]["description"],
            "postcode": address["address"]["zip"]
        },
        "alias": address["title"],
        "logoURL": address["logo"],
        "name": address["title"]
    }

def get_groupIdentifiers_from_Option_Code(option_codes):
    groupIndentifiers = []
    temp = ''
    for option_code in option_codes:
        iterr = option_code.split(".")
        if iterr[0] != temp:
            temp = iterr[0]
            groupIndentifiers.append(temp)

    return groupIndentifiers