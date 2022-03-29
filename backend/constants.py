import os

# Required Endpoints
STORE_URL="https://www.foody.com.cy/{store_key}"
JWT_FETCH_URL = "https://login.foody.com.cy/connection/temp/jwt"
STORE_INFO_FETCH_URL = "https://api.foody.com.cy/branch-info/getBranchInfo/{store_id}"
STORE_MENU_FETCH_URL_EN = "https://api.foody.com.cy/menu-boundary-new/branch-menus/en/{store_id}.json"
STORE_MENU_FETCH_URL_EL = "https://api.foody.com.cy/menu-boundary-new/branch-menus/el/{store_id}.json"
STORE_MENU_FETCH_URLS = [
    {
        'locale': 'en',
        'URL': STORE_MENU_FETCH_URL_EN
    },
    {
        'locale': 'el',
        'URL': STORE_MENU_FETCH_URL_EL
    },
]
OPEN_RESTAURANTS_URL = "https://availability.foody.com.cy/getRestaurantsForPostCode"
TAKEAWAY_RESTAURANTS_URL = "https://availability.foody.com.cy/getTakeawayRestaurantsForPostCode"
CLOSED_RESTAURANTS_URL = "https://availability.foody.com.cy/getClosedRestaurantsForPostCode"

# Header keys
JWT_HEADER_KEY = "x-ft"

# DB Connection
MONGODB_USER = os.environ.get("MONGODB_USER", "")
MONGODB_PASSWORD = os.environ.get("MONGODB_PASSWORD", "")
MONGODB_HOST = os.environ.get("MONGODB_HOST", "localhost")
MONGODB_PORT = os.environ.get("MONGODB_PORT", 27017)
MONGODB_DATABASE_NAME = os.environ.get("MONGODB_DATABASE_NAME", "gonna_order")
MONGODB_COLLECTION_NAME = os.environ.get("MONGODB_COLLECTION_NAME", "stores")

# MongoDB collection keys
UPDATED_DATE = "updated_date"
STORE_KEY = "store_key"
RESULT_KEY = "result"
STATUS_KEY = "status"
ERROR_KEY = "error"
DOMAIN_KEY = "domain"
FOODY_DOMAIN_VALUE = "FOOD.CY"
DELIVEROO_DOMAIN_VALUE = "DELIVEROO.NL"
UBEREATS_DOMAIN_VALUE = "UBEREATS.US"
WOLT_DOMAIN_VALUE = "WOLT.COM"
EFOOD_DMOAIN_VALUE = "EFOOD.GR"
DATA_FRESHNESS = 60 * 60 * 24 * 7

ALLOWED_DOMAINS = {FOODY_DOMAIN_VALUE, DELIVEROO_DOMAIN_VALUE, UBEREATS_DOMAIN_VALUE, 
                    WOLT_DOMAIN_VALUE, EFOOD_DMOAIN_VALUE}
# Foody CDN
FOODY_FILES_CDN_BASE = "https://cdn.foody.com.cy/files/"

# Foody Country
FOODY_COUNTRY = "CY"

# Foody allergen data
FOODY_ALLERGEN_DATA = {
    1: "Wheat",
    2: "Rye",
    3: "Barley",
    4: "Oats",
    5: "Crustaceans and products thereof",
    6: "Eggs and products thereof",
    7: "Fish and products thereof",
    8: "Peanuts and products thereof",
    9: "Soybeans and products thereof",
    10: "Milk",
    11: "Almonds",
    12: "Hazelnuts",
    13: "Walnuts",
    14: "Cashews",
    15: "Pecan nuts",
    16: "Brazil nuts",
    17: "Pistachio nuts",
    18: "Macadamia nuts",
    19: "Celery and products thereof",
    20: "Mustard and products thereof",
    21: "Sesame seeds and products thereof",
    22: "Sulphur dioxide and sulphites",
    23: "Lupin and products thereof",
    24: "Molluscs and products thereof",
    0: "No allergens"
}

