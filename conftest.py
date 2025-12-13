"""
Streamware MVP - Pytest Configuration and Fixtures
"""

import pytest
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def base_url():
    """Base URL for tests"""
    return os.environ.get("TEST_BASE_URL", "http://localhost:8765")


@pytest.fixture
def ws_url():
    """WebSocket URL for tests"""
    return os.environ.get("TEST_WS_URL", "ws://localhost:8765")


@pytest.fixture
def sample_documents():
    """Sample document data for tests"""
    from backend.main import DataSimulator
    return DataSimulator.generate_documents(5)


@pytest.fixture
def sample_cameras():
    """Sample camera data for tests"""
    from backend.main import DataSimulator
    return DataSimulator.generate_cameras(4)


@pytest.fixture
def sample_sales():
    """Sample sales data for tests"""
    from backend.main import DataSimulator
    return DataSimulator.generate_sales()
