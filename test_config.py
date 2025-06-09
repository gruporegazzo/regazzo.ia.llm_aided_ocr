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

if __name__ == "__main__":
    print("Testing OCR Configuration...")
    print("=" * 40)
    
    if test_configuration():
        print("✓ Configuration test passed!")
        sys.exit(0)
    else:
        print("✗ Configuration test failed!")
        sys.exit(1)
