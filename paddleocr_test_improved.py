#!/usr/bin/env python3
"""
Improved PaddleOCR Test Class with Enhanced Parsing Logic
Addresses specific issues found in initial testing to achieve 100% accuracy
"""

import sys
import os
import pandas as pd
import re
from pathlib import Path
import logging
sys.path.append('.')

class ImprovedPaddleOCRTester:
    """Enhanced test class with improved parsing logic for payroll documents"""
    
    def __init__(self):
        self.test_data_dir = Path("test_data")
        self.valid_data_dir = Path("valid_data")
        self.results = {}
        
        os.environ['OCR_ENGINE'] = 'PADDLEOCR'
        os.environ['PADDLEOCR_USE_TABLE_RECOGNITION'] = 'True'
        
        logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        print("Improved PaddleOCR Tester initialized")
    
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
    
    def parse_payroll_table_enhanced(self, extracted_text):
        """Enhanced parsing logic that addresses specific issues found in testing"""
        parts = [part.strip() for part in extracted_text.split('|')]
        
        payroll_entries = []
        current_entry = {}
        
        pending_values = []
        
        for i, part in enumerate(parts):
            code_match = re.match(r'^(\d{4})\s+(.+)', part)
            if code_match:
                if current_entry and pending_values:
                    self._assign_pending_values(current_entry, pending_values)
                    pending_values = []
                
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
            
            elif current_entry:
                if part.lower() in ['dias', 'horas', '%', 'parcelas']:
                    current_entry['Unidade'] = part
                
                elif re.match(r'^\d+/\d+$', part):
                    current_entry['Quantidade'] = part
                
                elif re.match(r'^\d+([,\.]\d+)?$', part):
                    pending_values.append(part)
        
        if current_entry:
            if pending_values:
                self._assign_pending_values(current_entry, pending_values)
            payroll_entries.append(current_entry)
        
        print(f"Parsed {len(payroll_entries)} payroll entries with enhanced logic")
        return payroll_entries
    
    def _assign_pending_values(self, entry, values):
        """Assign pending numeric values to appropriate columns based on payroll logic"""
        desc_lower = entry['Descricao'].lower()
        
        if 'salario' in desc_lower or 'salário' in desc_lower:
            if len(values) >= 2:
                entry['Quantidade'] = values[0]
                largest_val = max(values[1:], key=lambda x: float(x.replace(',', '.')))
                entry['Vantagens'] = largest_val
            elif len(values) == 1:
                try:
                    amount = float(values[0].replace(',', '.'))
                    if amount > 1000:
                        entry['Vantagens'] = values[0]
                    else:
                        entry['Quantidade'] = values[0]
                except ValueError:
                    entry['Quantidade'] = values[0]
        
        elif any(keyword in desc_lower for keyword in ['gratificação', 'gratificacao', 'auxilio', 'auxílio']):
            if len(values) >= 2:
                entry['Quantidade'] = values[0]
                entry['Vantagens'] = values[1]
            elif len(values) == 1:
                try:
                    amount = float(values[0].replace(',', '.'))
                    if amount > 100:  # Likely an amount
                        entry['Vantagens'] = values[0]
                    else:  # Likely a quantity/percentage
                        entry['Quantidade'] = values[0]
                except ValueError:
                    entry['Quantidade'] = values[0]
        
        elif any(keyword in desc_lower for keyword in ['imposto', 'banco', 'seguro', 'fundo']):
            if len(values) >= 1:
                largest_val = max(values, key=lambda x: float(x.replace(',', '.')) if re.match(r'^\d+([,\.]\d+)?$', x) else 0)
                entry['Descontos'] = largest_val
                other_vals = [v for v in values if v != largest_val]
                if other_vals and not entry['Quantidade']:
                    entry['Quantidade'] = other_vals[0]
        
        else:
            if len(values) >= 1:
                entry['Quantidade'] = values[0]
            if len(values) >= 2:
                entry['Vantagens'] = values[1]
    
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
        """Enhanced comparison with detailed field-by-field analysis"""
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
        
        code_matches = len(set(ref_codes) & set(extracted_codes))
        code_accuracy = code_matches / len(ref_codes) if ref_codes else 0
        
        field_matches = 0
        total_fields = 0
        
        for i, ref_row in reference_df.iterrows():
            ref_code = re.search(r'^(\d{4})', str(ref_row['Descricao']))
            if ref_code:
                ref_code = ref_code.group(1)
                for ext_entry in extracted_entries:
                    ext_code = re.search(r'^(\d{4})', ext_entry.get('Descricao', ''))
                    if ext_code and ext_code.group(1) == ref_code:
                        for field in ['Quantidade', 'Unidade', 'Vantagens', 'Descontos']:
                            total_fields += 1
                            ref_val = str(ref_row[field]) if pd.notna(ref_row[field]) else ''
                            ext_val = ext_entry.get(field, '')
                            
                            ref_val_norm = ref_val.replace(' ', '').lower()
                            ext_val_norm = ext_val.replace(' ', '').lower()
                            
                            if ref_val_norm == ext_val_norm or (not ref_val_norm and not ext_val_norm):
                                field_matches += 1
                        break
        
        field_accuracy = field_matches / total_fields if total_fields > 0 else 0
        
        print(f"Code matching accuracy: {code_matches}/{len(ref_codes)} = {code_accuracy:.2%}")
        print(f"Field matching accuracy: {field_matches}/{total_fields} = {field_accuracy:.2%}")
        
        return code_accuracy, field_accuracy, code_matches, len(ref_codes)
    
    def test_single_pdf(self, pdf_name):
        """Test extraction for a single PDF file with enhanced analysis"""
        print(f"\n{'='*60}")
        print(f"TESTING {pdf_name} (ENHANCED)")
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
            
            payroll_entries = self.parse_payroll_table_enhanced(extracted_text)
            
            csv_lines = self.convert_to_csv_format(payroll_entries)
            
            code_acc, field_acc, code_matches, total_codes = self.compare_with_reference(payroll_entries, reference_df)
            
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
                'code_accuracy': code_acc,
                'field_accuracy': field_acc,
                'code_matches': code_matches,
                'total_codes': total_codes
            }
            
            self.results[pdf_name] = result
            return result
            
        except Exception as e:
            print(f"ERROR testing {pdf_name}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def run_all_tests(self):
        """Run enhanced tests on all available PDF files"""
        print("Starting enhanced PaddleOCR payroll tests...")
        
        test_files = ["0005852149", "0007226055"]
        total_code_accuracy = 0
        total_field_accuracy = 0
        successful_tests = 0
        
        for pdf_name in test_files:
            result = self.test_single_pdf(pdf_name)
            if result:
                total_code_accuracy += result['code_accuracy']
                total_field_accuracy += result['field_accuracy']
                successful_tests += 1
        
        print(f"\n{'='*60}")
        print(f"ENHANCED RESULTS SUMMARY")
        print(f"{'='*60}")
        
        if successful_tests > 0:
            avg_code_accuracy = total_code_accuracy / successful_tests
            avg_field_accuracy = total_field_accuracy / successful_tests
            
            print(f"Tests completed: {successful_tests}/{len(test_files)}")
            print(f"Average code accuracy: {avg_code_accuracy:.2%}")
            print(f"Average field accuracy: {avg_field_accuracy:.2%}")
            print(f"Overall accuracy: {(avg_code_accuracy + avg_field_accuracy) / 2:.2%}")
            
            for pdf_name, result in self.results.items():
                if result:
                    print(f"  {pdf_name}:")
                    print(f"    Code accuracy: {result['code_accuracy']:.2%}")
                    print(f"    Field accuracy: {result['field_accuracy']:.2%}")
        else:
            print("No tests completed successfully")
        
        return self.results

def main():
    """Main function to run the enhanced payroll tester"""
    tester = ImprovedPaddleOCRTester()
    results = tester.run_all_tests()
    
    return results

if __name__ == "__main__":
    main()
