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
                               STORE_INFO_FETCH_URL, DOMAIN_KEY, FOODY_DOMAIN_VALUE,STORE_URL)
from backend.mapping import StoreInfo, Result, set_locale
from backend.messages import (INTERNAL_SERVER_ERROR_MESSAGE, JWT_TOKEN_FETCH_ERROR, STORE_NOT_FOUND,
                              PROCESS_COMPLETED, PROCESS_FAILED, PROCESS_IN_PROGRESS)

import requests
import re
from bs4 import BeautifulSoup
import json

def prepare_headers(jwt_token):
    return {
        JWT_HEADER_KEY: jwt_token
    }


def fetch_jwt_token() -> str:
    response = requests.get(JWT_FETCH_URL)
    assert response.status_code == statuses.OK, JWT_TOKEN_FETCH_ERROR
    data = response.json()
    return data and data.get('jwt')

def fetch_store_id(store_key) -> str:
    response = requests.get(STORE_URL.format(store_key=store_key))
    assert response.status_code == statuses.OK, "Not found"
    data = response.text.encode('utf8').decode('ascii', 'ignore')
    search_result = re.search(r'[^�]*\"shopID\"\: ([\d]+)[^�]*',data )
    assert search_result is not None, "Not found"
    return search_result.group(1)

def fetch_store_info(store_id, jwt_token) -> StoreInfo:
    fetch_store_info_url = STORE_INFO_FETCH_URL.format(store_id=store_id)
    response = requests.get(fetch_store_info_url, headers=prepare_headers(jwt_token))
    data = {}
    if(response.status_code == statuses.OK):
        data = response.json()
    store_info = StoreInfo.from_dict(data)
    return store_info

def foody_scraping(store_key, domain_key):
    jwt_token = fetch_jwt_token()
    store_id = fetch_store_id(store_key)
    store_info = fetch_store_info(store_id, jwt_token)
    result_obj = None
    for fetch_store_menu_url_obj in STORE_MENU_FETCH_URLS:
        fetch_store_menu_url = fetch_store_menu_url_obj['URL'].format(store_id=store_id)
        locale = fetch_store_menu_url_obj['locale']
        set_locale(locale)
        response = requests.get(fetch_store_menu_url, headers=prepare_headers(jwt_token))

        current_obj = Result.from_dict(response.json())
        current_obj.store_info = store_info
        current_obj.prepare_option_groups()
        current_obj.prepare_variants_for_each_category()

        if result_obj is not None:
            result_obj += current_obj
        else:
            result_obj = current_obj

    result = result_obj and result_obj.to_dict()
    return result