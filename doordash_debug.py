# django_debug.py - Run this in your project directory

import os
import sys
import django

# Add your project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom.settings')  # Change 'ecom' to your project name
django.setup()

# Now import Django components
from django.conf import settings

def check_doordash_environment():
    """
    Check if your DoorDash credentials are configured and working
    """
    print("=== DOORDASH ENVIRONMENT CHECK ===")

    # Check if settings are loaded
    print(f"Django settings module: {settings.SETTINGS_MODULE}")
    print(f"Debug mode: {settings.DEBUG}")
    print()

    # Your credentials
    developer_id = getattr(settings, 'DOORDASH_DEVELOPER_ID', None)
    key_id = getattr(settings, 'DOORDASH_KEY_ID', None)
    signing_secret = getattr(settings, 'DOORDASH_SIGNING_SECRET', None)
    base_url = getattr(settings, 'DOORDASH_BASE_URL', None)

    print(f"Developer ID: {developer_id}")
    print(f"Key ID: {key_id}")
    print(f"Signing Secret: {signing_secret}")
    print(f"Base URL: {base_url}")
    print()

    if not all([developer_id, key_id, signing_secret]):
        print("❌ Missing credentials in settings!")
        print("\nPlease add these to your settings.py:")
        print("DOORDASH_DEVELOPER_ID = '811c829f-1159-4a96-b927-112a6ccc5e8e'")
        print("DOORDASH_KEY_ID = 'a76ac2a7-09df-4635-a5cb-86f3edbf3a06'")
        print("DOORDASH_SIGNING_SECRET = 'OoAaVZ-ij_r4c0kM0kJTg7qOB7fP8MzPq7jyhZ6oIU'")
        return False

    # Test if credentials match expected values
    expected = {
        'developer_id': '811c829f-1159-4a96-b927-112a6ccc5e8e',
        'key_id': 'a76ac2a7-09df-4635-a5cb-86f3edbf3a06',
        'signing_secret': 'OoAaVZ-ij_r4c0kM0kJTg7qOB7fP8MzPq7jyhZ6oIU'
    }

    matches = {
        'developer_id': developer_id == expected['developer_id'],
        'key_id': key_id == expected['key_id'],
        'signing_secret': signing_secret == expected['signing_secret']
    }

    print("=== CREDENTIAL VERIFICATION ===")
    for key, match in matches.items():
        status = "✅" if match else "❌"
        print(f"{status} {key}: {match}")

    if not all(matches.values()):
        print("\n❌ Credentials don't match expected values!")
        return False

    print("\n✅ All credentials match expected values")

    # Test Django app imports
    print("\n=== TESTING IMPORTS ===")

    try:
        from business.models import Cart, Business
        print("✅ Business models imported")
    except Exception as e:
        print(f"❌ Business models import failed: {e}")
        return False

    try:
        from business.services.doordash_service import DoorDashService
        print("✅ DoorDash service imported")

        service = DoorDashService()
        print("✅ DoorDash service initialized")

        # Test JWT generation
        headers = service.get_headers()
        print("✅ JWT generation successful")
        print(f"Authorization header present: {'Authorization' in headers}")

    except Exception as e:
        print(f"❌ DoorDash service error: {e}")
        import traceback
        print(f"Full error: {traceback.format_exc()}")
        return False

    # Test actual API call
    print("\n=== TESTING API CALL ===")

    try:
        test_result = service.get_delivery_quote(
            pickup_address="123 Test Street, Adelaide SA 5000",
            dropoff_address="456 Test Avenue, Adelaide SA 5001",
            order_value=1000  # $10 test order
        )

        print(f"API test result: {test_result}")

        if test_result['success']:
            print("🎉 SUCCESS! Your DoorDash integration is working!")
            print(f"Test delivery fee: ${test_result.get('fee', 0)/100}")
            return True
        else:
            error = test_result.get('error', 'Unknown error')
            status_code = test_result.get('status_code', 'Unknown')

            print(f"❌ API test failed: {error}")
            print(f"Status code: {status_code}")

            if status_code == 401:
                print("\n💡 DIAGNOSIS: Authentication failed")
                print("This means your credentials are not accepted by DoorDash.")
                print("\nPossible reasons:")
                print("1. Credentials are not activated in DoorDash Developer Portal")
                print("2. Credentials are for production, but you're using sandbox URL")
                print("3. Your DoorDash account needs approval")
                print("4. Credentials were copied incorrectly")
                print("\nNext steps:")
                print("1. Go to https://developer.doordash.com/portal/credentials")
                print("2. Check if your credentials show as 'Active'")
                print("3. Generate new sandbox credentials if needed")

            return False

    except Exception as e:
        print(f"❌ API test exception: {e}")
        import traceback
        print(f"Full error: {traceback.format_exc()}")
        return False

if __name__ == '__main__':
    success = check_doordash_environment()
    if success:
        print("\n🎉 All tests passed! Your DoorDash integration should work.")
    else:
        print("\n❌ Tests failed. Please fix the issues above.")