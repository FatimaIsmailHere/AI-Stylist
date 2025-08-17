#!/usr/bin/env python3
"""Test script to verify the upload functionality works"""

import requests
import tempfile
from PIL import Image
import numpy as np

def create_test_image():
    """Create a simple test image"""
    # Create a simple RGB image (300x400 pixels)
    img_array = np.random.randint(0, 255, (400, 300, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    img.save(temp_file.name, 'JPEG')
    return temp_file.name

def test_upload():
    """Test the upload endpoint"""
    try:
        # Create test image
        image_path = create_test_image()
        
        # Upload the image
        with open(image_path, 'rb') as f:
            files = {'file': ('test_image.jpg', f, 'image/jpeg')}
            data = {'user_id': 1}
            
            response = requests.post('http://localhost:5000/upload', files=files, data=data)
            
        print(f"Upload response status: {response.status_code}")
        print(f"Upload response: {response.json()}")
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                outfit_id = result['outfit_id']
                print(f"✓ Upload successful! Outfit ID: {outfit_id}")
                
                # Test suggestions endpoint
                suggestion_data = {'outfit_id': outfit_id}
                suggestions_response = requests.post('http://localhost:5000/generate-suggestions', data=suggestion_data)
                
                print(f"Suggestions response status: {suggestions_response.status_code}")
                print(f"Suggestions response: {suggestions_response.json()}")
                
                return True
            else:
                print(f"✗ Upload failed: {result}")
                return False
        else:
            print(f"✗ HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Test error: {e}")
        return False

if __name__ == "__main__":
    print("Testing AI Stylist Backend...")
    if test_upload():
        print("✓ Backend test completed successfully!")
    else:
        print("✗ Backend test failed!")