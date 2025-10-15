"""
PDF Text Extraction Utility
Handles PDF parsing with multiple fallback methods including OCR
"""

import PyPDF2
import pdfplumber
from typing import Optional
import tempfile
import os


class PDFExtractor:
    def __init__(self):
        self.min_text_threshold = 100  # Minimum characters for valid extraction
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from PDF using multiple methods with OCR fallback
        """
        text = ""
        
        # Try pdfplumber first (better for complex layouts)
        try:
            text = self._extract_with_pdfplumber(file_path)
            if text and len(text.strip()) > self.min_text_threshold:
                print("✓ Extracted text using pdfplumber")
                return text
        except Exception as e:
            print(f"pdfplumber failed: {e}")
        
        # Fallback to PyPDF2
        try:
            text = self._extract_with_pypdf2(file_path)
            if text and len(text.strip()) > self.min_text_threshold:
                print("✓ Extracted text using PyPDF2")
                return text
        except Exception as e:
            print(f"PyPDF2 failed: {e}")
        
        # Final fallback to OCR (for scanned PDFs or image-based PDFs)
        # try:
        #     print("⚠ Insufficient text extracted, attempting OCR...")
        #     text = self._extract_with_ocr(file_path)
        #     if text and len(text.strip()) > self.min_text_threshold:
        #         print("✓ Extracted text using OCR")
        #         return text
        # except Exception as e:
        #     print(f"OCR extraction failed: {e}")
        
        if not text or len(text.strip()) < self.min_text_threshold:
            raise Exception(
                "Could not extract sufficient text from PDF. "
                "The file may be corrupted, image-only without readable text, or empty."
            )
        
        return text
    
    def _extract_with_pdfplumber(self, file_path: str) -> str:
        """Extract text using pdfplumber (better for tables and layouts)"""
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
        return text.strip()
    
    def _extract_with_pypdf2(self, file_path: str) -> str:
        """Extract text using PyPDF2 (faster, simpler)"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
        return text.strip()
    
    def _extract_with_ocr(self, file_path: str) -> str:
        """
        Extract text using OCR (pytesseract + pdf2image)
        For scanned PDFs or image-based PDFs
        """
        try:
            from pdf2image import convert_from_path
            import pytesseract
            from PIL import Image
        except ImportError:
            raise Exception(
                "OCR dependencies not installed. Install with: "
                "pip install pytesseract pdf2image pillow"
            )
        
        text = ""
        
        # Convert PDF pages to images
        try:
            images = convert_from_path(file_path, dpi=300)  # Higher DPI for better OCR
        except Exception as e:
            raise Exception(f"Failed to convert PDF to images: {e}")
        
        # Run OCR on each page
        for i, image in enumerate(images):
            try:
                print(f"  OCR processing page {i+1}/{len(images)}...")
                
                # Configure tesseract for better accuracy
                custom_config = r'--oem 3 --psm 6'  # LSTM OCR, assume uniform text block
                
                page_text = pytesseract.image_to_string(
                    image,
                    config=custom_config,
                    lang='eng'  # Can add more languages: 'eng+fra+deu'
                )
                
                if page_text:
                    text += f"\n\n--- Page {i+1} ---\n\n{page_text}"
                    
            except Exception as e:
                print(f"  Failed to OCR page {i+1}: {e}")
                continue
        
        return text.strip()
    
    def get_metadata(self, file_path: str) -> dict:
        """Extract PDF metadata"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata = pdf_reader.metadata
                return {
                    "num_pages": len(pdf_reader.pages),
                    "title": metadata.get('/Title', '') if metadata else '',
                    "author": metadata.get('/Author', '') if metadata else '',
                    "subject": metadata.get('/Subject', '') if metadata else '',
                    "creator": metadata.get('/Creator', '') if metadata else '',
                    "producer": metadata.get('/Producer', '') if metadata else ''
                }
        except Exception as e:
            return {"error": str(e)}
    
    def is_scanned_pdf(self, file_path: str) -> bool:
        """
        Detect if PDF is likely scanned (image-based) vs text-based
        """
        try:
            # Try to extract text with PyPDF2
            text = self._extract_with_pypdf2(file_path)
            
            # Get metadata
            metadata = self.get_metadata(file_path)
            num_pages = metadata.get('num_pages', 0)
            
            if num_pages == 0:
                return True
            
            # Calculate average characters per page
            avg_chars_per_page = len(text) / num_pages if num_pages > 0 else 0
            
            # If very few characters per page, likely scanned
            # Typical text PDF has 1000+ characters per page
            return avg_chars_per_page < 100
            
        except Exception:
            return True  # Assume scanned if we can't determine