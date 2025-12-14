"""
OCR Document Processor
Real OCR integration for documents app using Tesseract or cloud services
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import re

logger = logging.getLogger("streamware.ocr")


@dataclass
class InvoiceData:
    """Extracted invoice data"""
    vendor: str = ""
    nip: str = ""
    invoice_number: str = ""
    date: str = ""
    due_date: str = ""
    amount_net: float = 0.0
    amount_vat: float = 0.0
    amount_gross: float = 0.0
    currency: str = "PLN"
    payment_method: str = ""
    bank_account: str = ""
    raw_text: str = ""
    confidence: float = 0.0


class OCRProcessor:
    """Document OCR processor with invoice data extraction"""
    
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path(__file__).parent.parent.parent / "data"
        self.documents_dir = self.data_dir / "documents"
        self.documents_dir.mkdir(parents=True, exist_ok=True)
        
        # Try to import OCR libraries
        self.tesseract_available = False
        self.pytesseract_available = False
        
        try:
            import pytesseract
            self.pytesseract_available = True
            logger.info("✅ Tesseract OCR available")
        except ImportError:
            logger.warning("⚠️ Tesseract not available")
        
        # Check for Tesseract binary
        try:
            import subprocess
            result = subprocess.run(['tesseract', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                self.tesseract_available = True
                logger.info("✅ Tesseract binary available")
        except (FileNotFoundError, subprocess.SubprocessError):
            logger.warning("⚠️ Tesseract binary not found")
        
        self.ocr_available = self.pytesseract_available and self.tesseract_available
    
    def process_document(self, file_path: str) -> Optional[InvoiceData]:
        """Process document and extract invoice data"""
        if not self.ocr_available:
            logger.error("OCR not available - install Tesseract and pytesseract")
            return None
        
        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return None
        
        try:
            # Extract text using OCR
            text = self._extract_text(file_path)
            if not text:
                logger.warning("No text extracted from document")
                return None
            
            # Parse invoice data
            invoice_data = self._parse_invoice_data(text)
            invoice_data.raw_text = text
            
            logger.info(f"✅ Processed document: {file_path.name}")
            return invoice_data
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return None
    
    def _extract_text(self, file_path: Path) -> str:
        """Extract text from document using OCR"""
        import pytesseract
        from PIL import Image
        
        try:
            # Open image
            image = Image.open(file_path)
            
            # Extract text
            text = pytesseract.image_to_string(image, lang='pol')
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return ""
    
    def _parse_invoice_data(self, text: str) -> InvoiceData:
        """Parse invoice data from OCR text"""
        data = InvoiceData()
        
        # Normalize text
        text = text.upper()
        lines = text.split('\n')
        
        # Extract vendor (usually first line with company name)
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 5 and not any(x in line for x in ['NIP', 'UL.', 'STR.', 'TEL', 'EMAIL']):
                data.vendor = line
                break
        
        # Extract NIP
        nip_patterns = [
            r'NIP[:\s]*(\d{10})',
            r'NIP[:\s]*(\d{3}-\d{3}-\d{2}-\d{2})',
            r'(\d{10})',
        ]
        for pattern in nip_patterns:
            match = re.search(pattern, text)
            if match:
                data.nip = match.group(1).replace('-', '')
                break
        
        # Extract invoice number
        invoice_patterns = [
            r'FAKTURA\s+(?:VAT\s+)?NR[:\s]*(\S+)',
            r'INVOICE\s+NO[:\s]*(\S+)',
            r'NR[:\s]*(\d{1,}/\d{4})',
        ]
        for pattern in invoice_patterns:
            match = re.search(pattern, text)
            if match:
                data.invoice_number = match.group(1)
                break
        
        # Extract dates
        date_patterns = [
            r'DATA\s+SPRZEDAŻY[:\s]*(\d{4}-\d{2}-\d{2})',
            r'DATA\s+WYSTAWIENIA[:\s]*(\d{4}-\d{2}-\d{2})',
            r'(\d{4}-\d{2}-\d{2})',
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                data.date = match.group(1)
                break
        
        # Extract due date
        due_patterns = [
            r'TERMIN\s+PŁATNOŚCI[:\s]*(\d{4}-\d{2}-\d{2})',
            r'DUE\s+DATE[:\s]*(\d{4}-\d{2}-\d{2})',
        ]
        for pattern in due_patterns:
            match = re.search(pattern, text)
            if match:
                data.due_date = match.group(1)
                break
        
        # Extract amounts (look for PLN, EUR, USD)
        amount_patterns = [
            r'RAZEM[:\s]*(\d+[.,]\d{2})\s*PLN',
            r'TOTAL[:\s]*(\d+[.,]\d{2})\s*PLN',
            r'(\d+[.,]\d{2})\s*PLN',
        ]
        
        for pattern in amount_patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Take the largest amount as gross total
                amounts = [float(m.replace(',', '.')) for m in matches]
                data.amount_gross = max(amounts)
                break
        
        # Extract bank account
        account_patterns = [
            r'KONTO[:\s]*(\d{2}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4})',
            r'ACCOUNT[:\s]*(\d{2}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4})',
        ]
        for pattern in account_patterns:
            match = re.search(pattern, text)
            if match:
                data.bank_account = match.group(1).replace(' ', '')
                break
        
        # Set confidence based on how much data we extracted
        extracted_fields = sum([
            bool(data.vendor),
            bool(data.nip),
            bool(data.invoice_number),
            bool(data.date),
            bool(data.amount_gross) > 0
        ])
        data.confidence = extracted_fields / 5.0
        
        return data
    
    def save_document(self, file_path: str, invoice_data: InvoiceData) -> str:
        """Save processed document data"""
        import json
        
        # Generate document ID
        doc_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Save to documents directory
        doc_file = self.documents_dir / f"{doc_id}.json"
        
        document_data = {
            "id": doc_id,
            "filename": Path(file_path).name,
            "vendor": invoice_data.vendor,
            "nip": invoice_data.nip,
            "invoice_number": invoice_data.invoice_number,
            "date": invoice_data.date,
            "due_date": invoice_data.due_date,
            "amount_net": invoice_data.amount_net,
            "amount_vat": invoice_data.amount_vat,
            "amount_gross": invoice_data.amount_gross,
            "currency": invoice_data.currency,
            "payment_method": invoice_data.payment_method,
            "bank_account": invoice_data.bank_account,
            "status": "pending",
            "confidence": invoice_data.confidence,
            "processed_at": datetime.now().isoformat(),
            "raw_text": invoice_data.raw_text[:1000]  # Truncate for storage
        }
        
        doc_file.write_text(json.dumps(document_data, indent=2), encoding='utf-8')
        
        logger.info(f"💾 Saved document: {doc_id}")
        return doc_id
    
    def get_all_documents(self) -> List[Dict]:
        """Get all processed documents"""
        import json
        
        documents = []
        for doc_file in self.documents_dir.glob("*.json"):
            try:
                data = json.loads(doc_file.read_text(encoding='utf-8'))
                documents.append(data)
            except Exception as e:
                logger.error(f"Error reading document {doc_file}: {e}")
        
        # Sort by date (newest first)
        documents.sort(key=lambda x: x.get('processed_at', ''), reverse=True)
        return documents
    
    def get_document_by_id(self, doc_id: str) -> Optional[Dict]:
        """Get specific document by ID"""
        import json
        
        doc_file = self.documents_dir / f"{doc_id}.json"
        if doc_file.exists():
            try:
                return json.loads(doc_file.read_text(encoding='utf-8'))
            except Exception as e:
                logger.error(f"Error reading document {doc_id}: {e}")
        return None
    
    def update_document_status(self, doc_id: str, status: str) -> bool:
        """Update document status"""
        doc = self.get_document_by_id(doc_id)
        if doc:
            doc['status'] = status
            doc['updated_at'] = datetime.now().isoformat()
            
            import json
            doc_file = self.documents_dir / f"{doc_id}.json"
            doc_file.write_text(json.dumps(doc, indent=2), encoding='utf-8')
            return True
        return False


# Singleton
ocr_processor = OCRProcessor()


def process_document_file(file_path: str) -> Optional[str]:
    """Process document file and return document ID"""
    invoice_data = ocr_processor.process_document(file_path)
    if invoice_data:
        return ocr_processor.save_document(file_path, invoice_data)
    return None


def get_documents_list() -> List[Dict]:
    """Get all documents"""
    return ocr_processor.get_all_documents()


def get_document_details(doc_id: str) -> Optional[Dict]:
    """Get document details"""
    return ocr_processor.get_document_by_id(doc_id)
