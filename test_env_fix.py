#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

def test_env_configuration():
    """Test that .env configuration loads without ValueError"""
    try:
        from llm_aided_ocr import OCR_ENGINE, PADDLEOCR_LANG, PADDLEOCR_USE_TABLE_RECOGNITION
        print('✓ Configuration loaded successfully')
        print(f'OCR_ENGINE: {OCR_ENGINE}')
        print(f'PADDLEOCR_LANG: {PADDLEOCR_LANG}')
        print(f'PADDLEOCR_USE_TABLE_RECOGNITION: {PADDLEOCR_USE_TABLE_RECOGNITION}')
        print(f'Type of PADDLEOCR_USE_TABLE_RECOGNITION: {type(PADDLEOCR_USE_TABLE_RECOGNITION)}')
        return True
    except Exception as e:
        print(f'✗ Error loading configuration: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing .env Configuration Fix...")
    print("=" * 50)
    
    if test_env_configuration():
        print("✓ .env configuration test passed!")
        sys.exit(0)
    else:
        print("✗ .env configuration test failed!")
        sys.exit(1)
