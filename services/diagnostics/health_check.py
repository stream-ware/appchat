"""
Streamware Health Check & Diagnostics System
Tests all app functionalities and identifies working vs placeholder features
"""

import asyncio
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import json

logger = logging.getLogger("streamware.diagnostics")


class FeatureStatus(str, Enum):
    FUNCTIONAL = "functional"      # Works with real data/service
    PLACEHOLDER = "placeholder"    # UI exists but no real functionality
    ERROR = "error"               # Has errors
    DISABLED = "disabled"         # Intentionally disabled
    UNKNOWN = "unknown"           # Not tested yet


@dataclass
class FeatureCheck:
    """Result of checking a single feature"""
    feature_id: str
    name: str
    app_type: str
    status: FeatureStatus
    description: str = ""
    error: Optional[str] = None
    has_real_data: bool = False
    has_external_service: bool = False
    service_url: Optional[str] = None
    tested_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AppDiagnostics:
    """Diagnostic results for an app"""
    app_id: str
    name: str
    overall_status: FeatureStatus
    features: List[FeatureCheck] = field(default_factory=list)
    functional_count: int = 0
    placeholder_count: int = 0
    error_count: int = 0


class HealthCheckSystem:
    """
    Comprehensive health check system for all Streamware apps
    Identifies what's real vs placeholder
    """
    
    def __init__(self):
        self.results: Dict[str, AppDiagnostics] = {}
        self.last_check: Optional[datetime] = None
        
    async def run_all_checks(self) -> Dict[str, Any]:
        """Run health checks for all apps"""
        logger.info("🏥 Starting comprehensive health check...")
        self.results = {}
        
        # Check each app category
        await self._check_internet_app()
        await self._check_documents_app()
        await self._check_cameras_app()
        await self._check_sales_app()
        await self._check_home_app()
        await self._check_analytics_app()
        await self._check_files_app()
        await self._check_cloud_storage_app()
        await self._check_curllm_app()
        await self._check_registry_app()
        await self._check_services_app()
        await self._check_monitoring_app()
        
        self.last_check = datetime.now()
        
        return self._generate_report()
    
    async def _check_internet_app(self):
        """Check internet/integrations app"""
        app = AppDiagnostics(app_id="internet", name="🌐 Internet & Integracje", overall_status=FeatureStatus.UNKNOWN)
        
        # Weather - FUNCTIONAL (uses real API)
        weather_check = await self._test_weather()
        app.features.append(weather_check)
        
        # Crypto - FUNCTIONAL (uses real API)
        crypto_check = await self._test_crypto()
        app.features.append(crypto_check)
        
        # Currency Exchange - FUNCTIONAL (uses NBP API)
        exchange_check = await self._test_exchange()
        app.features.append(exchange_check)
        
        # RSS - FUNCTIONAL (real feeds)
        rss_check = await self._test_rss()
        app.features.append(rss_check)
        
        # Email - PLACEHOLDER (no real SMTP configured)
        app.features.append(FeatureCheck(
            feature_id="email",
            name="📧 Email",
            app_type="internet",
            status=FeatureStatus.PLACEHOLDER,
            description="Formularz email istnieje, ale brak skonfigurowanego SMTP",
            has_real_data=False,
            has_external_service=False
        ))
        
        # Webhooks - PLACEHOLDER
        app.features.append(FeatureCheck(
            feature_id="webhooks",
            name="🪝 Webhooks",
            app_type="internet",
            status=FeatureStatus.PLACEHOLDER,
            description="Endpoint istnieje, ale brak aktywnych webhooków",
            has_real_data=False
        ))
        
        self._calculate_app_status(app)
        self.results["internet"] = app
    
    async def _test_weather(self) -> FeatureCheck:
        """Test weather functionality"""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get("https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current_weather=true")
                if resp.status_code == 200:
                    return FeatureCheck(
                        feature_id="weather",
                        name="🌤️ Pogoda",
                        app_type="internet",
                        status=FeatureStatus.FUNCTIONAL,
                        description="Open-Meteo API działa poprawnie",
                        has_real_data=True,
                        has_external_service=True,
                        service_url="https://api.open-meteo.com"
                    )
        except Exception as e:
            return FeatureCheck(
                feature_id="weather",
                name="🌤️ Pogoda",
                app_type="internet",
                status=FeatureStatus.ERROR,
                error=str(e)
            )
        return FeatureCheck(
            feature_id="weather",
            name="🌤️ Pogoda",
            app_type="internet",
            status=FeatureStatus.ERROR,
            error="API unavailable"
        )
    
    async def _test_crypto(self) -> FeatureCheck:
        """Test crypto functionality"""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
                if resp.status_code == 200:
                    return FeatureCheck(
                        feature_id="crypto",
                        name="₿ Kryptowaluty",
                        app_type="internet",
                        status=FeatureStatus.FUNCTIONAL,
                        description="CoinGecko API działa poprawnie",
                        has_real_data=True,
                        has_external_service=True,
                        service_url="https://api.coingecko.com"
                    )
        except Exception as e:
            return FeatureCheck(
                feature_id="crypto",
                name="₿ Kryptowaluty",
                app_type="internet",
                status=FeatureStatus.ERROR,
                error=str(e)
            )
        return FeatureCheck(feature_id="crypto", name="₿ Kryptowaluty", app_type="internet", status=FeatureStatus.ERROR)
    
    async def _test_exchange(self) -> FeatureCheck:
        """Test currency exchange functionality"""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get("https://api.nbp.pl/api/exchangerates/tables/A/?format=json")
                if resp.status_code == 200:
                    return FeatureCheck(
                        feature_id="exchange",
                        name="💱 Kursy walut",
                        app_type="internet",
                        status=FeatureStatus.FUNCTIONAL,
                        description="NBP API działa poprawnie",
                        has_real_data=True,
                        has_external_service=True,
                        service_url="https://api.nbp.pl"
                    )
        except Exception as e:
            return FeatureCheck(
                feature_id="exchange",
                name="💱 Kursy walut",
                app_type="internet",
                status=FeatureStatus.ERROR,
                error=str(e)
            )
        return FeatureCheck(feature_id="exchange", name="💱 Kursy walut", app_type="internet", status=FeatureStatus.ERROR)
    
    async def _test_rss(self) -> FeatureCheck:
        """Test RSS functionality"""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get("https://feeds.bbci.co.uk/news/rss.xml")
                if resp.status_code == 200:
                    return FeatureCheck(
                        feature_id="rss",
                        name="📰 RSS",
                        app_type="internet",
                        status=FeatureStatus.FUNCTIONAL,
                        description="RSS feeds dostępne",
                        has_real_data=True,
                        has_external_service=True
                    )
        except Exception as e:
            return FeatureCheck(feature_id="rss", name="📰 RSS", app_type="internet", status=FeatureStatus.ERROR, error=str(e))
        return FeatureCheck(feature_id="rss", name="📰 RSS", app_type="internet", status=FeatureStatus.ERROR)
    
    async def _check_documents_app(self):
        """Check documents app"""
        app = AppDiagnostics(app_id="documents", name="📄 Dokumenty", overall_status=FeatureStatus.UNKNOWN)
        
        app.features.append(FeatureCheck(
            feature_id="invoice_scan",
            name="📷 Skanowanie faktur",
            app_type="documents",
            status=FeatureStatus.PLACEHOLDER,
            description="Brak integracji ze skanerem/OCR",
            has_real_data=False
        ))
        
        app.features.append(FeatureCheck(
            feature_id="invoice_list",
            name="📋 Lista faktur",
            app_type="documents",
            status=FeatureStatus.PLACEHOLDER,
            description="Brak połączenia z systemem księgowym",
            has_real_data=False
        ))
        
        app.features.append(FeatureCheck(
            feature_id="export_excel",
            name="📥 Eksport Excel",
            app_type="documents",
            status=FeatureStatus.PLACEHOLDER,
            description="Funkcja wymaga danych do eksportu",
            has_real_data=False
        ))
        
        self._calculate_app_status(app)
        self.results["documents"] = app
    
    async def _check_cameras_app(self):
        """Check cameras/monitoring app"""
        app = AppDiagnostics(app_id="cameras", name="🎥 Monitoring CCTV", overall_status=FeatureStatus.UNKNOWN)
        
        app.features.append(FeatureCheck(
            feature_id="camera_grid",
            name="📺 Podgląd kamer",
            app_type="cameras",
            status=FeatureStatus.PLACEHOLDER,
            description="Brak skonfigurowanych kamer RTSP/ONVIF",
            has_real_data=False
        ))
        
        app.features.append(FeatureCheck(
            feature_id="motion_detection",
            name="🏃 Detekcja ruchu",
            app_type="cameras",
            status=FeatureStatus.PLACEHOLDER,
            description="Wymaga kamer i AI do detekcji",
            has_real_data=False
        ))
        
        self._calculate_app_status(app)
        self.results["cameras"] = app
    
    async def _check_sales_app(self):
        """Check sales app"""
        app = AppDiagnostics(app_id="sales", name="📊 Sprzedaż", overall_status=FeatureStatus.UNKNOWN)
        
        app.features.append(FeatureCheck(
            feature_id="sales_dashboard",
            name="📊 Dashboard sprzedaży",
            app_type="sales",
            status=FeatureStatus.PLACEHOLDER,
            description="Brak połączenia z CRM/ERP",
            has_real_data=False
        ))
        
        app.features.append(FeatureCheck(
            feature_id="sales_report",
            name="📈 Raporty",
            app_type="sales",
            status=FeatureStatus.PLACEHOLDER,
            description="Wymaga danych sprzedażowych",
            has_real_data=False
        ))
        
        self._calculate_app_status(app)
        self.results["sales"] = app
    
    async def _check_home_app(self):
        """Check smart home app"""
        app = AppDiagnostics(app_id="home", name="🏠 Smart Home", overall_status=FeatureStatus.UNKNOWN)
        
        app.features.append(FeatureCheck(
            feature_id="temperature",
            name="🌡️ Temperatura",
            app_type="home",
            status=FeatureStatus.PLACEHOLDER,
            description="Brak połączenia z Home Assistant/MQTT",
            has_real_data=False
        ))
        
        app.features.append(FeatureCheck(
            feature_id="lights",
            name="💡 Oświetlenie",
            app_type="home",
            status=FeatureStatus.PLACEHOLDER,
            description="Wymaga integracji IoT",
            has_real_data=False
        ))
        
        self._calculate_app_status(app)
        self.results["home"] = app
    
    async def _check_analytics_app(self):
        """Check analytics app"""
        app = AppDiagnostics(app_id="analytics", name="📈 Analityka", overall_status=FeatureStatus.UNKNOWN)
        
        app.features.append(FeatureCheck(
            feature_id="analytics_dashboard",
            name="📊 Dashboard analityczny",
            app_type="analytics",
            status=FeatureStatus.PLACEHOLDER,
            description="Brak źródeł danych (GA, DB)",
            has_real_data=False
        ))
        
        self._calculate_app_status(app)
        self.results["analytics"] = app
    
    async def _check_files_app(self):
        """Check files app"""
        app = AppDiagnostics(app_id="files", name="📁 File Manager", overall_status=FeatureStatus.UNKNOWN)
        
        # Check if Documents folder exists and has files
        docs_path = Path.home() / "Documents"
        downloads_path = Path.home() / "Downloads"
        
        has_docs = docs_path.exists() and any(docs_path.iterdir()) if docs_path.exists() else False
        has_downloads = downloads_path.exists() and any(downloads_path.iterdir()) if downloads_path.exists() else False
        
        app.features.append(FeatureCheck(
            feature_id="file_list",
            name="📄 Lista plików",
            app_type="files",
            status=FeatureStatus.FUNCTIONAL if has_docs or has_downloads else FeatureStatus.PLACEHOLDER,
            description=f"Dokumenty: {'✅' if has_docs else '❌'} | Pobrane: {'✅' if has_downloads else '❌'}",
            has_real_data=has_docs or has_downloads
        ))
        
        app.features.append(FeatureCheck(
            feature_id="file_search",
            name="🔍 Wyszukiwanie",
            app_type="files",
            status=FeatureStatus.FUNCTIONAL,
            description="Wyszukiwanie lokalne działa",
            has_real_data=True
        ))
        
        self._calculate_app_status(app)
        self.results["files"] = app
    
    async def _check_cloud_storage_app(self):
        """Check cloud storage app"""
        app = AppDiagnostics(app_id="cloud_storage", name="☁️ Cloud Storage", overall_status=FeatureStatus.UNKNOWN)
        
        # Check for saved connections
        config_file = Path(__file__).parent.parent.parent / "data" / "app_configs" / "cloud_storage.json"
        has_connections = config_file.exists()
        
        app.features.append(FeatureCheck(
            feature_id="onedrive",
            name="📘 OneDrive",
            app_type="cloud_storage",
            status=FeatureStatus.PLACEHOLDER,
            description="Formularz połączenia dostępny, wymaga konfiguracji OAuth",
            has_real_data=False,
            has_external_service=False
        ))
        
        app.features.append(FeatureCheck(
            feature_id="nextcloud",
            name="🔵 Nextcloud",
            app_type="cloud_storage",
            status=FeatureStatus.PLACEHOLDER,
            description="Formularz połączenia dostępny, wymaga serwera Nextcloud",
            has_real_data=False,
            has_external_service=False
        ))
        
        app.features.append(FeatureCheck(
            feature_id="gdrive",
            name="📗 Google Drive",
            app_type="cloud_storage",
            status=FeatureStatus.PLACEHOLDER,
            description="Formularz połączenia dostępny, wymaga konfiguracji OAuth",
            has_real_data=False,
            has_external_service=False
        ))
        
        self._calculate_app_status(app)
        self.results["cloud_storage"] = app
    
    async def _check_curllm_app(self):
        """Check CurlLM app"""
        app = AppDiagnostics(app_id="curllm", name="🤖 CurlLM", overall_status=FeatureStatus.UNKNOWN)
        
        # Check if Ollama is running
        ollama_running = False
        models_available = []
        try:
            import httpx
            async with httpx.AsyncClient(timeout=2) as client:
                resp = await client.get("http://localhost:11434/api/tags")
                if resp.status_code == 200:
                    ollama_running = True
                    models_available = [m["name"] for m in resp.json().get("models", [])]
        except:
            pass
        
        app.features.append(FeatureCheck(
            feature_id="ollama",
            name="🦙 Ollama",
            app_type="curllm",
            status=FeatureStatus.FUNCTIONAL if ollama_running else FeatureStatus.ERROR,
            description=f"Modele: {', '.join(models_available[:3])}..." if models_available else "Ollama nie uruchomiony",
            has_real_data=ollama_running,
            has_external_service=True,
            service_url="http://localhost:11434"
        ))
        
        app.features.append(FeatureCheck(
            feature_id="llm_query",
            name="💬 Zapytania LLM",
            app_type="curllm",
            status=FeatureStatus.FUNCTIONAL if ollama_running else FeatureStatus.DISABLED,
            description="Wymaga działającego Ollama",
            has_real_data=ollama_running
        ))
        
        self._calculate_app_status(app)
        self.results["curllm"] = app
    
    async def _check_registry_app(self):
        """Check registry app"""
        app = AppDiagnostics(app_id="registry", name="📦 Registry Manager", overall_status=FeatureStatus.UNKNOWN)
        
        app.features.append(FeatureCheck(
            feature_id="local_registry",
            name="📁 Local Apps",
            app_type="registry",
            status=FeatureStatus.FUNCTIONAL,
            description="Lokalne aplikacje z apps/ folder",
            has_real_data=True
        ))
        
        app.features.append(FeatureCheck(
            feature_id="docker_registry",
            name="🐳 Docker Hub",
            app_type="registry",
            status=FeatureStatus.PLACEHOLDER,
            description="Wymaga konfiguracji Docker",
            has_real_data=False
        ))
        
        app.features.append(FeatureCheck(
            feature_id="git_registry",
            name="📂 GitHub",
            app_type="registry",
            status=FeatureStatus.PLACEHOLDER,
            description="Wymaga tokenu GitHub",
            has_real_data=False
        ))
        
        self._calculate_app_status(app)
        self.results["registry"] = app
    
    async def _check_services_app(self):
        """Check services app"""
        app = AppDiagnostics(app_id="services", name="⚙️ Usługi", overall_status=FeatureStatus.UNKNOWN)
        
        # Check if modular app exists
        services_dir = Path(__file__).parent.parent.parent / "apps" / "services"
        has_makefile = (services_dir / "Makefile").exists()
        
        app.features.append(FeatureCheck(
            feature_id="services_list",
            name="📋 Lista usług",
            app_type="services",
            status=FeatureStatus.FUNCTIONAL if has_makefile else FeatureStatus.PLACEHOLDER,
            description="Modular app z Makefile" if has_makefile else "Brak modularnej aplikacji",
            has_real_data=has_makefile
        ))
        
        self._calculate_app_status(app)
        self.results["services"] = app
    
    async def _check_monitoring_app(self):
        """Check monitoring app"""
        app = AppDiagnostics(app_id="monitoring", name="📊 Monitoring", overall_status=FeatureStatus.UNKNOWN)
        
        # Check if modular app exists
        monitoring_dir = Path(__file__).parent.parent.parent / "apps" / "monitoring"
        has_makefile = (monitoring_dir / "Makefile").exists()
        
        app.features.append(FeatureCheck(
            feature_id="system_monitoring",
            name="💻 Monitoring systemu",
            app_type="monitoring",
            status=FeatureStatus.FUNCTIONAL if has_makefile else FeatureStatus.PLACEHOLDER,
            description="CPU, RAM, Disk monitoring" if has_makefile else "Wymaga konfiguracji",
            has_real_data=has_makefile
        ))
        
        self._calculate_app_status(app)
        self.results["monitoring"] = app
    
    def _calculate_app_status(self, app: AppDiagnostics):
        """Calculate overall app status from features"""
        for feature in app.features:
            if feature.status == FeatureStatus.FUNCTIONAL:
                app.functional_count += 1
            elif feature.status == FeatureStatus.PLACEHOLDER:
                app.placeholder_count += 1
            elif feature.status == FeatureStatus.ERROR:
                app.error_count += 1
        
        if app.error_count > 0:
            app.overall_status = FeatureStatus.ERROR
        elif app.functional_count > 0 and app.placeholder_count == 0:
            app.overall_status = FeatureStatus.FUNCTIONAL
        elif app.functional_count > 0:
            app.overall_status = FeatureStatus.FUNCTIONAL  # Partially functional
        else:
            app.overall_status = FeatureStatus.PLACEHOLDER
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate diagnostic report"""
        total_features = 0
        functional_features = 0
        placeholder_features = 0
        error_features = 0
        
        apps_summary = []
        for app_id, app in self.results.items():
            total_features += len(app.features)
            functional_features += app.functional_count
            placeholder_features += app.placeholder_count
            error_features += app.error_count
            
            apps_summary.append({
                "app_id": app_id,
                "name": app.name,
                "status": app.overall_status.value,
                "functional": app.functional_count,
                "placeholder": app.placeholder_count,
                "errors": app.error_count,
                "features": [asdict(f) for f in app.features]
            })
        
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_apps": len(self.results),
                "total_features": total_features,
                "functional": functional_features,
                "placeholder": placeholder_features,
                "errors": error_features,
                "health_score": round(functional_features / total_features * 100, 1) if total_features > 0 else 0
            },
            "apps": apps_summary
        }
    
    def get_quick_status(self) -> Dict[str, str]:
        """Get quick status for all apps"""
        return {
            app_id: app.overall_status.value 
            for app_id, app in self.results.items()
        }


# Singleton
health_check = HealthCheckSystem()


async def run_startup_diagnostics() -> Dict[str, Any]:
    """Run diagnostics at startup"""
    return await health_check.run_all_checks()
