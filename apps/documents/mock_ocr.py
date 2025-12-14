"""
Mock OCR Processor for testing without Tesseract
Provides realistic mock data for invoice processing
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger("streamware.mock_ocr")


@dataclass
class MockInvoiceData:
    """Mock invoice data for testing"""
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


class MockOCRProcessor:
    """Mock OCR processor for testing without real Tesseract"""
    
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path(__file__).parent.parent.parent / "data"
        self.documents_dir = self.data_dir / "documents"
        self.documents_dir.mkdir(parents=True, exist_ok=True)
        
        # Mock invoice templates
        self.mock_vendors = [
            {"name": "ABC Sp. z o.o.", "nip": "1234567890", "account": "12 3456 7890 1234 5678 9012 3456"},
            {"name": "XYZ Services Ltd", "nip": "9876543210", "account": "98 7654 3210 9876 5432 1098 7654"},
            {"name": "Test Company S.A.", "nip": "5556667777", "account": "55 5666 7777 5556 6677 7755"},
        ]
        
        logger.info("✅ Mock OCR Processor initialized")
    
    def process_document(self, file_path: str) -> Optional[MockInvoiceData]:
        """Process document and return mock invoice data"""
        import random
        
        file_path = Path(file_path)
        # For mock OCR, we don't require the actual file to exist
        # Just use the filename for generating mock data
        
        # Generate mock invoice data
        vendor_data = random.choice(self.mock_vendors)
        
        # Generate random but realistic data
        invoice_number = f"FV/{random.randint(1000, 9999)}/2024"
        days_ago = random.randint(1, 30)
        date = datetime.now().replace(day=random.randint(1, 28)).strftime("%Y-%m-%d")
        due_days = random.randint(14, 30)
        due_date = datetime.now().replace(day=random.randint(1, 28)).strftime("%Y-%m-%d")
        
        # Random amounts
        amount_net = round(random.uniform(100, 5000), 2)
        vat_rate = 0.23
        amount_vat = round(amount_net * vat_rate, 2)
        amount_gross = round(amount_net + amount_vat, 2)
        
        # Create invoice data
        invoice_data = MockInvoiceData(
            vendor=vendor_data["name"],
            nip=vendor_data["nip"],
            invoice_number=invoice_number,
            date=date,
            due_date=due_date,
            amount_net=amount_net,
            amount_vat=amount_vat,
            amount_gross=amount_gross,
            currency="PLN",
            payment_method="transfer",
            bank_account=vendor_data["account"],
            raw_text=f"FAKTURA VAT NR {invoice_number}\nSprzedawca: {vendor_data['name']}\nNIP: {vendor_data['nip']}\nKwota: {amount_gross} PLN",
            confidence=random.uniform(0.85, 0.98)
        )
        
        logger.info(f"✅ Mock processed document: {file_path.name}")
        return invoice_data
    
    def save_document(self, file_path: str, invoice_data: MockInvoiceData) -> str:
        """Save processed document data"""
        # Generate document ID
        doc_id = f"mock_doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
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
            "raw_text": invoice_data.raw_text,
            "mock": True  # Mark as mock data
        }
        
        doc_file.write_text(json.dumps(document_data, indent=2), encoding='utf-8')
        
        logger.info(f"💾 Saved mock document: {doc_id}")
        return doc_id
    
    def get_all_documents(self) -> List[Dict]:
        """Get all processed documents"""
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
            
            doc_file = self.documents_dir / f"{doc_id}.json"
            doc_file.write_text(json.dumps(doc, indent=2), encoding='utf-8')
            return True
        return False
    
    def create_sample_documents(self, count: int = 5):
        """Create sample documents for testing"""
        import random
        
        logger.info(f"📄 Creating {count} sample documents...")
        
        for i in range(count):
            # Mock file path
            mock_file = f"sample_invoice_{i+1}.pdf"
            
            # Generate invoice data
            invoice_data = self.process_document(mock_file)
            if invoice_data:
                doc_id = self.save_document(mock_file, invoice_data)
                logger.info(f"   Created: {doc_id}")
        
        logger.info(f"✅ Created {count} sample documents")


# Singleton
mock_ocr_processor = MockOCRProcessor()


def process_document_file_mock(file_path: str) -> Optional[str]:
    """Process document file using mock OCR and return document ID"""
    invoice_data = mock_ocr_processor.process_document(file_path)
    if invoice_data:
        return mock_ocr_processor.save_document(file_path, invoice_data)
    return None


def get_documents_list_mock() -> List[Dict]:
    """Get all documents from mock OCR"""
    return mock_ocr_processor.get_all_documents()


def get_document_details_mock(doc_id: str) -> Optional[Dict]:
    """Get document details from mock OCR"""
    return mock_ocr_processor.get_document_by_id(doc_id)


def create_sample_documents(count: int = 5):
    """Create sample documents for testing"""
    mock_ocr_processor.create_sample_documents(count)
