"""
Service Manager - Core system services orchestration
Manages lifecycle of all Streamware services with health checks and auto-recovery
"""

import asyncio
import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

logger = logging.getLogger("streamware.services")

class ServiceStatus(str, Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class ServiceConfig:
    """Service configuration"""
    id: str
    name: str
    type: str  # "internal", "container", "external"
    enabled: bool = True
    auto_start: bool = True
    health_check_interval: int = 30  # seconds
    restart_on_failure: bool = True
    max_restarts: int = 3
    dependencies: List[str] = field(default_factory=list)
    environment: Dict[str, str] = field(default_factory=dict)
    ports: List[int] = field(default_factory=list)
    volumes: List[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ServiceConfig":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class ServiceState:
    """Runtime state of a service"""
    status: ServiceStatus = ServiceStatus.STOPPED
    pid: Optional[int] = None
    container_id: Optional[str] = None
    started_at: Optional[str] = None
    last_health_check: Optional[str] = None
    health_status: str = "unknown"
    restart_count: int = 0
    error_message: Optional[str] = None


class ServiceManager:
    """
    Central service manager for all Streamware services
    Supports internal Python services, Docker/Podman containers, and external services
    """
    
    def __init__(self):
        self.services: Dict[str, ServiceConfig] = {}
        self.states: Dict[str, ServiceState] = {}
        self._health_check_tasks: Dict[str, asyncio.Task] = {}
        self._callbacks: Dict[str, List[Callable]] = {}
        self._load_config()
        logger.info(f"🔧 ServiceManager initialized with {len(self.services)} services")
    
    def _load_config(self):
        """Load service configurations"""
        config_file = Path(__file__).parent.parent.parent / "data" / "services_config.json"
        if config_file.exists():
            with open(config_file, "r") as f:
                data = json.load(f)
                for svc_id, svc_data in data.get("services", {}).items():
                    self.services[svc_id] = ServiceConfig.from_dict({"id": svc_id, **svc_data})
                    self.states[svc_id] = ServiceState()
    
    def _save_state(self):
        """Save service states to file"""
        state_file = Path(__file__).parent.parent.parent / "data" / "services_state.json"
        states = {sid: asdict(state) for sid, state in self.states.items()}
        with open(state_file, "w") as f:
            json.dump(states, f, indent=2, default=str)
    
    def register_service(self, config: ServiceConfig):
        """Register a new service"""
        self.services[config.id] = config
        self.states[config.id] = ServiceState()
        logger.info(f"📦 Service registered: {config.id} ({config.name})")
    
    def get_service(self, service_id: str) -> Optional[ServiceConfig]:
        """Get service configuration"""
        return self.services.get(service_id)
    
    def get_state(self, service_id: str) -> Optional[ServiceState]:
        """Get service runtime state"""
        return self.states.get(service_id)
    
    def get_all_services(self) -> List[Dict]:
        """Get all services with their states"""
        result = []
        for sid, config in self.services.items():
            state = self.states.get(sid, ServiceState())
            result.append({
                "id": sid,
                "name": config.name,
                "type": config.type,
                "enabled": config.enabled,
                "status": state.status.value,
                "health": state.health_status,
                "started_at": state.started_at,
                "restart_count": state.restart_count
            })
        return result
    
    async def start_service(self, service_id: str) -> Dict[str, Any]:
        """Start a service"""
        config = self.services.get(service_id)
        if not config:
            return {"success": False, "error": f"Service not found: {service_id}"}
        
        state = self.states[service_id]
        if state.status == ServiceStatus.RUNNING:
            return {"success": True, "message": "Service already running"}
        
        # Check dependencies
        for dep in config.dependencies:
            dep_state = self.states.get(dep)
            if not dep_state or dep_state.status != ServiceStatus.RUNNING:
                return {"success": False, "error": f"Dependency not running: {dep}"}
        
        state.status = ServiceStatus.STARTING
        self._emit("service_starting", service_id)
        
        try:
            if config.type == "internal":
                result = await self._start_internal_service(config)
            elif config.type == "container":
                result = await self._start_container_service(config)
            else:
                result = {"success": False, "error": f"Unknown service type: {config.type}"}
            
            if result.get("success"):
                state.status = ServiceStatus.RUNNING
                state.started_at = datetime.now().isoformat()
                state.health_status = "healthy"
                self._emit("service_started", service_id)
                self._start_health_check(service_id)
            else:
                state.status = ServiceStatus.ERROR
                state.error_message = result.get("error")
                self._emit("service_error", service_id)
            
            self._save_state()
            return result
            
        except Exception as e:
            state.status = ServiceStatus.ERROR
            state.error_message = str(e)
            logger.error(f"Failed to start service {service_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def stop_service(self, service_id: str) -> Dict[str, Any]:
        """Stop a service"""
        config = self.services.get(service_id)
        if not config:
            return {"success": False, "error": f"Service not found: {service_id}"}
        
        state = self.states[service_id]
        if state.status == ServiceStatus.STOPPED:
            return {"success": True, "message": "Service already stopped"}
        
        state.status = ServiceStatus.STOPPING
        self._emit("service_stopping", service_id)
        
        # Stop health check
        if service_id in self._health_check_tasks:
            self._health_check_tasks[service_id].cancel()
            del self._health_check_tasks[service_id]
        
        try:
            if config.type == "internal":
                result = await self._stop_internal_service(config, state)
            elif config.type == "container":
                result = await self._stop_container_service(config, state)
            else:
                result = {"success": True}
            
            state.status = ServiceStatus.STOPPED
            state.pid = None
            state.container_id = None
            self._emit("service_stopped", service_id)
            self._save_state()
            return result
            
        except Exception as e:
            state.status = ServiceStatus.ERROR
            state.error_message = str(e)
            return {"success": False, "error": str(e)}
    
    async def restart_service(self, service_id: str) -> Dict[str, Any]:
        """Restart a service"""
        await self.stop_service(service_id)
        await asyncio.sleep(1)
        return await self.start_service(service_id)
    
    async def _start_internal_service(self, config: ServiceConfig) -> Dict:
        """Start internal Python service"""
        # Internal services are managed by the main application
        return {"success": True, "message": f"Internal service {config.id} started"}
    
    async def _stop_internal_service(self, config: ServiceConfig, state: ServiceState) -> Dict:
        """Stop internal Python service"""
        return {"success": True}
    
    async def _start_container_service(self, config: ServiceConfig) -> Dict:
        """Start Docker/Podman container service"""
        import subprocess
        
        # Detect container runtime (podman preferred)
        runtime = "podman" if self._has_podman() else "docker"
        
        # Build command
        cmd = [runtime, "run", "-d", "--name", f"streamware-{config.id}"]
        
        # Add environment variables
        for key, value in config.environment.items():
            cmd.extend(["-e", f"{key}={value}"])
        
        # Add ports
        for port in config.ports:
            cmd.extend(["-p", f"{port}:{port}"])
        
        # Add volumes
        for volume in config.volumes:
            cmd.extend(["-v", volume])
        
        # Add image (from environment or default)
        image = config.environment.get("IMAGE", f"streamware/{config.id}:latest")
        cmd.append(image)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                container_id = result.stdout.strip()[:12]
                self.states[config.id].container_id = container_id
                return {"success": True, "container_id": container_id}
            else:
                return {"success": False, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _stop_container_service(self, config: ServiceConfig, state: ServiceState) -> Dict:
        """Stop Docker/Podman container"""
        import subprocess
        
        runtime = "podman" if self._has_podman() else "docker"
        container_name = f"streamware-{config.id}"
        
        try:
            subprocess.run([runtime, "stop", container_name], timeout=30)
            subprocess.run([runtime, "rm", container_name], timeout=10)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _has_podman(self) -> bool:
        """Check if Podman is available"""
        import shutil
        return shutil.which("podman") is not None
    
    def _start_health_check(self, service_id: str):
        """Start health check task for service"""
        config = self.services.get(service_id)
        if not config:
            return
        
        async def health_check_loop():
            while True:
                await asyncio.sleep(config.health_check_interval)
                await self._check_service_health(service_id)
        
        task = asyncio.create_task(health_check_loop())
        self._health_check_tasks[service_id] = task
    
    async def _check_service_health(self, service_id: str):
        """Check health of a service"""
        config = self.services.get(service_id)
        state = self.states.get(service_id)
        if not config or not state:
            return
        
        state.last_health_check = datetime.now().isoformat()
        
        # Simple health check based on service type
        if config.type == "container":
            import subprocess
            runtime = "podman" if self._has_podman() else "docker"
            result = subprocess.run(
                [runtime, "inspect", "-f", "{{.State.Health.Status}}", f"streamware-{config.id}"],
                capture_output=True, text=True
            )
            state.health_status = result.stdout.strip() or "running"
        else:
            state.health_status = "healthy"
        
        # Auto-restart on failure
        if state.health_status == "unhealthy" and config.restart_on_failure:
            if state.restart_count < config.max_restarts:
                state.restart_count += 1
                logger.warning(f"Service {service_id} unhealthy, restarting ({state.restart_count}/{config.max_restarts})")
                await self.restart_service(service_id)
    
    def on(self, event: str, callback: Callable):
        """Register event callback"""
        if event not in self._callbacks:
            self._callbacks[event] = []
        self._callbacks[event].append(callback)
    
    def _emit(self, event: str, service_id: str):
        """Emit event to callbacks"""
        for callback in self._callbacks.get(event, []):
            try:
                callback(service_id)
            except Exception as e:
                logger.error(f"Error in callback for {event}: {e}")


# Singleton instance
service_manager = ServiceManager()
