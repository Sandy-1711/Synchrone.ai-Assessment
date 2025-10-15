import PyPDF2
import pdfplumber
from typing import Optional


class PDFExtractor:
    def extract_text(self, file_path: str) -> str:
        text = ""
        print(file_path)
        # Try pdfplumber first (better for complex layouts)
        try:
            text = self._extract_with_pdfplumber(file_path)
            print("USING PDFPLUMBER")
            print(text)
            if text and len(text.strip()) > 100:
                return text
        except Exception as e:
            print(f"pdfplumber failed: {e}")

        # Fallback to PyPDF2
        try:
            text = self._extract_with_pypdf2(file_path)
            print("USING PyPDF2")
            print(text)
            if text and len(text.strip()) > 100:
                return text
        except Exception as e:
            print(f"PyPDF2 failed: {e}")

        if not text or len(text.strip()) < 100:
            raise Exception("Could not extract sufficient text from PDF")

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
        with open(file_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
        return text.strip()

    def get_metadata(self, file_path: str) -> dict:
        """Extract PDF metadata"""
        try:
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata = pdf_reader.metadata
                return {
                    "num_pages": len(pdf_reader.pages),
                    "title": metadata.get("/Title", ""),
                    "author": metadata.get("/Author", ""),
                    "subject": metadata.get("/Subject", ""),
                    "creator": metadata.get("/Creator", ""),
                    "producer": metadata.get("/Producer", ""),
                }
        except Exception as e:
            return {"error": str(e)}
