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
    UserManager,
    SkillRegistry,
    User,
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
        assert len(view["commands"]) == 7  # 7 categories: documents, cameras, sales, home, analytics, internet, system
    
    def test_generate_empty_view(self):
        """Test empty/welcome view generation - now returns welcome dashboard"""
        view = ViewGenerator.generate("empty", "")
        
        assert view["type"] == "welcome"
        assert view["view"] == "dashboard"
        assert "apps" in view


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


class TestUserManager:
    """Tests for UserManager authentication and access control"""
    
    def test_authenticate_valid_user(self):
        """Test authentication with valid credentials"""
        um = UserManager()
        user = um.authenticate("admin", "admin123")
        
        assert user is not None
        assert user.username == "admin"
        assert user.role == "admin"
    
    def test_authenticate_invalid_password(self):
        """Test authentication with invalid password"""
        um = UserManager()
        user = um.authenticate("admin", "wrongpassword")
        
        assert user is None
    
    def test_authenticate_invalid_user(self):
        """Test authentication with non-existent user"""
        um = UserManager()
        user = um.authenticate("nonexistent", "password")
        
        assert user is None
    
    def test_login_success(self):
        """Test successful login"""
        um = UserManager()
        result = um.login("session_123", "kowalski", "biuro123")
        
        assert result["success"] == True
        assert result["user"] == "Jan Kowalski"
        assert result["role"] == "Pracownik biurowy"
    
    def test_login_failure(self):
        """Test failed login"""
        um = UserManager()
        result = um.login("session_123", "admin", "wrongpassword")
        
        assert result["success"] == False
        assert "error" in result
    
    def test_logout(self):
        """Test logout"""
        um = UserManager()
        um.login("session_123", "admin", "admin123")
        
        assert um.get_user("session_123") is not None
        
        result = um.logout("session_123")
        
        assert result == True
        assert um.get_user("session_123") is None
    
    def test_has_permission_admin(self):
        """Test admin has all permissions"""
        um = UserManager()
        um.login("session_admin", "admin", "admin123")
        
        assert um.has_permission("session_admin", "documents") == True
        assert um.has_permission("session_admin", "cameras") == True
        assert um.has_permission("session_admin", "sales") == True
        assert um.has_permission("session_admin", "home") == True
    
    def test_has_permission_office_user(self):
        """Test office user has limited permissions"""
        um = UserManager()
        um.login("session_office", "kowalski", "biuro123")
        
        assert um.has_permission("session_office", "documents") == True
        assert um.has_permission("session_office", "sales") == True
        assert um.has_permission("session_office", "cameras") == False
        assert um.has_permission("session_office", "home") == False
    
    def test_has_permission_security_user(self):
        """Test security user has camera/home permissions"""
        um = UserManager()
        um.login("session_security", "dozorca", "ochrona123")
        
        assert um.has_permission("session_security", "cameras") == True
        assert um.has_permission("session_security", "home") == True
        assert um.has_permission("session_security", "documents") == False
        assert um.has_permission("session_security", "sales") == False
    
    def test_get_allowed_apps(self):
        """Test getting allowed apps for user"""
        um = UserManager()
        um.login("session_test", "kowalski", "biuro123")
        
        apps = um.get_allowed_apps("session_test")
        
        assert "documents" in apps
        assert "sales" in apps
        assert "cameras" not in apps
    
    def test_get_users_list(self):
        """Test getting list of all users"""
        um = UserManager()
        users = um.get_users_list()
        
        assert len(users) == 5  # admin, kowalski, dozorca, manager, gosc
        usernames = [u["username"] for u in users]
        assert "admin" in usernames
        assert "kowalski" in usernames
        assert "dozorca" in usernames


