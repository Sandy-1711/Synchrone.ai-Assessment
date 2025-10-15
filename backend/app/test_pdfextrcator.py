import os
from app.utils.pdf_extractor import PDFExtractor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Directory of this file
PDF_PATH = os.path.join(BASE_DIR, "../tests/sample_contract_scanned.pdf")  # Adjust path

extractor = PDFExtractor()
text = extractor.extract_text(PDF_PATH)
print(text[:500])  # Print sample of extracted text
