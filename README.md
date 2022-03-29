# stores-scrap

Stores Scrap project provides an API which can be used to scrap any store menu from food booking websites including foody, deliveroo, ubereats, wolt, and e-food.

## Run the backend

Backend of this project is written in Flask

### Create virtual environment

```shell
python3 -m venv env
source env/bin/activate
```

### Install the requirements

```shell
pip install -r requirements.txt
```

### Expose environment variables
It requires a REDIS server, and a MongoDB to work. Following ENV variables can be used to provide these settings:
```shell
export MONGODB_HOST="MONGODB_HOST_HERE"
export REDIS_HOST="REDIS_HOST_HERE"
```

### Run tests

```shell
nose2 -v
```

### Run API server

```shell
gunicorn runserver:app
```

### Run Celery worker
```shell
celery -A runserver:celery worker
```

### Run complete setup from Docker
This project contains the Dockerfile for building both API service and worker service, and it also contains the 
docker-compose.yaml file that can be used to start all services altogether.

To start the services:
```shell
docker-compose up -d 
```

To stop the services:
```shell
docker-compose down
```

## API Docs
API Documentation for this project can be found [here](https://documenter.getpostman.com/view/1872196/TzCLAUxy).

## How to test APIs in local environment
API can be tested in local environment using Postman. 
API parameters are store-key and domain-key, and there is no need to introduce other arguments.
And It can be tested in the following procedure:

First of all, open the postman and put the send method as GET.

http://localhost:5000/api/store-menu?store-key={store_key}&domain-key={domain-key}

The API is configured as the above structure. Here store-key and domain-key parameters are used to determine the specific store which will be scraped.

1. Ensure the website of which store you are going to scrap and put the corresponding domain name into the domain-name field of the API parameters.

   foody.com.cy: FOOD.CY

   deliveroo.co.uk: DELIVEROO.NL 
   
   wolt.com: WOLT.COM
   
   ubereats.com: UBEREATS.COM
   
   e-food.gr: EFOOD.GR

2. Get the link of the store you want to scrap.

   For example, the API should have to following structure:

   http://75.119.153.127/api/store-menu?store-key=https://wolt.com/en/aze/baku/venue/parlaq-dessert&domain-key=WOLT.COM 

   http://75.119.153.127/api/store-menu?store-key=https://www.e-food.gr/delivery/menu/pizza-fan&domain-key=EFOOD.GR

   http://75.119.153.127/api/store-menu?store-key=https://deliveroo.nl/en/menu/amsterdam/pijp/sushi-only-ceintuurbaan&domain-key=DELIVEROO.NL

   http://75.119.153.127/api/store-menu?store-key=starbucks&domain-key=FOOD.CY

   http://localhost:5000/api/store-menu?store-key=https://www.ubereats.com/nl-en/store/new-york-pizza-amsterdam-pieter-calandlaan/P7r7FKBCQ12wdHcymnIxSg&domain-key=UBEREATS.COM

3. Copy and paste it into the store-name field of the API parameters.

4. And click the send button and wait until response gets back to the response field.

5. If it is the first time to scrap that store, then you will get the following JSON object of which status value is "Store menu scraping process is started!".

6. If you want to see the scraping result, you have to click send button, once more. Then you can get the following result in the response field.
