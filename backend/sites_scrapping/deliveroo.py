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
                               STORE_INFO_FETCH_URL, DOMAIN_KEY, FOODY_DOMAIN_VALUE,STORE_URL, DELIVEROO_STORE_MENU_FETCH_URL)
from backend.mapping import StoreInfo, Result, set_locale
from backend.messages import (INTERNAL_SERVER_ERROR_MESSAGE, JWT_TOKEN_FETCH_ERROR, STORE_NOT_FOUND,
                              PROCESS_COMPLETED, PROCESS_FAILED, PROCESS_IN_PROGRESS)

import requests
import re
from bs4 import BeautifulSoup
import json

def deliveroo_scrapping(store_key):

    optiongroups_props = []
    restaurantID = get_restaurantID_from_store_key_and_optiongroups(store_key)
    response = requests.get(DELIVEROO_STORE_MENU_FETCH_URL.format(restaurantID=restaurantID))
    
    response.raise_for_status()
    if response.status_code == 200:
        json_object = response.json()
        
        store_info = store_Info_Deliveroo(json_object)
        categories = categories_Deliveroo(json_object)
        option_groups = option_Groups_Deliveroo(json_object)
        result = {"categories": categories, "storeInfo": store_info, "optionGroups": option_groups}
        return result
    
    else:
        return None

def get_restaurantID_from_store_key_and_optiongroups(store_key):
    response = requests.get(store_key)
    soup = BeautifulSoup(response.content, 'html.parser')
    props = soup.find(id="__NEXT_DATA__")
    s = str(props) 
    strtemp = s[51:len(s) - 9]
    json_object = json.loads(strtemp)
    restaurantID = json_object["props"]["initialState"]["menuPage"]["menu"]["meta"]["restaurant"]["id"]
    return restaurantID

def option_Groups_Deliveroo(json_object):
    option_categories = json_object["menu"]["menu_modifier_groups"]
    option_items = json_object["menu"]["menu_items"]
    option_groups = []
    for option_category in option_categories:
        options = []
        option_group = {}
        for modifier_item_id in option_category["modifier_item_ids"]:
            for option_item in option_items:
                if option_item["id"] == modifier_item_id:
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
                        "price": option_item["price"],
                        "shortDescription": {
                            "translations": []
                        }
                    })

        option_group = {
            "allowMultipleSelections": 'false' if option_category["max_selection_points"] == option_category["min_selection_points"] == 1 else 'true',
            "identifier": option_category["id"],
            "maxCardinality": option_category["max_selection_points"],
            "minCardinality": 0,
            "name": {
                "translations": [
                    {
                        "locale": "en",
                        "value": option_category["name"]
                    },
                    {
                        "locale": "nl",
                        "value": option_category["name"]
                    }
                ]
            },
            "options": options}
        option_groups.append(option_group)
    return option_groups
    
    
def categories_Deliveroo(json_object):
    menu_categories = json_object["menu"]["menu_categories"]
    menu_items = json_object["menu"]["menu_items"]
    categories = []
    menu_categories.pop(0)
    menu_categories.pop(0)

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
            if menu_item["category_id"] == menu_category["id"] and menu_item["description"] != None:
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
                        "optionGroupIdentifiers": menu_item["modifier_group_ids"],
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




def store_Info_Deliveroo(json_object):
    address = json_object["address"]
    return {
        "address": {
            "city": address["city"],
            "country": address["country"],
            "line1": address["address1"],
            "postcode": address["post_code"]
        },
        "alias": json_object["uname"],
        "backgroundURL": json_object["image_url"],
        "name": json_object["name_with_branch"]
    }