import unittest
from http.client import OK
from unittest.mock import patch, MagicMock

from backend import app, FOODY_DOMAIN_VALUE
from backend.messages import PROCESS_STARTED


class TestApi(unittest.TestCase):
    def setUp(self) -> None:
        self.app = app.test_client()

    @patch('backend.celery_tasks.fetch_store_menu')
    @patch('backend.celery_tasks.update_scraping_status')
    @patch('backend.celery_tasks.get_stores_collection')
    def test_fetch_store_menu(self, mock_get_stores_collection, mock_update_scraping_status,
                              mock_fetch_store_menu):
        mock_store_collection = MagicMock()
        mock_store_collection.find_one.return_value = None
        mock_get_stores_collection.return_value = mock_store_collection

        store_key = 'test'
        domain_key = FOODY_DOMAIN_VALUE
        store_result = {
            'result': None,
            'error': None,
            'status': PROCESS_STARTED,
            'store_key': store_key,
            'domain_key': domain_key
        }

        mock_update_scraping_status.return_value = store_result
        mock_fetch_store_menu.apply_async.return_value = None

        expected_response = {
            'data': store_result,
            'msg': "OK",
            'status': OK
        }

        api_response = self.app.get('/api/store-menu?store-key={}&domain-key={}'.format(store_key, domain_key))

        self.assertDictEqual(api_response.json, expected_response)
