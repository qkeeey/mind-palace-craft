"""
Test script for fal.ai image-to-image object extraction
Tests the extract_object_image endpoint with a sample image
"""

import requests
import sys
from pathlib import Path

# Configuration
API_URL = "http://localhost:8081/extract_object_image"
TEST_IMAGE_PATH = input("Enter path to test room image: ").strip()

def test_extraction():
    """Test object extraction from a room image"""
    
    # Verify file exists
    if not Path(TEST_IMAGE_PATH).exists():
        print(f"❌ Error: File not found: {TEST_IMAGE_PATH}")
        return False
    
    # Get object details from user
    object_name = input("Enter object name (e.g., 'chair'): ").strip()
    object_desc = input("Enter object description (e.g., 'a wooden chair with armrests'): ").strip()
    
    if not object_name or not object_desc:
        print("❌ Error: Object name and description are required")
        return False
    
    print(f"\n🔍 Testing extraction of '{object_name}' from room image...")
    print(f"   Image: {TEST_IMAGE_PATH}")
    print(f"   Description: {object_desc}")
    print(f"   API: {API_URL}\n")
    
    # Prepare request
    try:
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'room_image': f}
            data = {
                'object_name': object_name,
                'object_description': object_desc
            }
            
            print("📤 Sending request to API...")
            response = requests.post(API_URL, files=files, data=data, timeout=180)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    image_url = result.get('image_url')
                    print(f"\n✅ SUCCESS!")
                    print(f"   Object extracted: {object_name}")
                    print(f"   Image URL: {image_url}")
                    print(f"\n📝 You can now view the extracted object at:")
                    print(f"   {image_url}\n")
                    return True
                else:
                    error = result.get('error', 'Unknown error')
                    print(f"\n❌ FAILED: {error}")
                    return False
            else:
                print(f"\n❌ HTTP Error {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Detail: {error_data.get('detail', 'No details')}")
                except:
                    print(f"   Response: {response.text}")
                return False
                
    except FileNotFoundError:
        print(f"\n❌ Error: File not found: {TEST_IMAGE_PATH}")
        return False
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Error: Could not connect to API at {API_URL}")
        print("   Is the backend server running?")
        print("   Start it with: cd alpaca && python api_server.py")
        return False
    except requests.exceptions.Timeout:
        print(f"\n❌ Error: Request timed out (>180s)")
        print("   The fal.ai API might be slow or overloaded")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 Fal.AI Object Extraction Test")
    print("=" * 60)
    print("This script tests the /extract_object_image endpoint")
    print("Make sure the backend server is running on port 8081\n")
    
    if not TEST_IMAGE_PATH:
        print("❌ No image path provided. Exiting.")
        return
    
    success = test_extraction()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ TEST PASSED")
        print("=" * 60)
        print("\n💡 Tips:")
        print("   - Check the extracted image URL in your browser")
        print("   - If quality is poor, try:")
        print("     • Better room lighting")
        print("     • Higher resolution photo")
        print("     • More specific object description")
        sys.exit(0)
    else:
        print("❌ TEST FAILED")
        print("=" * 60)
        print("\n💡 Troubleshooting:")
        print("   1. Make sure backend is running: cd alpaca && python api_server.py")
        print("   2. Check logs in api_server.log and fal_service logs")
        print("   3. Verify fal.ai API key is valid")
        print("   4. Try with a different image or object")
        sys.exit(1)

if __name__ == "__main__":
    main()
