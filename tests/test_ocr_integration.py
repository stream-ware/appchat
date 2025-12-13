#!/usr/bin/env python3
"""
Test OCR integration functionality
"""

import asyncio
import sys
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.integrations.ocr_processor import OCRProcessor, process_document_file, get_documents_list


def create_test_invoice():
    """Create a test invoice image for OCR testing"""
    # Create a simple test image
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        # Try to use a font, fallback to default if not available
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Draw invoice text
    text_lines = [
        "FAKTURA VAT NR 123/2024",
        "",
        "Sprzedawca:",
        "Test Company Sp. z o.o.",
        "ul. Testowa 1",
        "00-123 Warszawa",
        "NIP: 1234567890",
        "",
        "Nabywca:",
        "Client Company Ltd",
        "",
        "Data wystawienia: 2024-01-15",
        "Data sprzedaży: 2024-01-15",
        "Termin płatności: 2024-01-30",
        "",
        "Towar/usługa | Ilość | Cena | Wartość",
        "Test Service | 1 | 1000.00 PLN | 1000.00 PLN",
        "VAT 23% | | | 230.00 PLN",
        "",
        "RAZEM: 1230.00 PLN",
        "",
        "Konto bankowe:",
        "12 3456 7890 1234 5678 9012 3456"
    ]
    
    y_pos = 50
    for line in text_lines:
        draw.text((50, y_pos), line, fill='black', font=font)
        y_pos += 30
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name, 'PNG')
    
    return temp_file.name


async def test_ocr_processor():
    """Test OCR processor functionality"""
    print("🧪 Testing OCR Processor...")
    
    # Create test invoice
    print("📄 Creating test invoice...")
    test_file = create_test_invoice()
    
    try:
        # Initialize OCR processor
        processor = OCRProcessor()
        
        if not processor.ocr_available:
            print("⚠️ OCR not available - install Tesseract")
            print("   sudo apt-get install tesseract-ocr tesseract-ocr-pol")
            print("   pip install pytesseract")
            return False
        
        # Process document
        print("🔍 Processing document...")
        invoice_data = processor.process_document(test_file)
        
        if invoice_data:
            print(f"✅ Document processed successfully")
            print(f"   Vendor: {invoice_data.vendor}")
            print(f"   NIP: {invoice_data.nip}")
            print(f"   Invoice: {invoice_data.invoice_number}")
            print(f"   Amount: {invoice_data.amount_gross} {invoice_data.currency}")
            print(f"   Confidence: {invoice_data.confidence:.2f}")
            
            # Save document
            doc_id = processor.save_document(test_file, invoice_data)
            print(f"💾 Saved as: {doc_id}")
            
            # Retrieve documents
            documents = get_documents_list()
            print(f"📋 Total documents: {len(documents)}")
            
            return True
        else:
            print("❌ Failed to process document")
            return False
    
    finally:
        # Cleanup
        Path(test_file).unlink(missing_ok=True)
    
    return False


async def test_ocr_integration():
    """Test OCR integration with backend"""
    print("🧪 Testing OCR Integration...")
    
    # Create test invoice
    test_file = create_test_invoice()
    
    try:
        # Process using integration function
        doc_id = process_document_file(test_file)
        
        if doc_id:
            print(f"✅ Document processed via integration: {doc_id}")
            
            # Check documents list
            documents = get_documents_list()
            if documents:
                latest = documents[0]
                print(f"   Latest: {latest.get('vendor', 'Unknown')} - {latest.get('amount_gross', 0)} PLN")
            
            return True
        else:
            print("❌ Integration failed")
            return False
    
    finally:
        Path(test_file).unlink(missing_ok=True)
    
    return False


async def main():
    """Run all OCR tests"""
    print("=" * 60)
    print("🧪 OCR INTEGRATION TESTS")
    print("=" * 60)
    
    tests = [
        ("OCR Processor", test_ocr_processor),
        ("OCR Integration", test_ocr_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test in tests:
        print(f"\n📋 {name}:")
        try:
            if await test():
                passed += 1
                print(f"✅ {name} PASSED")
            else:
                print(f"❌ {name} FAILED")
        except Exception as e:
            print(f"❌ {name} ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 SUMMARY: {passed}/{total} tests passed")
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
