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