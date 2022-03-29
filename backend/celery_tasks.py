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
                               STORE_INFO_FETCH_URL, DOMAIN_KEY, UBEREATS_DOMAIN_VALUE, 
                               DELIVEROO_DOMAIN_VALUE, FOODY_DOMAIN_VALUE,STORE_URL,
                               UPDATED_DATE, WOLT_DOMAIN_VALUE, EFOOD_DMOAIN_VALUE)
from backend.mapping import StoreInfo, Result, set_locale
from backend.messages import (INTERNAL_SERVER_ERROR_MESSAGE, JWT_TOKEN_FETCH_ERROR, STORE_NOT_FOUND,
                              PROCESS_COMPLETED, PROCESS_FAILED, PROCESS_IN_PROGRESS)

import requests
import re
from bs4 import BeautifulSoup
import json
import logging
import time

logger = logging.getLogger() 

@celery.task
def fetch_store_Menus(store_key, domain_key):
    result=''
    try:
        update_scraping_status(store_key, domain_key, PROCESS_IN_PROGRESS)

        if domain_key == FOODY_DOMAIN_VALUE:
            logger.debug("Store menus of FOOD.CY...") 
            from backend.sites_scrapping.foody import foody_scraping
            result = foody_scraping(store_key, domain_key)
        
        elif domain_key == DELIVEROO_DOMAIN_VALUE:
            logger.debug("Store menus of DELIVEROO.NL...") 
            from backend.sites_scrapping.deliveroo import  deliveroo_scrapping
            result = deliveroo_scrapping(store_key)
        
        elif domain_key == UBEREATS_DOMAIN_VALUE:
            logger.debug("Store menus of UBEREATS.US...")
            from backend.sites_scrapping.ubereats import ubereats_scrapping
            result = ubereats_scrapping(store_key)
        elif domain_key == WOLT_DOMAIN_VALUE:
            logger.debug("Store menus of WOLT.COM...")
            from backend.sites_scrapping.wolt import wolt_scrapping
            result = wolt_scrapping(store_key)
        elif domain_key == EFOOD_DMOAIN_VALUE:
            logger.debug("Store menus of EFOOD.GR...")
            from backend.sites_scrapping.efood import efood_scrapping
            result = efood_scrapping(store_key)
        status = PROCESS_COMPLETED
        error = None
        
    except AssertionError as err:
        error = str(err)
        logger.error(f"Assertion error: {error}")
        status = PROCESS_FAILED
        result = None
    except Exception as err:
        import traceback
        traceback.print_exc()
        logger.error(err)
        error = INTERNAL_SERVER_ERROR_MESSAGE
        status = PROCESS_FAILED
        result = None
    update_scraping_status(store_key, domain_key, status, result=result, error=error)
          

def get_stores_collection():
    if MONGODB_USER and MONGODB_PASSWORD:
        mongo_uri = "mongodb://%s:%s@%s:%s/" % (quote(MONGODB_USER), quote(MONGODB_PASSWORD),
                                                MONGODB_HOST, MONGODB_PORT)
    else:
        mongo_uri = "mongodb://%s:%s/" % (MONGODB_HOST, MONGODB_PORT)
 
    client = MongoClient(mongo_uri)
    db = client[MONGODB_DATABASE_NAME]
    stores_collection = db[MONGODB_COLLECTION_NAME]
    return stores_collection

def update_scraping_status(store_key, domain_key, status, result=None, error=None):
    stores_collection = get_stores_collection()
    return stores_collection.find_one_and_update(
        {
            STORE_KEY: store_key,
        },
        {
            "$set": {
                UPDATED_DATE: time.time(),
                STORE_KEY: store_key,
                DOMAIN_KEY: domain_key,
                RESULT_KEY: result,
                STATUS_KEY: status,
                ERROR_KEY: error
            }
        },
        upsert=True,
        return_document=ReturnDocument.AFTER
    )

@celery.task
def fetch_all_stores_menu_items():
    restaurant_urls = [OPEN_RESTAURANTS_URL, TAKEAWAY_RESTAURANTS_URL, CLOSED_RESTAURANTS_URL]
    jwt_token = fetch_jwt_token()
    headers = prepare_headers(jwt_token)
    for restaurant_url in restaurant_urls:
        try:
            response = requests.get(restaurant_url, headers=headers)
            assert response.status_code == statuses.OK
            response_json = response.json()
            print(response_json)
            data = response_json and response_json.get('data')
            restaurants = data and data.get('restaurants')
            restaurants = restaurants or list()
            for restaurant in restaurants:
                store_key = restaurant['slug']
                fetch_store_menu.apply_async(args=[store_key, FOODY_DOMAIN_VALUE])
        except AssertionError:
            logger.error(f"API: {restaurant_url} didn't respond with 200 status!!")
        except Exception as err:
            logger.error(err)
            import traceback
            traceback.print_exc()

