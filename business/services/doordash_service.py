# business/services/doordash_service.py - FINAL CORRECTED VERSION

import jwt
import time
import requests
import json
import base64
from django.conf import settings
import logging
import traceback

logger = logging.getLogger(__name__)

class DoorDashService:
    def __init__(self):
        logger.info("=== DOORDASH SERVICE FINAL VERSION ===")

        # Get credentials from settings
        self.developer_id = getattr(settings, 'DOORDASH_DEVELOPER_ID', None)
        self.key_id = getattr(settings, 'DOORDASH_KEY_ID', None)
        self.signing_secret = getattr(settings, 'DOORDASH_SIGNING_SECRET', None)

        # Use sandbox URL (your credentials are for sandbox)
        self.base_url = 'https://openapi.doordash.com/drive/v2'

        logger.info(f"Developer ID: {self.developer_id}")
        logger.info(f"Key ID: {self.key_id}")
        logger.info(f"Signing secret present: {bool(self.signing_secret)}")
        logger.info(f"Base URL: {self.base_url}")

        if not all([self.developer_id, self.key_id, self.signing_secret]):
            raise ValueError("Missing DoorDash credentials")

    def _generate_jwt(self):
        """Generate JWT with EXACT DoorDash specifications"""
        logger.info("--- GENERATING JWT (CORRECTED VERSION) ---")

        try:
            current_time = int(time.time())

            # CRITICAL: Use integers for timestamps, not strings
            payload = {
                'aud': 'doordash',
                'iss': self.developer_id,
                'kid': self.key_id,
                'exp': current_time + 300,  # INTEGER, not string
                'iat': current_time         # INTEGER, not string
            }

            # CRITICAL: Exact header format DoorDash expects
            headers = {
                'alg': 'HS256',
                'typ': 'JWT',
                'dd-ver': 'DD-JWT-V1'
            }

            logger.info(f"Payload with INTEGER timestamps: {payload}")
            logger.info(f"Headers: {headers}")

            # Decode signing secret properly
            try:
                # Add padding if needed
                signing_secret_padded = self.signing_secret
                missing_padding = len(signing_secret_padded) % 4
                if missing_padding:
                    signing_secret_padded += '=' * (4 - missing_padding)

                # Decode using base64url
                signing_secret_bytes = base64.urlsafe_b64decode(signing_secret_padded)
                logger.info(f"✅ Signing secret decoded: {len(signing_secret_bytes)} bytes")

            except Exception as decode_error:
                logger.error(f"❌ Signing secret decode failed: {decode_error}")
                raise ValueError(f"Invalid signing secret: {decode_error}")

            # Generate JWT with PyJWT
            token = jwt.encode(
                payload=payload,
                key=signing_secret_bytes,
                algorithm='HS256',
                headers=headers
            )

            # Ensure token is string
            if isinstance(token, bytes):
                token = token.decode('utf-8')

            logger.info(f"✅ JWT generated successfully")
            logger.info(f"Token length: {len(token)}")
            logger.info(f"Token: {token[:50]}...{token[-20:]}")

            # Verify token structure
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError(f"Invalid JWT structure: {len(parts)} parts")

            return token

        except Exception as e:
            logger.error(f"❌ JWT generation failed: {e}")
            logger.error(traceback.format_exc())
            raise

    def get_headers(self):
        """Get properly formatted headers"""
        token = self._generate_jwt()

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'DukaniEthnicStore/1.0'
        }

        logger.info("✅ Headers generated")
        return headers

    def get_delivery_quote(self, pickup_address, dropoff_address, order_value, tip=0):
        """Get delivery quote with corrected request format"""
        logger.info("\n=== DOORDASH QUOTE REQUEST (FINAL VERSION) ===")
        logger.info(f"Pickup: {pickup_address}")
        logger.info(f"Dropoff: {dropoff_address}")
        logger.info(f"Order value: ${order_value/100}")

        # Generate unique delivery ID
        external_delivery_id = f"QUOTE-{int(time.time())}-{abs(hash(pickup_address)) % 100000}"
        logger.info(f"External delivery ID: {external_delivery_id}")

        # CRITICAL: Exact request format DoorDash expects
        request_body = {
            "external_delivery_id": external_delivery_id,
            "pickup_address": pickup_address,
            "dropoff_address": dropoff_address,
            "order_value": order_value,  # Must be integer (cents)
            "pickup_phone_number": "+61400000000",
            "dropoff_phone_number": "+61400000000"
        }

        # Only add tip if provided
        if tip > 0:
            request_body["tip"] = tip

        logger.info(f"Request body: {json.dumps(request_body, indent=2)}")

        try:
            headers = self.get_headers()
            url = f"{self.base_url}/quotes"

            logger.info(f"Making request to: {url}")

            response = requests.post(
                url,
                headers=headers,
                json=request_body,
                timeout=30
            )

            logger.info(f"Response status: {response.status_code}")

            try:
                response_text = response.text
                logger.info(f"Response body: {response_text}")
            except:
                response_text = "Could not read response"

            if response.status_code == 200:
                try:
                    quote_data = response.json()
                    logger.info("✅ SUCCESS! Quote received")
                    logger.info(f"Quote keys: {list(quote_data.keys())}")

                    if 'fee' in quote_data:
                        logger.info(f"Delivery fee: ${quote_data['fee']/100}")

                    return {
                        'success': True,
                        'quote_id': external_delivery_id,
                        'fee': quote_data.get('fee', 0),
                        'currency': quote_data.get('currency', 'AUD'),
                        'pickup_time_estimated': quote_data.get('pickup_time_estimated'),
                        'dropoff_time_estimated': quote_data.get('dropoff_time_estimated'),
                        'data': quote_data
                    }

                except json.JSONDecodeError as json_error:
                    logger.error(f"❌ Invalid JSON response: {json_error}")
                    return {
                        'success': False,
                        'error': f"Invalid response format: {json_error}",
                        'status_code': response.status_code
                    }

            elif response.status_code == 401:
                logger.error("❌ 401 Authentication Error")

                try:
                    error_data = response.json()
                    error_message = error_data.get('message', 'Authentication failed')
                    logger.error(f"DoorDash error: {error_message}")

                    # Specific handling for JWT signature errors
                    if 'signature could not be verified' in error_message:
                        return {
                            'success': False,
                            'error': 'DoorDash credentials invalid. Please check your Developer ID, Key ID, and Signing Secret in the DoorDash Developer Portal.',
                            'status_code': 401,
                            'details': 'JWT signature verification failed - this usually means credentials are incorrect or for wrong environment'
                        }
                    else:
                        return {
                            'success': False,
                            'error': error_message,
                            'status_code': 401
                        }

                except:
                    return {
                        'success': False,
                        'error': 'Authentication failed - invalid credentials',
                        'status_code': 401
                    }

            else:
                logger.error(f"❌ HTTP Error {response.status_code}")

                try:
                    error_data = response.json()
                    error_message = error_data.get('message', f"HTTP {response.status_code} error")
                except:
                    error_message = f"HTTP {response.status_code} error"

                return {
                    'success': False,
                    'error': error_message,
                    'status_code': response.status_code,
                    'response_body': response_text
                }

        except requests.exceptions.Timeout:
            logger.error("❌ Request timeout")
            return {
                'success': False,
                'error': 'Request timeout - DoorDash API not responding'
            }

        except requests.exceptions.ConnectionError:
            logger.error("❌ Connection error")
            return {
                'success': False,
                'error': 'Connection error - cannot reach DoorDash API'
            }

        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }

    def accept_delivery_quote(self, external_delivery_id, pickup_details, dropoff_details, tip=0):
        """Accept delivery quote"""
        logger.info(f"=== ACCEPTING QUOTE: {external_delivery_id} ===")

        request_body = {
            "tip": tip,
            "pickup_business_name": pickup_details.get('business_name', ''),
            "pickup_phone_number": pickup_details.get('phone', '+61400000000'),
            "pickup_instructions": pickup_details.get('instructions', ''),
            "dropoff_contact_given_name": dropoff_details.get('name', ''),
            "dropoff_phone_number": dropoff_details.get('phone', '+61400000000'),
            "dropoff_instructions": dropoff_details.get('instructions', ''),
            "dropoff_contact_send_notifications": True,
            "order_value": pickup_details.get('order_value', 0)
        }

        try:
            response = requests.post(
                f"{self.base_url}/quotes/{external_delivery_id}/accept",
                headers=self.get_headers(),
                json=request_body,
                timeout=30
            )

            if response.status_code == 200:
                delivery_data = response.json()
                logger.info("✅ Delivery created successfully")
                return {
                    'success': True,
                    'delivery_id': delivery_data.get('delivery_id'),
                    'tracking_url': delivery_data.get('tracking_url'),
                    'data': delivery_data
                }
            else:
                logger.error(f"❌ Accept quote failed: {response.status_code}")
                return {
                    'success': False,
                    'error': f"Failed to accept quote: {response.text}",
                    'status_code': response.status_code
                }

        except Exception as e:
            logger.error(f"❌ Accept quote error: {e}")
            return {
                'success': False,
                'error': f"Accept quote failed: {str(e)}"
            }

    def get_delivery_status(self, external_delivery_id):
        """Get delivery status"""
        try:
            response = requests.get(
                f"{self.base_url}/deliveries/{external_delivery_id}",
                headers=self.get_headers(),
                timeout=30
            )

            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f"Status check failed: {response.text}"
                }

        except Exception as e:
            return {
                'success': False,
                'error': f"Status check failed: {str(e)}"
            }