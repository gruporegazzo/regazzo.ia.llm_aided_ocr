#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

def test_configuration():
    """Test that OCR configuration is loaded correctly"""
    try:
        from llm_aided_ocr import OCR_ENGINE, PADDLEOCR_LANG, PADDLEOCR_USE_TABLE_RECOGNITION
        print(f'✓ OCR Engine: {OCR_ENGINE}')
        print(f'✓ PaddleOCR Language: {PADDLEOCR_LANG}')
        print(f'✓ Table Recognition: {PADDLEOCR_USE_TABLE_RECOGNITION}')
        return True
    except Exception as e:
        print(f'✗ Configuration test failed: {e}')
        return False

def test_paddleocr_import():
    """Test that PaddleOCR can be imported and initialized"""
    try:
        from llm_aided_ocr import get_paddleocr_instance
        ocr = get_paddleocr_instance()
        print(f'✓ PaddleOCR instance created successfully')
        print(f'✓ OCR instance type: {type(ocr)}')
        return True
    except Exception as e:
        print(f'✗ PaddleOCR import test failed: {e}')
        return False

def test_ocr_function():
    """Test that ocr_image function works with both engines"""
    try:
        from llm_aided_ocr import ocr_image, ocr_image_tesseract, ocr_image_paddleocr
        from PIL import Image
        import numpy as np
        
        test_image = Image.new('RGB', (200, 50), color='white')
        
        tesseract_result = ocr_image_tesseract(test_image)
        print(f'✓ Tesseract OCR function works (result length: {len(tesseract_result)})')
        
        paddleocr_result = ocr_image_paddleocr(test_image)
        print(f'✓ PaddleOCR function works (result length: {len(paddleocr_result)})')
        
        main_result = ocr_image(test_image)
        print(f'✓ Main ocr_image function works (result length: {len(main_result)})')
        
        return True
    except Exception as e:
        print(f'✗ OCR function test failed: {e}')
        return False

if __name__ == "__main__":
    print("Testing OCR Engine Implementation...")
    print("=" * 50)
    
    tests = [
        ("Configuration Loading", test_configuration),
        ("PaddleOCR Import", test_paddleocr_import),
        ("OCR Functions", test_ocr_function)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"Failed: {test_name}")
    
    print(f"\n{'='*50}")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! OCR implementation is working correctly.")
        sys.exit(0)
    else:
        print("✗ Some tests failed. Please check the implementation.")
        sys.exit(1)
