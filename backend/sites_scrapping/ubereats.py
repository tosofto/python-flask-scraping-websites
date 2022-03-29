from http import client as statuses
from urllib.parse import quote
from bs4 import BeautifulSoup
from urllib.request import urlopen

from pymongo import MongoClient, ReturnDocument

from backend import celery, logger
from backend.constants import (JWT_FETCH_URL, JWT_HEADER_KEY, MONGODB_HOST,
                               MONGODB_PORT, MONGODB_DATABASE_NAME, MONGODB_COLLECTION_NAME, STORE_KEY, RESULT_KEY,
                               MONGODB_USER, MONGODB_PASSWORD, STATUS_KEY, ERROR_KEY, OPEN_RESTAURANTS_URL,
                               TAKEAWAY_RESTAURANTS_URL, CLOSED_RESTAURANTS_URL, STORE_MENU_FETCH_URLS, UBEREATS_STORE_MENU_FETCH_URL,
                               STORE_INFO_FETCH_URL, DOMAIN_KEY, FOODY_DOMAIN_VALUE,STORE_URL, DELIVEROO_STORE_MENU_FETCH_URL)
from backend.mapping import StoreInfo, Result, set_locale
from backend.messages import (INTERNAL_SERVER_ERROR_MESSAGE, JWT_TOKEN_FETCH_ERROR, STORE_NOT_FOUND,
                              PROCESS_COMPLETED, PROCESS_FAILED, PROCESS_IN_PROGRESS)

import requests
import re
from bs4 import BeautifulSoup
import json
import re

def ubereats_scrapping(store_key):
    UuID = get_UuID_from_store_key(store_key)
    headers = {'x-csrf-token': 'x', 'Content-Type': 'application/json'}
    data = {"storeUuid":UuID}
    response = requests.post(UBEREATS_STORE_MENU_FETCH_URL, data = json.dumps(data), headers = headers)
    response.raise_for_status()

    if response.status_code == 200:
        json_object = response.json()
        option_groups_to_return = []
        store_info = store_Info_Ubereats(json_object)
        categories, option_groups_to_return = categories_Ubereats(json_object, store_key)
        result = {"categories": categories, "storeInfo": store_info, "optionGroups": option_groups_to_return}

        return result

    else:
        return None

def get_UuID_from_store_key(store_key):
    response = requests.get(store_key)
    soup = BeautifulSoup(response.content, 'html.parser')
    pull_data = soup.find(id="__PLL__")
    pull_str = str(pull_data) 
    UUID_LENGTH = 36
    start_point = re.search("storeUuid", pull_str).end() + 15
    UuID = pull_str[start_point : start_point + UUID_LENGTH]

    return UuID

def categories_Ubereats(json_object, store_key):
    section_uuid = json_object["data"]["sections"][0]["uuid"]
    menu_categories = json_object["data"]["catalogSectionsMap"][section_uuid]
    menu_items = []
    categories = []
    option_groups_to_return = []

    for menu_category_in in menu_categories:
        category = {}
        name = {}
        offers = []
        offer = {}
        category_section_uuid = menu_category_in["catalogSectionUUID"]
        menu_category = menu_category_in["payload"]["standardItemsPayload"]
        name = {
            "translations": [
                {
                    "locale": "en",
                    "value": menu_category["title"]["text"]
                },
                {
                    "locale": "nl",
                    "value": menu_category["title"]["text"]
                }
            ]
        }
        for menu_item in menu_category["catalogItems"]:
            optionGroupIdentifiers = []
            options_json = get_options_Ubereats(section_uuid, category_section_uuid, menu_item["uuid"], store_key)
            optionGroups = options_json["queries"][1]["state"]["data"]["customizationsList"]
            for optiongroup in optionGroups:
                optionGroupIdentifiers.append(optiongroup["uuid"])
                allowMultipleSelections = 'false' if optiongroup["maxPermitted"] == optiongroup["minPermitted"] == 1 else 'true' 
                options = []
                for option in optiongroup["options"]:
                    options.append({"name": {
                        "translations": [
                            {
                                "locale": "en",
                                "value": option["title"]
                            },
                            {
                                "locale": "nl",
                                "value": option["title"]
                            }
                        ]},
                        "price": option["price"] / 100.0})
                optiongroup_item = {
                    "allowMultipleSelections": allowMultipleSelections,
                    "identifier": optiongroup["uuid"],
                    "maxCardinality": optiongroup["maxPermitted"],
                    "minCardinality": optiongroup["minPermitted"],
                    "name": {
                        "translations": [
                            {
                                "locale": "en",
                                "value": optiongroup["title"]
                            },
                            {
                                "locale": "nl",
                                "value": optiongroup["title"]
                            }
                        ]
                    },
                    "options": options
                }
                option_groups_to_return.append(optiongroup_item)
            offer = {
                "name": {
                    "translations": [
                        {
                            "locale": "en",
                            "value": menu_item["title"]
                        },
                        {
                            "locale": "nl",
                            "value": menu_item["title"]
                        }
                    ]
                },
                "optionGroupIdentifiers": optionGroupIdentifiers,
                "price": menu_item["price"] / 100.0,
                "shortDescription": {
                    "translations": [
                        {
                            "locale": "en",
                            "value": menu_item["itemDescription"] if "itemDescription" in menu_item else None
                        },
                        {
                            "locale": "nl",
                            "value": menu_item["itemDescription"] if "itemDescription" in menu_item else None
                        }
                    ]
                }
            }
            offers.append(offer)
        category = {"name": name, "offers":offers}
        categories.append(category)

    return categories, option_groups_to_return

def store_Info_Ubereats(json_object):
    address = json_object["data"]["location"]
    return {
        "address": {
            "city": address["city"],
            "country": address["country"],
            "line1": address["address"],
            "postcode": address["postalCode"]
        },
        "alias": json_object["data"]["slug"],
        "backgroundURL": json_object["data"]["heroImageUrls"][len(json_object["data"]["heroImageUrls"]) - 1],
        "name": json_object["data"]["title"]
    }

def get_options_Ubereats(sectionuuid, category_section_uuid, item_uuid, store_key):
    store_key_modified = store_key.split('?')
    url = store_key_modified[0] + '/' + sectionuuid + '/' + category_section_uuid + '/' + item_uuid
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    options_data = soup.find(id="__REACT_QUERY_STATE__")
    options_str = str(options_data)
    s = options_str[70 : len(options_str) - 18].replace("\\u0022", "\"").replace("%5C", "").replace(']"', ']').replace('}"', '}').replace('"[', '[').replace('"{', '{')
    options_json = json.loads(s)
    return options_json
