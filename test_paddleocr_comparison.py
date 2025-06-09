#!/usr/bin/env python3
"""
Focused PaddleOCR test to compare extraction with reference CSV data
"""

import sys
import os
import pandas as pd
import re
from pathlib import Path
sys.path.append('.')

def test_paddleocr_vs_csv():
    """Test PaddleOCR extraction against reference CSV data"""
    os.environ['OCR_ENGINE'] = 'PADDLEOCR'
    os.environ['PADDLEOCR_USE_TABLE_RECOGNITION'] = 'True'
    
    from llm_aided_ocr import convert_pdf_to_images, ocr_image_paddleocr
    
    print("=== PADDLEOCR VS CSV COMPARISON TEST ===")
    
    pdf_path = 'test_data/0005852149.pdf'
    csv_path = 'valid_data/0005852149_valid_data.csv'
    
    print(f"\nTesting: {pdf_path}")
    print(f"Reference: {csv_path}")
    
    try:
        ref_df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
    except UnicodeDecodeError:
        ref_df = pd.read_csv(csv_path, sep=';', encoding='latin-1')
    
    print(f"\nReference CSV ({len(ref_df)} rows):")
    print(ref_df.to_string())
    
    images = convert_pdf_to_images(pdf_path, 1, 0)
    if not images:
        print("ERROR: No images extracted")
        return
    
    extracted_text = ocr_image_paddleocr(images[0])
    
    print(f"\nExtracted text ({len(extracted_text)} chars):")
    print("-" * 60)
    print(extracted_text)
    print("-" * 60)
    
    lines = extracted_text.split('\n')
    table_entries = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if re.search(r'\b\d{4}\b', line):
            parts = [part.strip() for part in line.split('|')]
            
            for part in parts:
                if re.search(r'\b\d{4}\b', part):
                    table_entries.append(part)
    
    print(f"\nFound {len(table_entries)} potential table entries:")
    for i, entry in enumerate(table_entries):
        print(f"  {i+1}: {entry}")
    
    ref_descriptions = ref_df['Descricao'].tolist()
    print(f"\nReference descriptions:")
    for i, desc in enumerate(ref_descriptions):
        print(f"  {i+1}: {desc}")
    
    matches = 0
    for ref_desc in ref_descriptions:
        ref_code = re.search(r'\b(\d{4})\b', str(ref_desc))
        if ref_code:
            code = ref_code.group(1)
            for entry in table_entries:
                if code in entry:
                    matches += 1
                    print(f"MATCH: {code} found in '{entry}'")
                    break
    
    accuracy = matches / len(ref_descriptions) if ref_descriptions else 0
    print(f"\nAccuracy: {matches}/{len(ref_descriptions)} = {accuracy:.2%}")
    
    return accuracy

if __name__ == "__main__":
    test_paddleocr_vs_csv()
