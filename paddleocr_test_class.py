#!/usr/bin/env python3
"""
Comprehensive PaddleOCR Test Class for Payroll Document Extraction
Tests extraction against reference CSV data and iteratively refines the implementation
"""

import sys
import os
import pandas as pd
import re
from pathlib import Path
import logging
sys.path.append('.')

class PaddleOCRPayrollTester:
    """Test class for validating PaddleOCR extraction against reference CSV data"""
    
    def __init__(self):
        self.test_data_dir = Path("test_data")
        self.valid_data_dir = Path("valid_data")
        self.results = {}
        
        os.environ['OCR_ENGINE'] = 'PADDLEOCR'
        os.environ['PADDLEOCR_USE_TABLE_RECOGNITION'] = 'True'
        
        logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        print("PaddleOCR Payroll Tester initialized")
    
    def load_reference_csv(self, csv_path):
        """Load reference CSV data with proper encoding"""
        try:
            df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(csv_path, sep=';', encoding='latin-1')
        
        print(f"Loaded reference CSV: {csv_path.name} with {len(df)} rows")
        return df
    
    def extract_payroll_data(self, pdf_path):
        """Extract payroll data from PDF using PaddleOCR"""
        from llm_aided_ocr import convert_pdf_to_images, ocr_image_paddleocr
        
        print(f"Extracting from: {pdf_path.name}")
        
        images = convert_pdf_to_images(str(pdf_path), 1, 0)
        if not images:
            raise ValueError(f"No images extracted from {pdf_path}")
        
        extracted_text = ocr_image_paddleocr(images[0])
        print(f"Extracted {len(extracted_text)} characters")
        
        return extracted_text
    
    def parse_payroll_table(self, extracted_text):
        """Parse extracted text into structured payroll table data"""
        parts = [part.strip() for part in extracted_text.split('|')]
        
        payroll_entries = []
        current_entry = {}
        
        for i, part in enumerate(parts):
            code_match = re.match(r'^(\d{4})\s+(.+)', part)
            if code_match:
                if current_entry:
                    payroll_entries.append(current_entry)
                
                code, description = code_match.groups()
                current_entry = {
                    'Descricao': f"{code} - {description}",
                    'Quantidade': '',
                    'Unidade': '',
                    'Vantagens': '',
                    'Descontos': ''
                }
            
            elif current_entry and re.match(r'^\d+([,\.]\d+)?$', part):
                if not current_entry['Quantidade']:
                    current_entry['Quantidade'] = part
                elif not current_entry['Vantagens'] and not current_entry['Descontos']:
                    if any(keyword in current_entry['Descricao'].lower() for keyword in ['imposto', 'banco', 'seguro']):
                        current_entry['Descontos'] = part
                    else:
                        current_entry['Vantagens'] = part
            
            elif current_entry and part.lower() in ['dias', 'horas', '%', 'parcelas']:
                current_entry['Unidade'] = part
            
            elif current_entry and re.match(r'^\d+/\d+$', part):
                current_entry['Quantidade'] = part
        
        if current_entry:
            payroll_entries.append(current_entry)
        
        print(f"Parsed {len(payroll_entries)} payroll entries")
        return payroll_entries
    
    def convert_to_csv_format(self, payroll_entries):
        """Convert payroll entries to CSV format matching reference structure"""
        csv_lines = []
        
        for entry in payroll_entries:
            line = ';'.join([
                entry.get('Descricao', ''),
                entry.get('Quantidade', ''),
                entry.get('Unidade', ''),
                entry.get('Vantagens', ''),
                entry.get('Descontos', '')
            ])
            csv_lines.append(line)
        
        return csv_lines
    
    def compare_with_reference(self, extracted_entries, reference_df):
        """Compare extracted entries with reference CSV data"""
        ref_codes = []
        for desc in reference_df['Descricao']:
            code_match = re.search(r'^(\d{4})', str(desc))
            if code_match:
                ref_codes.append(code_match.group(1))
        
        extracted_codes = []
        for entry in extracted_entries:
            code_match = re.search(r'^(\d{4})', entry.get('Descricao', ''))
            if code_match:
                extracted_codes.append(code_match.group(1))
        
        matches = len(set(ref_codes) & set(extracted_codes))
        total_ref = len(ref_codes)
        accuracy = matches / total_ref if total_ref > 0 else 0
        
        print(f"Code matching accuracy: {matches}/{total_ref} = {accuracy:.2%}")
        
        print("\nDetailed comparison:")
        print("Reference codes:", ref_codes)
        print("Extracted codes:", extracted_codes)
        print("Missing codes:", set(ref_codes) - set(extracted_codes))
        print("Extra codes:", set(extracted_codes) - set(ref_codes))
        
        return accuracy, matches, total_ref
    
    def test_single_pdf(self, pdf_name):
        """Test extraction for a single PDF file"""
        print(f"\n{'='*60}")
        print(f"TESTING {pdf_name}")
        print(f"{'='*60}")
        
        pdf_path = self.test_data_dir / f"{pdf_name}.pdf"
        csv_path = self.valid_data_dir / f"{pdf_name}_valid_data.csv"
        
        if not pdf_path.exists():
            print(f"ERROR: PDF file not found: {pdf_path}")
            return None
        
        if not csv_path.exists():
            print(f"ERROR: Reference CSV not found: {csv_path}")
            return None
        
        try:
            reference_df = self.load_reference_csv(csv_path)
            print("Reference data:")
            print(reference_df.to_string(index=False))
            
            extracted_text = self.extract_payroll_data(pdf_path)
            
            payroll_entries = self.parse_payroll_table(extracted_text)
            
            csv_lines = self.convert_to_csv_format(payroll_entries)
            
            accuracy, matches, total = self.compare_with_reference(payroll_entries, reference_df)
            
            print(f"\nExtracted data in CSV format:")
            print("Descricao;Quantidade;Unidade;Vantagens;Descontos")
            for line in csv_lines:
                print(line)
            
            result = {
                'pdf_path': pdf_path,
                'csv_path': csv_path,
                'extracted_text': extracted_text,
                'payroll_entries': payroll_entries,
                'csv_lines': csv_lines,
                'reference_df': reference_df,
                'accuracy': accuracy,
                'matches': matches,
                'total': total
            }
            
            self.results[pdf_name] = result
            return result
            
        except Exception as e:
            print(f"ERROR testing {pdf_name}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def run_all_tests(self):
        """Run tests on all available PDF files"""
        print("Starting comprehensive PaddleOCR payroll tests...")
        
        test_files = ["0005852149", "0007226055"]
        total_accuracy = 0
        successful_tests = 0
        
        for pdf_name in test_files:
            result = self.test_single_pdf(pdf_name)
            if result:
                total_accuracy += result['accuracy']
                successful_tests += 1
        
        print(f"\n{'='*60}")
        print(f"OVERALL RESULTS")
        print(f"{'='*60}")
        
        if successful_tests > 0:
            avg_accuracy = total_accuracy / successful_tests
            print(f"Tests completed: {successful_tests}/{len(test_files)}")
            print(f"Average accuracy: {avg_accuracy:.2%}")
            
            for pdf_name, result in self.results.items():
                if result:
                    print(f"  {pdf_name}: {result['accuracy']:.2%} ({result['matches']}/{result['total']} codes)")
        else:
            print("No tests completed successfully")
        
        return self.results
    
    def suggest_improvements(self):
        """Analyze results and suggest improvements to extraction logic"""
        print(f"\n{'='*60}")
        print(f"IMPROVEMENT SUGGESTIONS")
        print(f"{'='*60}")
        
        for pdf_name, result in self.results.items():
            if not result:
                continue
            
            accuracy = result['accuracy']
            
            if accuracy < 0.8:
                print(f"\n{pdf_name}: NEEDS IMPROVEMENT ({accuracy:.2%})")
                print("Suggestions:")
                print("  - Improve table structure parsing logic")
                print("  - Enhance text preprocessing and cleaning")
                print("  - Adjust confidence thresholds")
                print("  - Better handling of multi-line entries")
            elif accuracy < 1.0:
                print(f"\n{pdf_name}: GOOD BUT CAN IMPROVE ({accuracy:.2%})")
                print("Suggestions:")
                print("  - Fine-tune parsing patterns")
                print("  - Handle edge cases better")
            else:
                print(f"\n{pdf_name}: EXCELLENT ({accuracy:.2%})")
                print("  - Extraction is working well")

def main():
    """Main function to run the payroll tester"""
    tester = PaddleOCRPayrollTester()
    results = tester.run_all_tests()
    tester.suggest_improvements()
    
    return results

if __name__ == "__main__":
    main()
