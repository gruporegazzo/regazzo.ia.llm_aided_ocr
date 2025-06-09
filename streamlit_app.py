import streamlit as st
import asyncio
import os
import tempfile
import logging
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
import traceback

from llm_aided_ocr import (
    convert_pdf_to_images, 
    ocr_image, 
    process_document, 
    remove_corrected_text_header,
    assess_output_quality,
    download_models,
    USE_LOCAL_LLM,
    API_PROVIDER,
    DEFAULT_LOCAL_MODEL_NAME,
    OPENAI_EMBEDDING_MODEL,
    OCR_ENGINE
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    st.set_page_config(
        page_title="LLM-Aided OCR",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🔍 LLM-Aided OCR")
    st.markdown("Transform your PDF documents with advanced OCR and AI-powered text correction")
    
    st.sidebar.header("⚙️ Configuration")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Upload a PDF file to process with OCR and LLM correction"
    )
    
    if uploaded_file is not None:
        st.sidebar.subheader("📄 Page Processing")
        max_test_pages = st.sidebar.number_input(
            "Max pages to process (0 = all pages)",
            min_value=0,
            value=0,
            help="Set to 0 to process all pages, or specify a number to limit processing"
        )
        
        skip_first_n_pages = st.sidebar.number_input(
            "Skip first N pages",
            min_value=0,
            value=0,
            help="Number of pages to skip from the beginning"
        )
        
        st.sidebar.subheader("🎨 Output Format")
        reformat_as_markdown = st.sidebar.checkbox(
            "Format as Markdown",
            value=True,
            help="Convert the output to well-formatted Markdown"
        )
        
        suppress_headers_and_page_numbers = st.sidebar.checkbox(
            "Remove headers and page numbers",
            value=True,
            help="Automatically remove headers, footers, and page numbers"
        )
        
        st.sidebar.subheader("🔍 OCR Engine")
        ocr_engine = st.sidebar.selectbox(
            "Select OCR Engine",
            ["TESSERACT", "PADDLEOCR"],
            index=0 if OCR_ENGINE.upper() == "TESSERACT" else 1,
            help="Choose between Tesseract (fast) or PaddleOCR (better for tables and complex layouts)"
        )
        
        if ocr_engine == "PADDLEOCR":
            use_table_recognition = st.sidebar.checkbox(
                "Enable table recognition",
                value=True,
                help="Detect and preserve table structure in documents"
            )
            
            enhanced_payroll = st.sidebar.checkbox(
                "Enhanced Payroll Parsing",
                value=False,
                help="Enable specialized parsing for government payroll documents (contra-cheques)"
            )
        
        st.sidebar.subheader("🤖 LLM Configuration")
        if USE_LOCAL_LLM:
            st.sidebar.info(f"Using Local LLM: {DEFAULT_LOCAL_MODEL_NAME}")
        else:
            st.sidebar.info(f"Using API: {API_PROVIDER}")
            if API_PROVIDER == "OPENAI":
                st.sidebar.info(f"Embedding Model: {OPENAI_EMBEDDING_MODEL}")
        
        if st.button("🚀 Process Document", type="primary"):
            import os
            os.environ['OCR_ENGINE'] = ocr_engine
            if ocr_engine == "PADDLEOCR":
                os.environ['PADDLEOCR_USE_TABLE_RECOGNITION'] = str(use_table_recognition)
                os.environ['PADDLEOCR_ENHANCED_PAYROLL_PARSING'] = str(enhanced_payroll)
            
            process_document_streamlit(
                uploaded_file,
                max_test_pages,
                skip_first_n_pages,
                reformat_as_markdown,
                suppress_headers_and_page_numbers
            )
    else:
        st.info("👆 Please upload a PDF file to get started")
        
        st.subheader("✨ Features")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **📄 PDF Processing**
            - Convert PDF pages to images
            - Advanced OCR with Tesseract or PaddleOCR
            - Table structure recognition (PaddleOCR)
            - Configurable page range processing
            """)
            
        with col2:
            st.markdown("""
            **🤖 AI Enhancement**
            - LLM-powered error correction
            - Smart text formatting
            - Quality assessment
            """)

def process_document_streamlit(uploaded_file, max_test_pages, skip_first_n_pages, reformat_as_markdown, suppress_headers_and_page_numbers):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        temp_pdf_path = tmp_file.name
    
    try:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🔧 Initializing...")
        if USE_LOCAL_LLM:
            with st.spinner("Downloading model (if needed)..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                _, download_status = loop.run_until_complete(download_models())
                st.success(f"Model status: {download_status}")
                loop.close()
        
        progress_bar.progress(10)
        
        status_text.text("📄 Converting PDF to images...")
        list_of_scanned_images = convert_pdf_to_images(temp_pdf_path, max_test_pages, skip_first_n_pages)
        st.success(f"Converted {len(list_of_scanned_images)} pages to images")
        progress_bar.progress(30)
        
        status_text.text("🔍 Extracting text with OCR...")
        with ThreadPoolExecutor() as executor:
            list_of_extracted_text_strings = list(executor.map(ocr_image, list_of_scanned_images))
        
        raw_ocr_output = "\n".join(list_of_extracted_text_strings)
        st.success("OCR extraction completed")
        progress_bar.progress(50)
        
        status_text.text("🤖 Processing with LLM...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        final_text = loop.run_until_complete(
            process_document(list_of_extracted_text_strings, reformat_as_markdown, suppress_headers_and_page_numbers)
        )
        loop.close()
        
        cleaned_text = remove_corrected_text_header(final_text)
        progress_bar.progress(80)
        
        status_text.text("📊 Assessing quality...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        quality_score, explanation = loop.run_until_complete(assess_output_quality(raw_ocr_output, final_text))
        loop.close()
        
        progress_bar.progress(100)
        status_text.text("✅ Processing completed!")
        
        st.subheader("📋 Results")
        
        if quality_score is not None:
            col1, col2 = st.columns([1, 3])
            with col1:
                st.metric("Quality Score", f"{quality_score}/100")
            with col2:
                st.info(f"**Assessment:** {explanation}")
        
        tab1, tab2 = st.tabs(["🎯 Final Output", "📝 Raw OCR"])
        
        with tab1:
            st.subheader("LLM-Corrected Text")
            if reformat_as_markdown:
                st.markdown(cleaned_text)
            else:
                st.text_area("Processed Text", cleaned_text, height=400)
            
            file_extension = '.md' if reformat_as_markdown else '.txt'
            st.download_button(
                label="📥 Download Processed Text",
                data=cleaned_text,
                file_name=f"{uploaded_file.name.replace('.pdf', '')}_llm_corrected{file_extension}",
                mime="text/markdown" if reformat_as_markdown else "text/plain"
            )
        
        with tab2:
            st.subheader("Raw OCR Output")
            st.text_area("Raw Text", raw_ocr_output, height=400)
            
            st.download_button(
                label="📥 Download Raw OCR",
                data=raw_ocr_output,
                file_name=f"{uploaded_file.name.replace('.pdf', '')}_raw_ocr.txt",
                mime="text/plain"
            )
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("Full traceback:")
        st.code(traceback.format_exc())
    
    finally:
        if os.path.exists(temp_pdf_path):
            os.unlink(temp_pdf_path)

if __name__ == "__main__":
    main()
