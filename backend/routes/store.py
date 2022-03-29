from http.client import INTERNAL_SERVER_ERROR, BAD_REQUEST, OK

from flask import request

from backend.constants import STORE_KEY, DOMAIN_KEY, ALLOWED_DOMAINS, DATA_FRESHNESS, UPDATED_DATE
from backend.extensions import api
from backend.messages import PROCESS_STARTED, STORE_KEY_IS_REQUIRED, DOMAIN_KEY_IS_REQUIRED

import requests
import re
from bs4 import BeautifulSoup
import json
import logging
import time

logger = logging.getLogger() 

@api.route('/store-menu', methods=['GET'])
def fetch_store_menu():
    from backend.celery_tasks import get_stores_collection, update_scraping_status, fetch_store_Menus
    try:
        store_key = request.args.get('store-key')
        domain_key = request.args.get('domain-key')
        assert domain_key, DOMAIN_KEY_IS_REQUIRED
        assert domain_key in ALLOWED_DOMAINS, "Supported domains are: {}".format(",".join(ALLOWED_DOMAINS))
        refresh = request.args.get('refresh') == "true"
        assert store_key, STORE_KEY_IS_REQUIRED

        time_interval = 0
        store_old = False
        store_result = None

        if not refresh:
            stores_collection = get_stores_collection()
            logger.debug("Database connected...") 
            store_result = stores_collection.find_one(filter={
                STORE_KEY: store_key,
                DOMAIN_KEY: domain_key
            })
            if store_result:
                time_interval = time.time() - store_result[UPDATED_DATE]
                if time_interval >= DATA_FRESHNESS:
                    stores_collection.delete_one(store_result)
                    store_old = True

        if store_result is None or store_old is True:
            if store_old is True:
                logger.debug("Menus are old. Updating them...")
            else:
                logger.debug("This is new store. Scraping store menus...") 
            store_result = update_scraping_status(store_key, domain_key, PROCESS_STARTED)
            fetch_store_Menus(store_key, domain_key)
        else:
            logger.debug("Menus existing in database...") 

        store_result.pop('_id', None)
        data = store_result
        msg = "OK"
        status = OK
    except AssertionError as err:
        msg = str(err)
        status = BAD_REQUEST
        data = None
    except Exception as err:
        import traceback
        traceback.print_exc()
        msg = str(err)
        status = INTERNAL_SERVER_ERROR
        data = None
    response = {
        'data': data,
        'msg': msg,
        'status': status
    }
    logger.debug("Responding...") 
    return response


@api.route('/domain-stores', methods=['GET'])
def fetch_scrapped_store_keys():
    from backend.celery_tasks import get_stores_collection
    try:
        domain = request.args.get('domain-key')
        assert domain, DOMAIN_KEY_IS_REQUIRED
        assert domain in ALLOWED_DOMAINS, "Supported domains are: {}".format(",".join(ALLOWED_DOMAINS))
        stores_collection = get_stores_collection()
        stores = stores_collection.find(filter={DOMAIN_KEY: domain}, projection={'_id': False, STORE_KEY: True})
        data = {
            'store_keys': [store.get(STORE_KEY) for store in stores]
        }
        msg = "OK"
        status = OK
    except AssertionError as err:
        msg = str(err)
        status = BAD_REQUEST
        data = None
    except Exception as err:
        import traceback
        traceback.print_exc()
        msg = str(err)
        status = INTERNAL_SERVER_ERROR
        data = None
    response = {
        'data': data,
        'msg': msg,
        'status': status
    }
    return response
