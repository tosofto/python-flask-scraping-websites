import unittest
from http.client import OK
from unittest.mock import MagicMock, patch

from backend import celery_tasks, PROCESS_COMPLETED, FOODY_DOMAIN_VALUE
from backend.mapping import Result, StoreInfo


class CeleryTaskTest(unittest.TestCase):
    @patch('requests.get')
    def test_fetch_jwt_token(self, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = OK
        expected_jwt_token = "test"
        mock_data = {
            'jwt': expected_jwt_token
        }
        mock_response.json.return_value = mock_data
        mock_requests_get.return_value = mock_response

        code_jwt_token = celery_tasks.fetch_jwt_token()

        self.assertIsNotNone(code_jwt_token)
        self.assertEqual(code_jwt_token, expected_jwt_token)

    def test_prepare_headers(self):
        # Arrange
        token = "test"
        expected_output = {
            "x-ft": token
        }

        # Act
        code_output = celery_tasks.prepare_headers(jwt_token=token)

        # Assert
        self.assertDictEqual(code_output, expected_output)

    @patch('requests.get')
    def test_fetch_store_info(self, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = OK
        mock_data = {
            'name': "Test"
        }
        mock_response.json.return_value = mock_data
        mock_requests_get.return_value = mock_response

        expected_store_obj = StoreInfo.from_dict(mock_data)

        test_store_id = "123"
        store_info_obj = celery_tasks.fetch_store_info(test_store_id, celery_tasks.fetch_jwt_token())

        self.assertDictEqual(store_info_obj.to_dict(), expected_store_obj.to_dict())

    @patch('requests.get')
    @patch('backend.celery_tasks.fetch_jwt_token')
    @patch('backend.celery_tasks.fetch_store_id')
    @patch('backend.celery_tasks.update_scraping_status')
    @patch('backend.celery_tasks.fetch_store_info')
    def test_fetch_store_menu(self, mock_fetch_store_info, mock_update_scraping_status, mock_fetch_store_id,
                              mock_fetch_jwt_token, mock_requests_get):
        mock_update_scraping_status.return_value = None
        mock_fetch_store_id.return_value = "123"
        mock_fetch_jwt_token.return_value = "test"
        mock_fetch_store_info.return_value = None

        mock_response = MagicMock()
        mock_response.status_code = OK
        store_key = 'test-key'
        domain_key = 'test-domain'
        mock_data = {
            'store-data': 'test'
        }
        mock_response.json.return_value = mock_data
        mock_requests_get.return_value = mock_response

        single_result_obj = Result.from_dict(mock_data)
        single_result_obj.store_info = None
        mock_result_obj = single_result_obj + single_result_obj

        celery_tasks.fetch_store_menu(store_key, domain_key)

        mock_update_scraping_status.assert_called_with(store_key, domain_key, PROCESS_COMPLETED,
                                                       result=mock_result_obj.to_dict(), error=None)

    @patch('requests.get')
    @patch('backend.celery_tasks.fetch_jwt_token')
    @patch('backend.celery_tasks.fetch_store_id')
    @patch('backend.celery_tasks.fetch_store_menu')
    def test_fetch_all_stores_menu_items(self, mock_fetch_store_menu, mock_fetch_store_id,
                                         mock_fetch_jwt_token, mock_requests_get):
        mock_fetch_store_menu.apply_async.return_value = None
        mock_fetch_store_id.return_value = "123"
        mock_fetch_jwt_token.return_value = "test"

        mock_response = MagicMock()
        mock_response.status_code = OK
        restaurants = [
            {
                'slug': 'store-key1'
            },
            {
                'slug': 'store-key2'
            },
            {
                'slug': 'store-key3'
            }
        ]
        mock_data = {
            'data': {
                'restaurants': restaurants
            }
        }
        mock_response.json.return_value = mock_data
        mock_requests_get.return_value = mock_response

        celery_tasks.fetch_all_stores_menu_items()

        for restaurant in restaurants:
            mock_fetch_store_menu.apply_async.assert_any_call(args=[restaurant['slug'], FOODY_DOMAIN_VALUE])
