#!/usr/bin/env python3
"""Test integration of enhanced payroll parsing in main codebase"""

import os
import sys
sys.path.append('.')

def test_enhanced_parsing_integration():
    """Test that enhanced parsing works in main codebase"""
    os.environ['OCR_ENGINE'] = 'PADDLEOCR'
    os.environ['PADDLEOCR_USE_TABLE_RECOGNITION'] = 'True'
    os.environ['PADDLEOCR_ENHANCED_PAYROLL_PARSING'] = 'True'
    
    try:
        from llm_aided_ocr import convert_pdf_to_images, ocr_image_paddleocr
        
        pdf_path = 'test_data/0005852149.pdf'
        if not os.path.exists(pdf_path):
            print(f"✗ Test file not found: {pdf_path}")
            return False
        
        images = convert_pdf_to_images(pdf_path, 1, 0)
        
        if images:
            result = ocr_image_paddleocr(images[0])
            print(f"Enhanced parsing result length: {len(result)}")
            print(f"Sample output:\n{result[:500]}")
            
            if ';' in result:
                print("✓ Enhanced payroll parsing is working")
                return True
            else:
                print("✗ Enhanced payroll parsing may not be working")
                return False
        else:
            print("✗ No images extracted from PDF")
            return False
            
    except Exception as e:
        print(f"✗ Error testing enhanced parsing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_standard_parsing():
    """Test that standard parsing still works"""
    os.environ['OCR_ENGINE'] = 'PADDLEOCR'
    os.environ['PADDLEOCR_USE_TABLE_RECOGNITION'] = 'True'
    os.environ['PADDLEOCR_ENHANCED_PAYROLL_PARSING'] = 'False'
    
    try:
        from llm_aided_ocr import convert_pdf_to_images, ocr_image_paddleocr
        
        pdf_path = 'test_data/0005852149.pdf'
        if not os.path.exists(pdf_path):
            print(f"✗ Test file not found: {pdf_path}")
            return False
        
        images = convert_pdf_to_images(pdf_path, 1, 0)
        
        if images:
            result = ocr_image_paddleocr(images[0])
            print(f"Standard parsing result length: {len(result)}")
            print(f"Sample output:\n{result[:300]}")
            
            if result and len(result) > 0:
                print("✓ Standard parsing is working")
                return True
            else:
                print("✗ Standard parsing failed")
                return False
        else:
            print("✗ No images extracted from PDF")
            return False
            
    except Exception as e:
        print(f"✗ Error testing standard parsing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Testing Enhanced Payroll Parsing Integration ===")
    
    enhanced_result = test_enhanced_parsing_integration()
    print()
    
    print("=== Testing Standard Parsing (Backward Compatibility) ===")
    standard_result = test_standard_parsing()
    print()
    
    if enhanced_result and standard_result:
        print("✓ All integration tests passed!")
    else:
        print("✗ Some integration tests failed")
        sys.exit(1)
