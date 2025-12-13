"""
Streamware MVP - Integration Tests
Tests for API endpoints and WebSocket communication
"""

import pytest
import asyncio
import json
from fastapi.testclient import TestClient
from httpx import AsyncClient

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from backend.main import app


class TestHealthEndpoint:
    """Tests for health check endpoint"""
    
    def test_health_returns_200(self):
        """Test health endpoint returns 200"""
        with TestClient(app) as client:
            response = client.get("/api/health")
            assert response.status_code == 200
    
    def test_health_returns_status(self):
        """Test health endpoint returns status field"""
        with TestClient(app) as client:
            response = client.get("/api/health")
            data = response.json()
            assert data["status"] == "healthy"
            assert "timestamp" in data


class TestCommandEndpoint:
    """Tests for command processing endpoint"""
    
    def test_command_endpoint_exists(self):
        """Test command endpoint is accessible"""
        with TestClient(app) as client:
            response = client.post("/api/command", json={"text": "test"})
            assert response.status_code == 200
    
    def test_documents_command(self):
        """Test documents command processing"""
        with TestClient(app) as client:
            response = client.post("/api/command", json={"text": "Pokaż faktury"})
            data = response.json()
            
            assert data["intent"]["app_type"] == "documents"
            assert data["view"]["type"] == "documents"
            assert len(data["view"]["data"]) > 0
    
    def test_cameras_command(self):
        """Test cameras command processing"""
        with TestClient(app) as client:
            response = client.post("/api/command", json={"text": "Pokaż kamery"})
            data = response.json()
            
            assert data["intent"]["app_type"] == "cameras"
            assert data["view"]["type"] == "cameras"
            assert len(data["view"]["cameras"]) == 4
    
    def test_sales_command(self):
        """Test sales command processing"""
        with TestClient(app) as client:
            response = client.post("/api/command", json={"text": "Pokaż sprzedaż"})
            data = response.json()
            
            assert data["intent"]["app_type"] == "sales"
            assert data["view"]["type"] == "sales"
            assert "chart" in data["view"]
    
    def test_help_command(self):
        """Test help command processing"""
        with TestClient(app) as client:
            response = client.post("/api/command", json={"text": "Pomoc"})
            data = response.json()
            
            assert data["intent"]["app_type"] == "system"
            assert data["view"]["view"] == "help"
    
    def test_response_text_generated(self):
        """Test that response text is generated"""
        with TestClient(app) as client:
            response = client.post("/api/command", json={"text": "Pokaż faktury"})
            data = response.json()
            
            assert "response" in data
            assert len(data["response"]) > 0
    
    def test_intent_confidence(self):
        """Test that confidence score is returned"""
        with TestClient(app) as client:
            response = client.post("/api/command", json={"text": "Pokaż faktury"})
            data = response.json()
            
            assert "confidence" in data["intent"]
            assert 0 <= data["intent"]["confidence"] <= 1


class TestWebSocketEndpoint:
    """Tests for WebSocket communication"""
    
    def test_websocket_connection(self):
        """Test WebSocket connection is established"""
        with TestClient(app) as client:
            with client.websocket_connect("/ws/test_client") as ws:
                # Should receive welcome message
                data = ws.receive_json()
                assert data["type"] == "welcome"
    
    def test_websocket_voice_command(self):
        """Test sending voice command via WebSocket"""
        with TestClient(app) as client:
            with client.websocket_connect("/ws/test_client_2") as ws:
                # Skip welcome
                ws.receive_json()
                
                # Send command
                ws.send_json({
                    "type": "voice_command",
                    "text": "Pokaż faktury"
                })
                
                # Receive response
                data = ws.receive_json()
                
                assert data["type"] == "response"
                assert data["intent"]["app_type"] == "documents"
                assert "view" in data
                assert "response_text" in data
    
    def test_websocket_multiple_commands(self):
        """Test sending multiple commands in sequence"""
        with TestClient(app) as client:
            with client.websocket_connect("/ws/test_client_3") as ws:
                ws.receive_json()  # Welcome
                
                commands = ["Pokaż faktury", "Pokaż kamery", "Pokaż sprzedaż"]
                expected_types = ["documents", "cameras", "sales"]
                
                for cmd, expected in zip(commands, expected_types):
                    ws.send_json({"type": "voice_command", "text": cmd})
                    data = ws.receive_json()
                    assert data["view"]["type"] == expected
    
    def test_websocket_action_message(self):
        """Test action message handling"""
        with TestClient(app) as client:
            with client.websocket_connect("/ws/test_client_4") as ws:
                ws.receive_json()  # Welcome
                
                # First load a view
                ws.send_json({"type": "voice_command", "text": "Pokaż faktury"})
                ws.receive_json()
                
                # Send action
                ws.send_json({
                    "type": "action",
                    "action_id": "refresh",
                    "app_type": "documents"
                })
                
                data = ws.receive_json()
                assert data["type"] == "view_update"


class TestViewDataStructure:
    """Tests for view data structure integrity"""
    
    def test_documents_view_structure(self):
        """Test documents view has correct structure"""
        with TestClient(app) as client:
            response = client.post("/api/command", json={"text": "Pokaż faktury"})
            view = response.json()["view"]
            
            # Check required fields
            assert "type" in view
            assert "view" in view
            assert "title" in view
            assert "columns" in view
            assert "data" in view
            assert "stats" in view
            assert "actions" in view
            
            # Check columns structure
            for col in view["columns"]:
                assert "key" in col
                assert "label" in col
            
            # Check data structure
            for row in view["data"]:
                assert "id" in row
                assert "vendor" in row
                assert "amount_gross" in row
            
            # Check stats structure
            for stat in view["stats"]:
                assert "label" in stat
                assert "value" in stat
                assert "icon" in stat
    
    def test_cameras_view_structure(self):
        """Test cameras view has correct structure"""
        with TestClient(app) as client:
            response = client.post("/api/command", json={"text": "Pokaż kamery"})
            view = response.json()["view"]
            
            assert "grid" in view
            assert view["grid"]["columns"] == 2
            assert view["grid"]["rows"] == 2
            
            assert "cameras" in view
            for cam in view["cameras"]:
                assert "id" in cam
                assert "name" in cam
                assert "status" in cam
                assert "objects_detected" in cam
    
    def test_sales_view_structure(self):
        """Test sales view has correct structure"""
        with TestClient(app) as client:
            response = client.post("/api/command", json={"text": "Pokaż sprzedaż"})
            view = response.json()["view"]
            
            assert "chart" in view
            assert view["chart"]["type"] == "bar"
            assert "labels" in view["chart"]
            assert "datasets" in view["chart"]
            
            assert "table" in view
            assert "columns" in view["table"]
            assert "data" in view["table"]


class TestErrorHandling:
    """Tests for error handling"""
    
    def test_empty_command(self):
        """Test handling of empty command"""
        with TestClient(app) as client:
            response = client.post("/api/command", json={"text": ""})
            assert response.status_code == 200
            data = response.json()
            assert data["intent"]["recognized"] == False
    
    def test_invalid_json(self):
        """Test handling of invalid JSON"""
        with TestClient(app) as client:
            response = client.post(
                "/api/command",
                content="not json",
                headers={"Content-Type": "application/json"}
            )
            assert response.status_code == 422  # Validation error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
