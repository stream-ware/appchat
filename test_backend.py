"""
Streamware MVP - Unit Tests
Tests for individual backend components
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from backend.main import (
    VoiceCommandProcessor,
    ViewGenerator,
    ResponseGenerator,
    DataSimulator,
    Document,
    CameraFeed,
    SalesData,
)


class TestVoiceCommandProcessor:
    """Tests for VoiceCommandProcessor"""
    
    def test_recognize_documents_command(self):
        """Test recognition of document-related commands"""
        commands = [
            "Pokaż faktury",
            "pokaż faktury",
            "POKAŻ FAKTURY",
            "zeskanuj fakturę",
            "ile faktur",
            "dokumenty",
        ]
        
        for cmd in commands:
            result = VoiceCommandProcessor.process(cmd)
            assert result["recognized"] == True
            assert result["app_type"] == "documents"
            assert result["confidence"] > 0.5
    
    def test_recognize_cameras_command(self):
        """Test recognition of camera-related commands"""
        commands = [
            "Pokaż kamery",
            "monitoring",
            "gdzie ruch",
            "alerty",
        ]
        
        for cmd in commands:
            result = VoiceCommandProcessor.process(cmd)
            assert result["recognized"] == True
            assert result["app_type"] == "cameras"
    
    def test_recognize_sales_command(self):
        """Test recognition of sales-related commands"""
        commands = [
            "Pokaż sprzedaż",
            "sprzedaż",
            "raport",
            "porównaj regiony",
        ]
        
        for cmd in commands:
            result = VoiceCommandProcessor.process(cmd)
            assert result["recognized"] == True
            assert result["app_type"] == "sales"
    
    def test_recognize_help_command(self):
        """Test recognition of help command"""
        result = VoiceCommandProcessor.process("pomoc")
        assert result["recognized"] == True
        assert result["app_type"] == "system"
        assert result["action"] == "help"
    
    def test_unrecognized_command(self):
        """Test handling of unrecognized commands"""
        result = VoiceCommandProcessor.process("xyz abc 123")
        assert result["recognized"] == False
        assert result["confidence"] == 0.0
    
    def test_partial_match(self):
        """Test partial matching of commands"""
        # Commands containing keywords should be recognized
        result = VoiceCommandProcessor.process("chcę zobaczyć faktury proszę")
        assert result["recognized"] == True
        assert result["app_type"] == "documents"
    
    def test_original_command_preserved(self):
        """Test that original command is preserved in result"""
        cmd = "Pokaż faktury TEST"
        result = VoiceCommandProcessor.process(cmd)
        assert result["original_command"] == cmd


class TestDataSimulator:
    """Tests for DataSimulator"""
    
    def test_generate_documents(self):
        """Test document generation"""
        docs = DataSimulator.generate_documents(5)
        
        assert len(docs) == 5
        for doc in docs:
            assert isinstance(doc, Document)
            assert doc.id
            assert doc.filename
            assert doc.vendor
            assert doc.nip
            assert doc.amount_net > 0
            assert doc.amount_gross > doc.amount_net
            assert doc.status in ["Nowa", "Zweryfikowana", "Do zapłaty", "Zapłacona"]
    
    def test_generate_cameras(self):
        """Test camera generation"""
        cameras = DataSimulator.generate_cameras(4)
        
        assert len(cameras) == 4
        for cam in cameras:
            assert isinstance(cam, CameraFeed)
            assert cam.id
            assert cam.name
            assert cam.status in ["online", "offline"]
            assert cam.objects_detected >= 0
    
    def test_generate_sales(self):
        """Test sales data generation"""
        sales = DataSimulator.generate_sales()
        
        assert len(sales) == 6  # 6 regions
        for s in sales:
            assert isinstance(s, SalesData)
            assert s.region
            assert s.amount > 0
            assert s.transactions > 0
            assert s.top_product


class TestViewGenerator:
    """Tests for ViewGenerator"""
    
    def test_generate_documents_view(self):
        """Test document view generation"""
        view = ViewGenerator.generate("documents", "show_all")
        
        assert view["type"] == "documents"
        assert view["view"] == "table"
        assert "title" in view
        assert "columns" in view
        assert "data" in view
        assert "stats" in view
        assert len(view["data"]) == 8  # Default count
        assert len(view["stats"]) == 4
    
    def test_generate_cameras_view(self):
        """Test camera view generation"""
        view = ViewGenerator.generate("cameras", "show_grid")
        
        assert view["type"] == "cameras"
        assert view["view"] == "matrix"
        assert view["grid"]["columns"] == 2
        assert view["grid"]["rows"] == 2
        assert len(view["cameras"]) == 4
    
    def test_generate_sales_view(self):
        """Test sales view generation"""
        view = ViewGenerator.generate("sales", "show_dashboard")
        
        assert view["type"] == "sales"
        assert view["view"] == "dashboard"
        assert "chart" in view
        assert "table" in view
        assert view["chart"]["type"] == "bar"
        assert len(view["chart"]["labels"]) == 6
    
    def test_generate_help_view(self):
        """Test help view generation"""
        view = ViewGenerator.generate("system", "help")
        
        assert view["type"] == "system"
        assert view["view"] == "help"
        assert "commands" in view
        assert len(view["commands"]) == 6  # 6 categories: documents, cameras, sales, home, analytics, system
    
    def test_generate_empty_view(self):
        """Test empty/welcome view generation"""
        view = ViewGenerator.generate("empty", "")
        
        assert view["type"] == "empty"
        assert view["view"] == "welcome"


class TestResponseGenerator:
    """Tests for ResponseGenerator"""
    
    def test_documents_response(self):
        """Test document response generation"""
        intent = {"recognized": True, "app_type": "documents", "action": "show_all"}
        view = ViewGenerator.generate("documents", "show_all")
        
        response = ResponseGenerator.generate(intent, view)
        
        assert "dokument" in response.lower()
        assert "PLN" in response
    
    def test_cameras_response(self):
        """Test camera response generation"""
        intent = {"recognized": True, "app_type": "cameras", "action": "show_grid"}
        view = ViewGenerator.generate("cameras", "show_grid")
        
        response = ResponseGenerator.generate(intent, view)
        
        assert "kamer" in response.lower()
        assert "online" in response.lower()
    
    def test_sales_response(self):
        """Test sales response generation"""
        intent = {"recognized": True, "app_type": "sales", "action": "show_dashboard"}
        view = ViewGenerator.generate("sales", "show_dashboard")
        
        response = ResponseGenerator.generate(intent, view)
        
        assert "sprzedaż" in response.lower()
        assert "PLN" in response
    
    def test_unrecognized_response(self):
        """Test response for unrecognized command"""
        intent = {"recognized": False, "app_type": "system", "action": "unknown"}
        view = {}
        
        response = ResponseGenerator.generate(intent, view)
        
        assert "nie rozumiem" in response.lower() or "pomoc" in response.lower()


class TestDocumentModel:
    """Tests for Document data model"""
    
    def test_document_fields(self):
        """Test Document has all required fields"""
        doc = Document(
            id="123",
            filename="test.pdf",
            vendor="Test Sp. z o.o.",
            nip="1234567890",
            amount_net=1000.0,
            amount_vat=230.0,
            amount_gross=1230.0,
            date="2024-01-01",
            due_date="2024-01-31",
            status="Nowa",
            scanned_at="2024-01-01 12:00:00"
        )
        
        assert doc.id == "123"
        assert doc.amount_gross == 1230.0
        assert doc.status == "Nowa"


class TestCameraModel:
    """Tests for CameraFeed data model"""
    
    def test_camera_fields(self):
        """Test CameraFeed has all required fields"""
        cam = CameraFeed(
            id="cam_1",
            name="Test Camera",
            location="test_loc",
            status="online",
            objects_detected=2,
            last_motion="12:00:00",
            stream_url="/api/stream/test",
            alerts=["Test alert"]
        )
        
        assert cam.id == "cam_1"
        assert cam.status == "online"
        assert len(cam.alerts) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