#deliveroo constants
DELIVEROO_STORE_MENU_FETCH_URL = "https://api.nl.deliveroo.com/orderapp/v1/restaurants/{restaurantID}"
#uber eats constants
UBEREATS_STORE_MENU_FETCH_URL = "https://www.ubereats.com/api/getStoreV1"
#wolt constants
WOLT_STORE_MENU_FETCH_URL = "https://restaurant-api.wolt.com/v4/venues/slug/{store_slug}/menu"
WOLT_STORE_INFO_FETCH_URL = "https://restaurant-api.wolt.com/v3/venues/slug/{store_slug}"
#efood constants
EFOOD_STORE_MENU_FETCH_URL = "https://api.e-food.gr/api/v1/restaurants/{shop_id}"
EFOOD_OPTIONGROUP_FETCH_URL = "https://api.e-food.gr/v3/shops/catalog/product?shop_id={shop_id}&item_code={item_code}"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36"
COOKIE = "_gcl_au=1.1.1019796631.1646262550; G_ENABLED_IDPS=google; _ga=GA1.2.1680562085.1646262551; accepted_cookies=true; cookie_privacy_level=personalization; sparks-sid=d60df637-f323-4ea8-aff6-b4b9d2ef536e; language=en_US; _gid=GA1.2.120976903.1647623284; RestaurantMenuCookieTrigger=true; efood_address=%CE%9A%CE%B1%CF%81%CE%B1%CE%BF%CE%BB%CE%AE+%CE%BA%CE%B1%CE%B9+%CE%94%CE%B7%CE%BC%CE%B7%CF%84%CF%81%CE%AF%CE%BF%CF%85+4%2C+%CE%9A%CE%AD%CE%BD%CF%84%CF%81%CE%BF+%CE%99%CF%89%CE%AC%CE%BD%CE%BD%CE%B9%CE%BD%CE%B1%2C+45332; RestaurantListCookieTrigger=true; __cf_bm=cHZmjUeKGzACWHl5_SxZ4GW4Sv2CevrmbYe5STcALa8-164792Hfv6LG8E3zJ0KT0Fod5V7/k5ZRnzAVrw1Ro+qW1GzaaaxIAaFi5NRXLC0OKeFFclB1FJkT+kJMt8=; ab.storage.deviceId.c971c83a-1b96-4bfb-8d59-ccc0a1361dd2=%7B%22g%22%3A%22abcb3eb0-eaff-59e7-4ad3-6a17eed1029d%22%2C%22c%22%3A1646262548713%2C%22l%22%3A1647929339823%7D; ab.storage.userId.c971c83a-1b96-4bfb-8d59-ccc0a1361dd2=%7B%22g%22%3A%225405575%22%2C%22c%22%3A1647564871668%2C%22l%22%3A1647929339823%7D; AMP_TOKEN=%24NOT_FOUND; cf_clearance=AA.CUgAjjwOajQxTjfajgy2aFqHq4fZQmdr2eitr6.0-1647929622-0-150; ci_session=a%3A7%3A%7Bs%3A10%3A%22session_id%22%3Bs%3A32%3A%2243964d38be70227e4dc3400ef967da01%22%3Bs%3A10%3A%22ip_address%22%3Bs%3A14%3A%22188.43.235.177%22%3Bs%3A10%3A%22user_agent%22%3Bs%3A114%3A%22Mozilla%2F5.0+%28Windows+NT+10.0%3B+Win64%3B+x64%29+AppleWebKit%2F537.36+%28KHTML%2C+like+Gecko%29+Chrome%2F99.0.4844.74+Safari%2F537.36%22%3Bs%3A13%3A%22last_activity%22%3Bi%3A1647856877%3Bs%3A9%3A%22user_data%22%3Bs%3A0%3A%22%22%3Bs%3A8%3A%22map_data%22%3Ba%3A13%3A%7Bs%3A12%3A%22user_address%22%3Bi%3A0%3Bs%3A7%3A%22address%22%3Bs%3A80%3A%22%CE%9A%CE%B1%CF%81%CE%B1%CE%BF%CE%BB%CE%AE+%CE%BA%CE%B1%CE%B9+%CE%94%CE%B7%CE%BC%CE%B7%CF%84%CF%81%CE%AF%CE%BF%CF%85+4%2C+%CE%9A%CE%AD%CE%BD%CF%84%CF%81%CE%BF+%CE%99%CF%89%CE%AC%CE%BD%CE%BD%CE%B9%CE%BD%CE%B1%2C+45332%22%3Bs%3A8%3A%22latitude%22%3Bs%3A9%3A%2239.665595%22%3Bs%3A9%3A%22longitude%22%3Bs%3A9%3A%2220.851233%22%3Bs%3A4%3A%22city%22%3Bs%3A12%3A%22%CE%9A%CE%AD%CE%BD%CF%84%CF%81%CE%BF%22%3Bs%3A6%3A%22county%22%3Bs%3A16%3A%22%CE%99%CF%89%CE%AC%CE%BD%CE%BD%CE%B9%CE%BD%CE%B1%22%3Bs%3A6%3A%22street%22%3Bs%3A40%3A%22%CE%9A%CE%B1%CF%81%CE%B1%CE%BF%CE%BB%CE%AE+%CE%BA%CE%B1%CE%B9+%CE%94%CE%B7%CE%BC%CE%B7%CF%84%CF%81%CE%AF%CE%BF%CF%85%22%3Bs%3A9%3A%22street_no%22%3Bs%3A1%3A%224%22%3Bs%3A4%3A%22slug%22%3Bs%3A1%3A%22%2F%22%3Bs%3A9%3A%22area_slug%22%3Bs%3A0%3A%22%22%3Bs%3A13%3A%22friendly_name%22%3Bs%3A0%3A%22%22%3Bs%3A5%3A%22scope%22%3Bs%3A8%3A%22personal%22%3Bs%3A3%3A%22zip%22%3Bs%3A5%3A%2245332%22%3B%7Ds%3A16%3A%22shop_listing_url%22%3Bs%3A662%3A%22https%3A%2F%2Fwww.e-food.gr%2Fshops%3Faddress%3D%25CE%259A%25CE%25B1%25CF%2581%25CE%25B1%25CE%25BF%25CE%25BB%25CE%25AE%2B%25CE%25BA%25CE%25B1%25CE%25B9%2B%25CE%2594%25CE%25B7%25CE%25BC%25CE%25B7%25CF%2584%25CF%2581%25CE%25AF%25CE%25BF%25CF%2585%2B4%252C%2B%25CE%259A%25CE%25AD%25CE%25BD%25CF%2584%25CF%2581%25CE%25BF%2B%25CE%2599%25CF%2589%25CE%25AC%25CE%25BD%25CE%25BD%25CE%25B9%25CE%25BD%25CE%25B1%252C%2B45332%26useraddress%3D0%26user_address%3D0%26latitude%3D39.665595%26longitude%3D20.851233%26city%3D%25CE%259A%25CE%25AD%25CE%25BD%25CF%2584%25CF%2581%25CE%25BF%26county%3D%25CE%2599%25CF%2589%25CE%25AC%25CE%25BD%25CE%25BD%25CE%25B9%25CE%25BD%25CE%25B1%26zip%3D45332%26street%3D%25CE%259A%25CE%25B1%25CF%2581%25CE%25B1%25CE%25BF%25CE%25BB%25CE%25AE%2B%25CE%25BA%25CE%25B1%25CE%25B9%2B%25CE%2594%25CE%25B7%25CE%25BC%25CE%25B7%25CF%2584%25CF%2581%25CE%25AF%25CE%25BF%25CF%2585%26slug%3D%252F%26area_slug%3D%26friendly_name%3D%26scope%3Dpersonal%26street_no%3D4%26nomap%3D0%26msg_chain%3DThe%2BBig%2BBad%2BWolf%26t%3D1647873950%22%3B%7D267b823a3ad6a97735bcf1ed5f9650df5303568e; _dc_gtm_UA-31518673-1=1; _gat_UA-31518673-1=1; AWSALB=jLfS+I3rs8A2FsvbmW8Czgby1r21tPjis/GOmQFGIOXk+eaQeWnebjdHefFCUIyEnkufIxexVxiZM2oBjXj0wZHV946LVNm7k6noW4QdiX4GYWmqPC76FE3cHWfe; AWSALBCORS=jLfS+I3rs8A2FsvbmW8Czgby1r21tPjis/GOmQFGIOXk+eaQeWnebjdHefFCUIyEnkufIxexVxiZM2oBjXj0wZHV946LVNm7k6noW4QdiX4GYWmqPC76FE3cHWfe; ab.storage.sessionId.c971c83a-1b96-4bfb-8d59-ccc0a1361dd2=%7B%22g%22%3A%2272082128-4a33-d7e0-8537-857a682b914e%22%2C%22e%22%3A1647931293112%2C%22c%22%3A1647929339822%2C%22l%22%3A1647929493112%7D"
