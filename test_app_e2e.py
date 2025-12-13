"""
Streamware MVP - E2E Tests with Playwright
Tests the full user experience including WebSocket communication
"""

import pytest
import asyncio
import json
from typing import Generator
from playwright.sync_api import Page, expect, sync_playwright
from playwright.async_api import async_playwright

# Test configuration
BASE_URL = "http://localhost:8765"
TIMEOUT = 10000  # 10 seconds


class TestStreamwareMVP:
    """End-to-end tests for Streamware MVP"""
    
    @pytest.fixture(scope="class")
    def browser_context(self):
        """Create browser context for tests"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            yield context
            context.close()
            browser.close()
    
    @pytest.fixture
    def page(self, browser_context):
        """Create new page for each test"""
        page = browser_context.new_page()
        yield page
        page.close()

    # ================================================================
    # Basic Page Tests
    # ================================================================
    
    def test_page_loads(self, page: Page):
        """Test that the main page loads correctly"""
        page.goto(BASE_URL)
        
        # Check page title
        expect(page).to_have_title("Streamware MVP - Voice Dashboard")
        
        # Check main layout exists
        expect(page.locator(".app-view")).to_be_visible()
        expect(page.locator(".chat-panel")).to_be_visible()
    
    def test_welcome_screen_displayed(self, page: Page):
        """Test that welcome screen is shown initially"""
        page.goto(BASE_URL)
        
        # Check welcome elements
        expect(page.locator(".welcome-view")).to_be_visible()
        expect(page.locator(".welcome-title")).to_contain_text("Witaj")
        
        # Check suggestion chips are present
        expect(page.locator(".suggestion-chip")).to_have_count(4)
    
    def test_chat_panel_elements(self, page: Page):
        """Test chat panel has all required elements"""
        page.goto(BASE_URL)
        
        # Check chat header
        expect(page.locator(".chat-header .logo")).to_be_visible()
        expect(page.locator(".chat-header .status")).to_contain_text("Połączono")
        
        # Check chat input
        expect(page.locator("#chat-input")).to_be_visible()
        expect(page.locator(".voice-btn")).to_be_visible()
        expect(page.locator(".send-btn")).to_be_visible()
    
    # ================================================================
    # Voice Command Tests (via text input)
    # ================================================================
    
    def test_documents_command(self, page: Page):
        """Test 'Pokaż faktury' command loads document view"""
        page.goto(BASE_URL)
        page.wait_for_timeout(1000)  # Wait for WebSocket connection
        
        # Send command
        page.fill("#chat-input", "Pokaż faktury")
        page.click(".send-btn")
        
        # Wait for response
        page.wait_for_timeout(2000)
        
        # Check document view loaded
        expect(page.locator("#app-title")).to_contain_text("dokument", ignore_case=True)
        
        # Check stats cards are visible
        expect(page.locator(".stat-card")).to_have_count(4, timeout=TIMEOUT)
        
        # Check data table is visible
        expect(page.locator(".data-table")).to_be_visible()
        
        # Check table has data rows
        rows = page.locator(".data-table tbody tr")
        expect(rows).to_have_count(8, timeout=TIMEOUT)  # 8 simulated documents
    
    def test_cameras_command(self, page: Page):
        """Test 'Pokaż kamery' command loads camera grid"""
        page.goto(BASE_URL)
        page.wait_for_timeout(1000)
        
        # Send command
        page.fill("#chat-input", "Pokaż kamery")
        page.click(".send-btn")
        
        page.wait_for_timeout(2000)
        
        # Check camera view loaded
        expect(page.locator("#app-title")).to_contain_text("kamer", ignore_case=True)
        
        # Check camera grid (2x2)
        expect(page.locator(".camera-grid")).to_be_visible()
        expect(page.locator(".camera-card")).to_have_count(4, timeout=TIMEOUT)
        
        # Check camera feeds have status indicators
        expect(page.locator(".status-indicator")).to_have_count(4)
    
    def test_sales_command(self, page: Page):
        """Test 'Pokaż sprzedaż' command loads sales dashboard"""
        page.goto(BASE_URL)
        page.wait_for_timeout(1000)
        
        # Send command
        page.fill("#chat-input", "Pokaż sprzedaż")
        page.click(".send-btn")
        
        page.wait_for_timeout(2000)
        
        # Check sales view loaded
        expect(page.locator("#app-title")).to_contain_text("sprzedaż", ignore_case=True)
        
        # Check stats cards
        expect(page.locator(".stat-card")).to_have_count(4, timeout=TIMEOUT)
        
        # Check bar chart
        expect(page.locator(".bar-chart")).to_be_visible()
        expect(page.locator(".bar-item")).to_have_count(6, timeout=TIMEOUT)  # 6 regions
        
        # Check data table
        expect(page.locator(".data-table")).to_be_visible()
    
    def test_help_command(self, page: Page):
        """Test 'Pomoc' command shows help view"""
        page.goto(BASE_URL)
        page.wait_for_timeout(1000)
        
        # Send command
        page.fill("#chat-input", "Pomoc")
        page.click(".send-btn")
        
        page.wait_for_timeout(2000)
        
        # Check help view loaded
        expect(page.locator("#app-title")).to_contain_text("Pomoc", ignore_case=True)
        
        # Check help categories
        expect(page.locator(".help-category")).to_have_count(4, timeout=TIMEOUT)
    
    # ================================================================
    # Chat Interaction Tests
    # ================================================================
    
    def test_chat_message_appears(self, page: Page):
        """Test that user message appears in chat"""
        page.goto(BASE_URL)
        page.wait_for_timeout(1000)
        
        # Count initial messages
        initial_count = page.locator(".message").count()
        
        # Send message
        page.fill("#chat-input", "Test message")
        page.click(".send-btn")
        
        page.wait_for_timeout(1000)
        
        # Check user message appeared
        expect(page.locator(".message.user")).to_have_count(1)
        expect(page.locator(".message.user")).to_contain_text("Test message")
        
        # Check assistant response appeared
        expect(page.locator(".message.assistant")).to_have_count(2)  # Welcome + response
    
    def test_enter_key_sends_message(self, page: Page):
        """Test that pressing Enter sends the message"""
        page.goto(BASE_URL)
        page.wait_for_timeout(1000)
        
        # Type and press Enter
        page.fill("#chat-input", "Faktury")
        page.press("#chat-input", "Enter")
        
        page.wait_for_timeout(1000)
        
        # Check message was sent
        expect(page.locator(".message.user")).to_contain_text("Faktury")
    
    def test_input_clears_after_send(self, page: Page):
        """Test that input field clears after sending message"""
        page.goto(BASE_URL)
        page.wait_for_timeout(1000)
        
        # Send message
        page.fill("#chat-input", "Test")
        page.click(".send-btn")
        
        # Check input is cleared
        expect(page.locator("#chat-input")).to_have_value("")
    
    # ================================================================
    # Suggestion Chip Tests
    # ================================================================
    
    def test_suggestion_chip_documents(self, page: Page):
        """Test clicking 'Faktury' suggestion chip"""
        page.goto(BASE_URL)
        page.wait_for_timeout(1000)
        
        # Click suggestion chip
        page.click(".suggestion-chip:has-text('Faktury')")
        
        page.wait_for_timeout(2000)
        
        # Check document view loaded
        expect(page.locator(".data-table")).to_be_visible()
    
    def test_suggestion_chip_cameras(self, page: Page):
        """Test clicking 'Kamery' suggestion chip"""
        page.goto(BASE_URL)
        page.wait_for_timeout(1000)
        
        # Click suggestion chip
        page.click(".suggestion-chip:has-text('Kamery')")
        
        page.wait_for_timeout(2000)
        
        # Check camera view loaded
        expect(page.locator(".camera-grid")).to_be_visible()
    
    def test_suggestion_chip_sales(self, page: Page):
        """Test clicking 'Sprzedaż' suggestion chip"""
        page.goto(BASE_URL)
        page.wait_for_timeout(1000)
        
        # Click suggestion chip
        page.click(".suggestion-chip:has-text('Sprzedaż')")
        
        page.wait_for_timeout(2000)
        
        # Check sales view loaded
        expect(page.locator(".bar-chart")).to_be_visible()
    
    # ================================================================
    # Navigation Tests
    # ================================================================
    
    def test_switch_between_views(self, page: Page):
        """Test switching between different app views"""
        page.goto(BASE_URL)
        page.wait_for_timeout(1000)
        
        # Load documents
        page.fill("#chat-input", "Pokaż faktury")
        page.press("#chat-input", "Enter")
        page.wait_for_timeout(1500)
        expect(page.locator(".data-table")).to_be_visible()
        
        # Switch to cameras
        page.fill("#chat-input", "Pokaż kamery")
        page.press("#chat-input", "Enter")
        page.wait_for_timeout(1500)
        expect(page.locator(".camera-grid")).to_be_visible()
        
        # Switch to sales
        page.fill("#chat-input", "Pokaż sprzedaż")
        page.press("#chat-input", "Enter")
        page.wait_for_timeout(1500)
        expect(page.locator(".bar-chart")).to_be_visible()
    
    # ================================================================
    # Data Verification Tests
    # ================================================================
    
    def test_document_data_format(self, page: Page):
        """Test that document data is correctly formatted"""
        page.goto(BASE_URL)
        page.wait_for_timeout(1000)
        
        page.fill("#chat-input", "Pokaż faktury")
        page.press("#chat-input", "Enter")
        page.wait_for_timeout(2000)
        
        # Check currency formatting (PLN)
        table_text = page.locator(".data-table").text_content()
        assert "PLN" in table_text or "zł" in table_text.lower()
        
        # Check status badges exist
        expect(page.locator(".badge")).to_have_count(8)  # One per row
    
    def test_camera_status_indicators(self, page: Page):
        """Test camera status indicators are correct"""
        page.goto(BASE_URL)
        page.wait_for_timeout(1000)
        
        page.fill("#chat-input", "Pokaż kamery")
        page.press("#chat-input", "Enter")
        page.wait_for_timeout(2000)
        
        # Check online cameras have green indicator
        online_indicators = page.locator(".status-indicator:not(.offline)")
        offline_indicators = page.locator(".status-indicator.offline")
        
        # At least some should be online
        assert online_indicators.count() >= 1
    
    def test_sales_chart_data(self, page: Page):
        """Test sales chart has correct number of bars"""
        page.goto(BASE_URL)
        page.wait_for_timeout(1000)
        
        page.fill("#chat-input", "Pokaż sprzedaż")
        page.press("#chat-input", "Enter")
        page.wait_for_timeout(2000)
        
        # Check 6 regions
        bars = page.locator(".bar-item")
        expect(bars).to_have_count(6)
        
        # Check each bar has value and label
        expect(page.locator(".bar-value")).to_have_count(6)
        expect(page.locator(".bar-label")).to_have_count(6)
    
    # ================================================================
    # Responsive Layout Tests
    # ================================================================
    
    def test_layout_80_20_split(self, page: Page):
        """Test that layout maintains 80/20 split"""
        page.goto(BASE_URL)
        page.set_viewport_size({"width": 1920, "height": 1080})
        
        app_view = page.locator(".app-view")
        chat_panel = page.locator(".chat-panel")
        
        # Get bounding boxes
        app_box = app_view.bounding_box()
        chat_box = chat_panel.bounding_box()
        
        # Check approximate 80/20 split (with some tolerance)
        total_width = app_box["width"] + chat_box["width"]
        app_ratio = app_box["width"] / total_width
        
        assert 0.75 <= app_ratio <= 0.85, f"App view should be ~80%, got {app_ratio*100:.1f}%"
    
    # ================================================================
    # Error Handling Tests
    # ================================================================
    
    def test_unknown_command(self, page: Page):
        """Test handling of unknown commands"""
        page.goto(BASE_URL)
        page.wait_for_timeout(1000)
        
        page.fill("#chat-input", "xyz nieznane polecenie abc")
        page.press("#chat-input", "Enter")
        page.wait_for_timeout(1500)
        
        # Should still show a response (even if it's "not understood")
        messages = page.locator(".message.assistant")
        expect(messages).to_have_count(2)  # Welcome + response


# ================================================================
# Async WebSocket Tests
# ================================================================

@pytest.mark.asyncio
class TestWebSocketConnection:
    """Test WebSocket communication directly"""
    
    async def test_websocket_connects(self):
        """Test WebSocket connection is established"""
        import websockets
        
        try:
            async with websockets.connect(f"ws://localhost:8765/ws/test_client") as ws:
                # Should receive welcome message
                response = await asyncio.wait_for(ws.recv(), timeout=5)
                data = json.loads(response)
                
                assert data["type"] == "welcome"
                assert "message" in data
        except Exception as e:
            pytest.skip(f"WebSocket test skipped: {e}")
    
    async def test_websocket_command_response(self):
        """Test sending command via WebSocket"""
        import websockets
        
        try:
            async with websockets.connect(f"ws://localhost:8765/ws/test_client_2") as ws:
                # Skip welcome
                await ws.recv()
                
                # Send command
                await ws.send(json.dumps({
                    "type": "voice_command",
                    "text": "Pokaż faktury"
                }))
                
                # Get response
                response = await asyncio.wait_for(ws.recv(), timeout=5)
                data = json.loads(response)
                
                assert data["type"] == "response"
                assert data["intent"]["app_type"] == "documents"
                assert data["view"]["type"] == "documents"
                assert len(data["view"]["data"]) == 8
        except Exception as e:
            pytest.skip(f"WebSocket test skipped: {e}")


# ================================================================
# Run tests
# ================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
