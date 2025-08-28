# business/services/shippit_service.py
import requests
import json
import logging
from django.conf import settings
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ShippitService:
    def __init__(self):
        self.api_key = settings.SHIPPIT_API_KEY
        self.base_url = settings.SHIPPIT_API_URL
        self.environment = settings.SHIPPIT_ENVIRONMENT
        self.timeout = 30  # seconds

        logger.info(f"Initializing ShippitService for {self.environment} environment")
        logger.debug(f"API Base URL: {self.base_url}")

    def _get_headers(self):
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def _log_request(self, endpoint, payload):
        logger.debug(f"Shippit API Request to {endpoint}:")
        logger.debug(f"Headers: {self._get_headers()}")
        logger.debug(f"Payload: {json.dumps(payload, indent=2)}")

    def _log_response(self, response):
        logger.debug(f"Shippit API Response:")
        logger.debug(f"Status Code: {response.status_code}")
        try:
            logger.debug(f"Body: {json.dumps(response.json(), indent=2)}")
        except:
            logger.debug(f"Body: {response.text}")

    def _handle_error(self, response, context):
        error_info = {
            'status_code': response.status_code,
            'context': context
        }

        try:
            error_data = response.json()
            error_info.update({
                'error': error_data.get('error'),
                'message': error_data.get('message'),
                'details': error_data.get('details')
            })
            error_msg = f"Shippit Error: {error_data.get('error', 'Unknown error')} - {error_data.get('message', 'No details')}"
        except:
            error_msg = f"Shippit Error: HTTP {response.status_code} - {response.text}"

        logger.error(f"{error_msg}\nContext: {context}")
        return error_info

    def quote_delivery(self, pickup_postcode, delivery_postcode, package_details):
        """
        Get delivery quote using correct Shippit API v3 format
        """
        endpoint = f"{self.base_url}/quotes"
        headers = self._get_headers()

        # Build the correct Shippit API v3 payload format
        payload = {
            "quote": {
                "dropoff_postcode": delivery_postcode,
                "dropoff_state": self._postcode_to_state(delivery_postcode),
                "dropoff_suburb": self._postcode_to_suburb(delivery_postcode),
                "parcel_attributes": [
                    {
                        "qty": 1,
                        "weight": package_details.get('weight', 1.0)
                    }
                ]
            }
        }

        # Add dimensions if provided
        parcel = payload["quote"]["parcel_attributes"][0]
        if package_details.get('length'):
            parcel["length"] = package_details['length']
        if package_details.get('width'):
            parcel["width"] = package_details['width']
        if package_details.get('height'):
            parcel["height"] = package_details['height']

        # Add pickup location if different from default (merchant location)
        if pickup_postcode:
            payload["quote"]["pickup_postcode"] = pickup_postcode
            payload["quote"]["pickup_state"] = self._postcode_to_state(pickup_postcode)
            payload["quote"]["pickup_suburb"] = self._postcode_to_suburb(pickup_postcode)

        self._log_request(endpoint, payload)

        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )

            self._log_response(response)

            if response.status_code == 200:
                data = response.json()

                # Parse the Shippit response and convert to expected format
                quotes = []

                if 'response' in data:
                    for courier_response in data['response']:
                        if courier_response.get('success') and courier_response.get('quotes'):
                            courier_type = courier_response.get('courier_type', 'Standard')

                            for quote_data in courier_response['quotes']:
                                quotes.append({
                                    'price': float(quote_data.get('price', 0)),
                                    'courier_name': courier_type,
                                    'service_type': courier_response.get('service_level', 'Standard'),
                                    'eta_date_from': quote_data.get('delivery_date'),
                                    'eta_date_to': quote_data.get('delivery_date'),
                                    'delivery_window': quote_data.get('delivery_window_desc'),
                                    'estimated_transit_time': quote_data.get('estimated_transit_time'),
                                    'raw_data': quote_data
                                })

                logger.info(f"Successfully parsed {len(quotes)} quotes from Shippit")

                # Log each quote for debugging
                for i, quote in enumerate(quotes):
                    logger.info(f"Quote {i+1}: ${quote['price']} via {quote['courier_name']}")

                return {
                    'success': True,
                    'quotes': quotes,  # Now properly formatted
                    'data': data
                }
            else:
                error_info = self._handle_error(response, 'quote_delivery')
                return {
                    'success': False,
                    'error': error_info
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"Shippit API connection error: {str(e)}")
            return {
                'success': False,
                'error': {
                    'message': 'Connection to Shippit failed',
                    'details': str(e)
                }
            }

    def _postcode_to_state(self, postcode):
        """Convert Australian postcode to state abbreviation"""
        postcode = int(postcode)

        if 1000 <= postcode <= 2599 or 2619 <= postcode <= 2899 or 2921 <= postcode <= 2999:
            return "NSW"
        elif 3000 <= postcode <= 3999 or 8000 <= postcode <= 8999:
            return "VIC"
        elif 4000 <= postcode <= 4999 or 9000 <= postcode <= 9999:
            return "QLD"
        elif 5000 <= postcode <= 5999:
            return "SA"
        elif 6000 <= postcode <= 6797 or 6800 <= postcode <= 6999:
            return "WA"
        elif 7000 <= postcode <= 7999:
            return "TAS"
        elif 800 <= postcode <= 899 or 900 <= postcode <= 999:
            return "NT"
        elif 200 <= postcode <= 299 or 2600 <= postcode <= 2618 or 2900 <= postcode <= 2920:
            return "ACT"
        else:
            return "NSW"  # Default fallback

    def _postcode_to_suburb(self, postcode):
        """Convert postcode to a generic suburb name - Shippit needs this field"""
        # For quote purposes, we can use generic names
        # In production, you might want to use a proper postcode database
        postcode = int(postcode)

        major_cities = {
            5000: "Adelaide",
            3000: "Melbourne",
            2000: "Sydney",
            4000: "Brisbane",
            6000: "Perth",
            7000: "Hobart",
            800: "Darwin",
            200: "Canberra"
        }

        # Check for exact matches first
        if postcode in major_cities:
            return major_cities[postcode]

        # Use ranges for major city areas
        if 5000 <= postcode <= 5199:
            return "Adelaide"
        elif 3000 <= postcode <= 3199:
            return "Melbourne"
        elif 2000 <= postcode <= 2199:
            return "Sydney"
        elif 4000 <= postcode <= 4199:
            return "Brisbane"
        elif 6000 <= postcode <= 6199:
            return "Perth"
        elif 7000 <= postcode <= 7199:
            return "Hobart"
        elif 800 <= postcode <= 899:
            return "Darwin"
        elif 200 <= postcode <= 299:
            return "Canberra"
        else:
            # Generic suburb name based on state
            state = self._postcode_to_state(str(postcode))
            return f"Suburb-{postcode}"

    def create_order(self, order_data):
        """
        Create a shipment order in Shippit
        """
        endpoint = f"{self.base_url}/orders"
        headers = self._get_headers()

        # Transform your order_data to Shippit format
        payload = {
            'order': {
                'reference': order_data.get('order_reference'),
                'user_attributes': {
                    'first_name': order_data.get('customer', {}).get('name', '').split(' ')[0],
                    'last_name': ' '.join(order_data.get('customer', {}).get('name', '').split(' ')[1:]),
                    'email': order_data.get('customer', {}).get('email'),
                    'phone': order_data.get('customer', {}).get('phone')
                },
                'delivery_attributes': {
                    'address_line_1': order_data.get('delivery_address', {}).get('street'),
                    'suburb': order_data.get('delivery_address', {}).get('suburb'),
                    'state': order_data.get('delivery_address', {}).get('state'),
                    'postcode': order_data.get('delivery_address', {}).get('postcode'),
                    'country': order_data.get('delivery_address', {}).get('country', 'AU'),
                    'delivery_instructions': order_data.get('delivery_instructions', '')
                },
                'parcel_attributes': []
            }
        }

        # Add parcel information
        for package in order_data.get('packages', []):
            parcel = {
                'qty': 1,
                'weight': package.get('weight', 1.0)
            }
            payload['order']['parcel_attributes'].append(parcel)

        self._log_request(endpoint, payload)

        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )

            self._log_response(response)

            if response.status_code == 201:
                data = response.json()
                logger.info(f"Successfully created Shippit order")
                return {
                    'success': True,
                    'data': data,
                    'tracking_url': data.get('order', {}).get('tracking_url'),
                    'tracking_number': data.get('order', {}).get('tracking_number')
                }
            else:
                error_info = self._handle_error(response, 'create_order')
                return {
                    'success': False,
                    'error': error_info
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"Shippit API connection error: {str(e)}")
            return {
                'success': False,
                'error': {
                    'message': 'Connection to Shippit failed',
                    'details': str(e)
                }
            }

    def get_order_status(self, tracking_number):
        """Get current status of an order"""
        endpoint = f"{self.base_url}/orders/{tracking_number}"
        headers = self._get_headers()

        self._log_request(endpoint, {})

        try:
            response = requests.get(
                endpoint,
                headers=headers,
                timeout=self.timeout
            )

            self._log_response(response)

            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json()
                }
            else:
                error_info = self._handle_error(response, 'get_order_status')
                return {
                    'success': False,
                    'error': error_info
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"Shippit API connection error: {str(e)}")
            return {
                'success': False,
                'error': {
                    'message': 'Connection to Shippit failed',
                    'details': str(e)
                }
            }

    def cancel_order(self, tracking_number, reason="Customer requested cancellation"):
        """Cancel an existing order"""
        endpoint = f"{self.base_url}/orders/{tracking_number}/cancel"
        headers = self._get_headers()

        payload = {
            'reason': reason
        }

        self._log_request(endpoint, payload)

        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )

            self._log_response(response)

            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json()
                }
            else:
                error_info = self._handle_error(response, 'cancel_order')
                return {
                    'success': False,
                    'error': error_info
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"Shippit API connection error: {str(e)}")
            return {
                'success': False,
                'error': {
                    'message': 'Connection to Shippit failed',
                    'details': str(e)
                }
            }