from http import client as statuses
from urllib.parse import quote
from bs4 import BeautifulSoup
from urllib.request import urlopen

from pymongo import MongoClient, ReturnDocument

from backend import celery, logger
from backend.constants import (JWT_FETCH_URL, JWT_HEADER_KEY, MONGODB_HOST,
                               MONGODB_PORT, MONGODB_DATABASE_NAME, MONGODB_COLLECTION_NAME, STORE_KEY, RESULT_KEY,
                               MONGODB_USER, MONGODB_PASSWORD, STATUS_KEY, ERROR_KEY, OPEN_RESTAURANTS_URL,
                               TAKEAWAY_RESTAURANTS_URL, CLOSED_RESTAURANTS_URL, STORE_MENU_FETCH_URLS,
                               STORE_INFO_FETCH_URL, DOMAIN_KEY, FOODY_DOMAIN_VALUE,STORE_URL, 
                               WOLT_STORE_INFO_FETCH_URL, DELIVEROO_STORE_MENU_FETCH_URL, WOLT_STORE_MENU_FETCH_URL)
from backend.mapping import StoreInfo, Result, set_locale
from backend.messages import (INTERNAL_SERVER_ERROR_MESSAGE, JWT_TOKEN_FETCH_ERROR, STORE_NOT_FOUND,
                              PROCESS_COMPLETED, PROCESS_FAILED, PROCESS_IN_PROGRESS)

import requests
import re
from bs4 import BeautifulSoup
import json

def wolt_scrapping(store_key):

    optiongroups_props = []
    store_slug = get_store_slug(store_key)
    response = requests.get(WOLT_STORE_MENU_FETCH_URL.format(store_slug=store_slug))
    response1 = requests.get(WOLT_STORE_INFO_FETCH_URL.format(store_slug=store_slug))
    
    response.raise_for_status()
    if response.status_code == 200 and response1.status_code == 200:
        json_object = response.json()
        address = response1.json()
        
        store_info = store_Info_Wolt(address)
        categories, selections = categories_Wolt(json_object)
        print(selections)
        option_groups = option_Groups_Wolt(json_object, selections)
        result = {"categories": categories, "storeInfo": store_info, "optionGroups": option_groups}
        return result
    
    else:
        return None

def get_store_slug(store_key):
    store_slug = store_key.split('/')
    return store_slug[len(store_slug) - 1]

def option_Groups_Wolt(json_object, selections):
    categories_and_options = json_object["options"]
    option_groups = []
    for category_and_options in categories_and_options:
        min_selection_value, max_selection_value = find_min_and_max_selectionValue(selections, category_and_options)
        options = []
        option_group = {}
        for option_item in category_and_options["values"]: 
            options.append({
                "name": {
                    "translations": [
                        {
                            "locale": "en",
                            "value": option_item["name"]
                        },
                        {
                            "locale": "nl",
                            "value": option_item["name"]
                        }
                    ]
                },
                "price": option_item["price"] / 100.0,
                "shortDescription": {
                    "translations": []
                }
            })
        option_group = {
            "allowMultipleSelections": 'false' if category_and_options["type"] == "Multichoice" else 'true',
            "identifier": category_and_options["id"],
            "maxCardinality": max_selection_value,
            "minCardinality": min_selection_value,
            "name": {
                "translations": [
                    {
                        "locale": "en",
                        "value": category_and_options["name"]
                    },
                    {
                        "locale": "nl",
                        "value": category_and_options["name"]
                    }
                ]
            },
            "options": options}
        option_groups.append(option_group)
    return option_groups

def find_min_and_max_selectionValue(selections, optiongroup):
    if selections:
        for selection in selections:
            if selection["id"] == optiongroup["id"]:
                return selection["minimum_total_selections"], selection["maximum_total_selections"]
    else:
        return 0, 0

def categories_Wolt(json_object):
    menu_categories = json_object["categories"]
    menu_items = json_object["items"]
    categories = []
    selections = []

    for menu_category in menu_categories:
        category = {}
        name = {}
        offers = []
        offer = {}
        name = {
            "translations": [
                {
                    "locale": "en",
                    "value": menu_category["name"]
                },
                {
                    "locale": "nl",
                    "value": menu_category["name"]
                }
            ]
        }
        for menu_item in menu_items:
            if menu_item["category"] == menu_category["id"]:
                optionGroupIdentifiers = []
                for optiongroup in menu_item["options"]:
                    selection = {"id": optiongroup["parent"], "maximum_total_selections": optiongroup["maximum_total_selections"], "minimum_total_selections" : optiongroup["minimum_total_selections"]}
                    optionGroupIdentifiers.append(optiongroup["id"])
                    selections.append(selection)
                short_description = menu_item["description"].replace('\n\n', " ").replace('\\"', '"')
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
                        "optionGroupIdentifiers": optionGroupIdentifiers,
                        "price": menu_item["baseprice"] / 100.0,
                        "shortDescription": {
                            "translations": [
                                {
                                    "locale": "en",
                                    "value": short_description
                                },
                                {
                                    "locale": "nl",
                                    "value": short_description
                                }
                            ]
                        }}
                offers.append(offer)
        category = {"name": name, "offers":offers}
        categories.append(category)

    return categories, selections

def store_Info_Wolt(address_json):
    address =address_json["results"][0]
    return {
        "address": {
            "city": address["city"],
            "country": address["country"],
            "line1": address["address"],
            "postcode": address["post_code"]
        },
        "alias": address["slug"],
        "backgroundURL": address["mainimage"],
        "name": address["name"][0]["value"]
    }