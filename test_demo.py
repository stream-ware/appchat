#!/usr/bin/env python3
"""
Streamware MVP - Test and Demo Script
Simulates voice commands and demonstrates all features
"""

import asyncio
import json
import sys
import time
from datetime import datetime

try:
    import httpx
    import websockets
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "httpx", "websockets"])
    import httpx
    import websockets


BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"


class StreamwareDemo:
    """Demo and test runner for Streamware MVP"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.client_id = f"test_{int(time.time())}"
        
    async def test_health(self):
        """Test health endpoint"""
        print("\n" + "="*60)
        print("🏥 Testing Health Endpoint")
        print("="*60)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/health")
            data = response.json()
            
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(data, indent=2)}")
            
            assert response.status_code == 200
            assert data["status"] == "healthy"
            print("✅ Health check passed!")
            
    async def test_rest_commands(self):
        """Test REST API command endpoint"""
        print("\n" + "="*60)
        print("🔧 Testing REST API Commands")
        print("="*60)
        
        commands = [
            "Pokaż faktury",
            "Pokaż kamery",
            "Pokaż sprzedaż",
            "Pomoc",
            "Nieznana komenda xyz",
        ]
        
        async with httpx.AsyncClient() as client:
            for cmd in commands:
                print(f"\n📤 Command: '{cmd}'")
                
                response = await client.post(
                    f"{self.base_url}/api/command",
                    json={"text": cmd}
                )
                data = response.json()
                
                print(f"   Intent: {data['intent']['app_type']} / {data['intent']['action']}")
                print(f"   Confidence: {data['intent']['confidence']:.2f}")
                print(f"   Response: {data['response'][:80]}...")
                print(f"   View type: {data['view']['type']}")
                
        print("\n✅ REST API tests passed!")
        
    async def test_websocket_session(self):
        """Test WebSocket real-time communication"""
        print("\n" + "="*60)
        print("🔌 Testing WebSocket Session")
        print("="*60)
        
        ws_full_url = f"{WS_URL}/ws/{self.client_id}"
        print(f"Connecting to: {ws_full_url}")
        
        async with websockets.connect(ws_full_url) as ws:
            # Receive welcome message
            welcome = await ws.recv()
            welcome_data = json.loads(welcome)
            print(f"\n📥 Welcome: {welcome_data['message']}")
            
            # Send test commands
            test_commands = [
                ("Pokaż faktury", "documents"),
                ("Monitoring kamer", "cameras"),
                ("Sprzedaż w tym miesiącu", "sales"),
            ]
            
            for cmd, expected_type in test_commands:
                print(f"\n📤 Sending: '{cmd}'")
                
                await ws.send(json.dumps({
                    "type": "voice_command",
                    "text": cmd
                }))
                
                response = await ws.recv()
                data = json.loads(response)
                
                print(f"   📥 Response type: {data['type']}")
                print(f"   🎯 Intent: {data['intent']['app_type']}")
                print(f"   📊 View: {data['view']['type']}")
                print(f"   🔊 TTS: {data['response_text'][:60]}...")
                
                # Verify correct app type
                assert data['view']['type'] == expected_type, \
                    f"Expected {expected_type}, got {data['view']['type']}"
                
                await asyncio.sleep(0.5)
        
        print("\n✅ WebSocket tests passed!")

    async def run_interactive_demo(self):
        """Run interactive demo showing all features"""
        print("\n" + "="*60)
        print("🎬 STREAMWARE MVP - INTERACTIVE DEMO")
        print("="*60)
        print("""
This demo shows the voice-controlled dashboard platform.
Open http://localhost:8000 in your browser to see the UI.
        """)
        
        demo_scenarios = [
            {
                "name": "📄 Scenario 1: Document Management",
                "commands": [
                    ("Pokaż faktury", "View all scanned documents"),
                    ("Ile faktur do zapłaty?", "Check unpaid invoices"),
                    ("Suma wszystkich faktur", "Get total amount"),
                ],
            },
            {
                "name": "🎥 Scenario 2: Camera Monitoring",
                "commands": [
                    ("Pokaż kamery", "Show 2x2 camera grid"),
                    ("Gdzie jest ruch?", "Check motion detection"),
                    ("Jakie są alerty?", "View active alerts"),
                ],
            },
            {
                "name": "📊 Scenario 3: Sales Dashboard",
                "commands": [
                    ("Pokaż sprzedaż", "View sales dashboard"),
                    ("Porównaj regiony", "Compare regional sales"),
                    ("Top produkty", "Show best sellers"),
                ],
            },
        ]
        
        ws_full_url = f"{WS_URL}/ws/demo_{int(time.time())}"
        
        async with websockets.connect(ws_full_url) as ws:
            # Skip welcome
            await ws.recv()
            
            for scenario in demo_scenarios:
                print(f"\n{'='*60}")
                print(f"{scenario['name']}")
                print("="*60)
                
                for cmd, description in scenario['commands']:
                    print(f"\n🎤 Voice command: \"{cmd}\"")
                    print(f"   Description: {description}")
                    
                    await ws.send(json.dumps({
                        "type": "voice_command",
                        "text": cmd
                    }))
                    
                    response = await ws.recv()
                    data = json.loads(response)
                    
                    print(f"\n   🔊 System response:")
                    print(f"   \"{data['response_text']}\"")
                    
                    if data['view'].get('stats'):
                        print(f"\n   📊 Stats displayed:")
                        for stat in data['view']['stats']:
                            print(f"      • {stat['icon']} {stat['label']}: {stat['value']}")
                    
                    await asyncio.sleep(1)
                
                print("\n" + "-"*40)
                await asyncio.sleep(2)
        
        print("\n" + "="*60)
        print("✅ DEMO COMPLETED")
        print("="*60)
        print("""
What was demonstrated:
1. Voice command recognition (simulated STT)
2. Intent parsing and routing
3. Dynamic view generation (tables, grids, charts)
4. Voice response generation (simulated TTS)
5. Real-time WebSocket communication

To try the full UI, open http://localhost:8000 in your browser.
        """)


async def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   🎤 STREAMWARE MVP - Voice-Controlled Dashboard Platform     ║
║                                                               ║
║   Testing and Demo Suite                                      ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    demo = StreamwareDemo()
    
    # Check if server is running
    try:
        async with httpx.AsyncClient() as client:
            await client.get(f"{BASE_URL}/api/health", timeout=5)
    except Exception as e:
        print(f"❌ Cannot connect to server at {BASE_URL}")
        print(f"   Error: {e}")
        print("\nMake sure the server is running:")
        print("  docker-compose up streamware")
        print("  # or")
        print("  python -m uvicorn backend.main:app --reload")
        sys.exit(1)
    
    # Run tests
    await demo.test_health()
    await demo.test_rest_commands()
    await demo.test_websocket_session()
    
    # Run interactive demo
    await demo.run_interactive_demo()
    
    print("\n🎉 All tests and demo completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
