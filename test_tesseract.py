#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

def test_tesseract():
    """Test that Tesseract OCR works"""
    try:
        import pytesseract
        from PIL import Image
        
        test_image = Image.new('RGB', (200, 50), color='white')
        
        result = pytesseract.image_to_string(test_image)
        print(f'✓ Tesseract OCR works (result length: {len(result)})')
        
        from llm_aided_ocr import ocr_image_tesseract
        our_result = ocr_image_tesseract(test_image)
        print(f'✓ Our Tesseract implementation works (result length: {len(our_result)})')
        
        return True
    except Exception as e:
        print(f'✗ Tesseract test failed: {e}')
        return False

if __name__ == "__main__":
    print("Testing Tesseract OCR...")
    print("=" * 40)
    
    if test_tesseract():
        print("✓ Tesseract test passed!")
        sys.exit(0)
    else:
        print("✗ Tesseract test failed!")
        sys.exit(1)
