# Run this in Django shell to check your credential environment
# python manage.py shell

def check_doordash_environment():
    """
    Check if your DoorDash credentials are for sandbox or production
    and verify they're working correctly
    """
    import requests
    import json
    from django.conf import settings

    print("=== DOORDASH ENVIRONMENT CHECK ===")

    # Your credentials
    developer_id = getattr(settings, 'DOORDASH_DEVELOPER_ID', None)
    key_id = getattr(settings, 'DOORDASH_KEY_ID', None)
    signing_secret = getattr(settings, 'DOORDASH_SIGNING_SECRET', None)

    print(f"Developer ID: {developer_id}")
    print(f"Key ID: {key_id}")
    print(f"Signing Secret: {signing_secret}")
    print()

    if not all([developer_id, key_id, signing_secret]):
        print("❌ Missing credentials in settings!")
        return False

    # Import your service
    try:
        from business.services.doordash_service import DoorDashService
        service = DoorDashService()
        print("✅ DoorDash service imported and initialized")
    except Exception as e:
        print(f"❌ Service initialization failed: {e}")
        return False

    # Test JWT generation
    try:
        headers = service.get_headers()
        print("✅ JWT generation successful")
        print(f"Authorization header length: {len(headers.get('Authorization', ''))}")
    except Exception as e:
        print(f"❌ JWT generation failed: {e}")
        return False

    # Test simple API call to check environment
    print("\n=== TESTING API ENDPOINTS ===")

    # Test a simple quote request to determine environment
    test_result = service.get_delivery_quote(
        pickup_address="123 Test Street, Adelaide SA 5000",
        dropoff_address="456 Test Avenue, Adelaide SA 5001",
        order_value=1000  # $10 test order
    )

    print(f"Test quote result: {test_result}")

    if test_result['success']:
        print("🎉 SUCCESS! Your credentials are working!")
        print(f"Environment: SANDBOX (credentials are valid)")
        return True
    else:
        error = test_result.get('error', 'Unknown error')
        status_code = test_result.get('status_code', 'Unknown')

        print(f"❌ Test failed: {error}")
        print(f"Status code: {status_code}")

        if status_code == 401:
            if 'signature could not be verified' in error:
                print("\n💡 DIAGNOSIS:")
                print("Your credentials appear to be incorrect or for a different environment.")
                print("\nPlease check:")
                print("1. Go to https://developer.doordash.com/portal/credentials")
                print("2. Verify your Developer ID, Key ID, and Signing Secret")
                print("3. Make sure you're using SANDBOX credentials")
                print("4. Generate new credentials if needed")
                return False
            else:
                print("\n💡 Authentication issue - different error type")
                return False
        else:
            print(f"\n💡 Non-authentication error: {status_code}")
            return False

# Run the check
if __name__ == '__main__':
    check_doordash_environment()