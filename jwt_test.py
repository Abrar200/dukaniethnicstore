# jwt_test.py
# Standalone script to test JWT generation for DoorDash
# Run this in your Django shell: python manage.py shell < jwt_test.py

import jwt
import jwt.utils
import time
import math
import requests
import json

def test_doordash_jwt():
    """Test JWT generation using exact DoorDash specification"""
    print("=== DOORDASH JWT TEST ===")

    # Your actual credentials
    access_key = {
        "developer_id": "811c829f-1159-4a96-b927-112a6ccc5e8e",
        "key_id": "a76ac2a7-09df-4635-a5cb-86f3edbf3a06",
        "signing_secret": "OoAaVZ-ij_r4c0kM0kJTg7qOB7fP8MzPq7jyhZ6oIU"
    }

    print(f"Developer ID: {access_key['developer_id']}")
    print(f"Key ID: {access_key['key_id']}")
    print(f"Signing Secret: {access_key['signing_secret']}")
    print()

    try:
        # Method 1: Exact DoorDash documentation implementation
        print("=== Method 1: Official DoorDash Implementation ===")
        current_time = time.time()

        token1 = jwt.encode(
            {
                "aud": "doordash",
                "iss": access_key["developer_id"],
                "kid": access_key["key_id"],
                "exp": str(math.floor(current_time + 300)),
                "iat": str(math.floor(current_time)),
            },
            jwt.utils.base64url_decode(access_key["signing_secret"]),
            algorithm="HS256",
            headers={"dd-ver": "DD-JWT-V1"}
        )

        if isinstance(token1, bytes):
            token1 = token1.decode('utf-8')

        print(f"✅ JWT Method 1 Success!")
        print(f"Token length: {len(token1)}")
        print(f"Token: {token1[:50]}...{token1[-20:]}")
        print()

        # Test the JWT with a real API call
        print("=== Testing JWT with DoorDash API ===")
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {token1}',
            'Content-Type': 'application/json'
        }

        test_request = {
            "external_delivery_id": f"TEST-{int(time.time())}",
            "pickup_address": "123 Test St, Adelaide SA 5000",
            "dropoff_address": "456 Test Ave, Adelaide SA 5001",
            "order_value": 1000,
            "pickup_phone_number": "+61400000000",
            "dropoff_phone_number": "+61400000000"
        }

        print(f"Making test request to DoorDash...")
        print(f"Request body: {json.dumps(test_request, indent=2)}")

        response = requests.post(
            "https://openapi.doordash.com/drive/v2/quotes",
            headers=headers,
            json=test_request,
            timeout=30
        )

        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response body: {response.text}")

        if response.status_code == 200:
            print("🎉 SUCCESS! JWT is working correctly!")
            quote_data = response.json()
            print(f"Delivery fee: {quote_data.get('fee', 0)} cents")
        elif response.status_code == 401:
            print("❌ 401 Unauthorized - JWT signature still failing")
            print("This indicates the credentials or JWT format is incorrect")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print("Response might give us clues about the issue")

    except Exception as e:
        print(f"❌ Method 1 failed: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

        # Method 2: Alternative implementation
        try:
            print("\n=== Method 2: Alternative Implementation ===")
            current_time = time.time()

            payload = {
                "aud": "doordash",
                "iss": access_key["developer_id"],
                "kid": access_key["key_id"],
                "exp": int(current_time + 300),
                "iat": int(current_time),
            }

            headers_jwt = {
                "alg": "HS256",
                "typ": "JWT",
                "dd-ver": "DD-JWT-V1"
            }

            decoded_secret = jwt.utils.base64url_decode(access_key["signing_secret"])

            token2 = jwt.encode(
                payload=payload,
                key=decoded_secret,
                algorithm="HS256",
                headers=headers_jwt
            )

            if isinstance(token2, bytes):
                token2 = token2.decode('utf-8')

            print(f"✅ JWT Method 2 Success!")
            print(f"Token: {token2[:50]}...{token2[-20:]}")

        except Exception as e2:
            print(f"❌ Method 2 also failed: {e2}")

if __name__ == "__main__":
    test_doordash_jwt()