class TestSkillRegistry:
    """Tests for SkillRegistry"""
    
    def test_get_all_apps(self):
        """Test getting all registered apps"""
        apps = SkillRegistry.get_all_apps()
        
        assert "documents" in apps
        assert "cameras" in apps
        assert "sales" in apps
        assert "home" in apps
        assert "analytics" in apps
        assert "internet" in apps
        assert "system" in apps
    
    def test_get_apps_for_user_admin(self):
        """Test getting apps for admin (all permissions)"""
        apps = SkillRegistry.get_apps_for_user(["*"])
        
        assert len(apps) == 7  # All apps
    
    def test_get_apps_for_user_limited(self):
        """Test getting apps for limited user"""
        apps = SkillRegistry.get_apps_for_user(["documents", "sales"])
        
        assert len(apps) == 2
        assert "documents" in apps
        assert "sales" in apps
        assert "cameras" not in apps
    
    def test_get_app(self):
        """Test getting single app"""
        app = SkillRegistry.get_app("documents")
        
        assert app is not None
        assert app["name"] == "📄 Dokumenty"
        assert "skills" in app
        assert len(app["skills"]) > 0
    
    def test_get_all_commands(self):
        """Test getting all commands as flat list"""
        commands = SkillRegistry.get_all_commands()
        
        assert len(commands) > 50  # Should have 50+ commands
        
        # Check command structure
        cmd = commands[0]
        assert "app" in cmd
        assert "command" in cmd
        assert "name" in cmd
        assert "description" in cmd
    
    def test_app_has_skills(self):
        """Test each app has skills defined"""
        apps = SkillRegistry.get_all_apps()
        
        for app_key, app in apps.items():
            assert "skills" in app
            assert len(app["skills"]) > 0
            
            # Each skill should have cmd, name, desc
            for skill in app["skills"]:
                assert "cmd" in skill
                assert "name" in skill
                assert "desc" in skill


class TestInternetCommands:
    """Tests for internet integration commands"""
    
    def test_recognize_weather_command(self):
        """Test recognition of weather commands"""
        commands = ["pogoda", "weather", "pogoda warszawa"]
        
        for cmd in commands:
            result = VoiceCommandProcessor.process(cmd)
            assert result["recognized"] == True
            assert result["app_type"] == "internet"
    
    def test_recognize_crypto_command(self):
        """Test recognition of crypto commands"""
        commands = ["bitcoin", "crypto", "kryptowaluty"]
        
        for cmd in commands:
            result = VoiceCommandProcessor.process(cmd)
            assert result["recognized"] == True
            assert result["app_type"] == "internet"
    
    def test_recognize_rss_command(self):
        """Test recognition of RSS commands"""
        result = VoiceCommandProcessor.process("rss")
        
        assert result["recognized"] == True
        assert result["app_type"] == "internet"
        assert result["action"] == "rss"
    
    def test_recognize_integrations_command(self):
        """Test recognition of integrations status command"""
        result = VoiceCommandProcessor.process("integracje")
        
        assert result["recognized"] == True
        assert result["app_type"] == "internet"
        assert result["action"] == "integrations"


class TestSystemCommands:
    """Tests for system commands including login/logout"""
    
    def test_recognize_login_command(self):
        """Test recognition of login command"""
        result = VoiceCommandProcessor.process("login")
        
        assert result["recognized"] == True
        assert result["app_type"] == "system"
        assert result["action"] == "login"
    
    def test_recognize_logout_command(self):
        """Test recognition of logout command"""
        result = VoiceCommandProcessor.process("logout")
        
        assert result["recognized"] == True
        assert result["app_type"] == "system"
        assert result["action"] == "logout"
    
    def test_recognize_welcome_command(self):
        """Test recognition of welcome/start command"""
        commands = ["start", "aplikacje"]
        
        for cmd in commands:
            result = VoiceCommandProcessor.process(cmd)
            assert result["recognized"] == True
            assert result["app_type"] == "system"
            assert result["action"] == "welcome"


class TestWelcomeView:
    """Tests for welcome dashboard view"""
    
    def test_generate_welcome_view(self):
        """Test generating welcome view with all apps"""
        view = ViewGenerator._generate_welcome_view()
        
        assert view["type"] == "welcome"
        assert view["view"] == "dashboard"
        assert "apps" in view
        assert "total_skills" in view
        assert view["total_skills"] > 50
    
    def test_generate_welcome_view_filtered(self):
        """Test generating welcome view with filtered permissions"""
        view = ViewGenerator._generate_welcome_view(["documents", "sales"])
        
        assert view["type"] == "welcome"
        assert "apps" in view
        assert len(view["apps"]) == 2
        assert "documents" in view["apps"]
        assert "sales" in view["apps"]
        assert "cameras" not in view["apps"]
    
    def test_generate_login_view(self):
        """Test generating login view"""
        view = ViewGenerator.generate("system", "login")
        
        assert view["type"] == "system"
        assert view["view"] == "login"
        assert "users" in view


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
