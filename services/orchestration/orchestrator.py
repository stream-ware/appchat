"""
Service Orchestrator - Manages Docker/Podman compose deployments
Provides unified interface for container orchestration
"""

import asyncio
import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger("streamware.orchestrator")

INFRA_DIR = Path(__file__).parent.parent.parent / "infrastructure"


@dataclass
class ContainerInfo:
    """Container information"""
    id: str
    name: str
    image: str
    status: str
    ports: List[str]
    created: str


class Orchestrator:
    """
    Container orchestration for Streamware services
    Supports Docker Compose and Podman Compose
    """
    
    def __init__(self):
        self.runtime = self._detect_runtime()
        self.compose_file = self._get_compose_file()
        logger.info(f"🐳 Orchestrator initialized (runtime: {self.runtime})")
    
    def _detect_runtime(self) -> str:
        """Detect container runtime"""
        import shutil
        
        # Check for podman-compose first (rootless preferred)
        if shutil.which("podman-compose"):
            return "podman-compose"
        elif shutil.which("podman") and shutil.which("docker-compose"):
            # Podman with docker-compose compatibility
            return "docker-compose"
        elif shutil.which("docker-compose"):
            return "docker-compose"
        elif shutil.which("docker"):
            return "docker compose"
        
        return "none"
    
    def _get_compose_file(self) -> Path:
        """Get appropriate compose file"""
        if "podman" in self.runtime:
            podman_file = INFRA_DIR / "podman" / "podman-compose.yml"
            if podman_file.exists():
                return podman_file
        
        return INFRA_DIR / "docker" / "docker-compose.yml"
    
    def _run_compose(self, *args, capture: bool = True) -> Dict[str, Any]:
        """Run compose command"""
        if self.runtime == "none":
            return {"success": False, "error": "No container runtime found"}
        
        cmd = self.runtime.split() + ["-f", str(self.compose_file)] + list(args)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture,
                text=True,
                timeout=300,
                cwd=str(self.compose_file.parent)
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def up(self, services: List[str] = None, detach: bool = True, profiles: List[str] = None) -> Dict:
        """Start services"""
        args = ["up"]
        
        if detach:
            args.append("-d")
        
        if profiles:
            for profile in profiles:
                args.extend(["--profile", profile])
        
        if services:
            args.extend(services)
        
        logger.info(f"🚀 Starting services: {services or 'all'}")
        result = self._run_compose(*args)
        
        if result.get("success"):
            logger.info("✅ Services started successfully")
        else:
            logger.error(f"❌ Failed to start services: {result.get('error') or result.get('stderr')}")
        
        return result
    
    async def down(self, remove_volumes: bool = False) -> Dict:
        """Stop and remove services"""
        args = ["down"]
        
        if remove_volumes:
            args.append("-v")
        
        logger.info("🛑 Stopping services...")
        return self._run_compose(*args)
    
    async def restart(self, services: List[str] = None) -> Dict:
        """Restart services"""
        args = ["restart"]
        if services:
            args.extend(services)
        
        logger.info(f"🔄 Restarting services: {services or 'all'}")
        return self._run_compose(*args)
    
    async def logs(self, service: str = None, tail: int = 100, follow: bool = False) -> Dict:
        """Get service logs"""
        args = ["logs", "--tail", str(tail)]
        
        if follow:
            args.append("-f")
        
        if service:
            args.append(service)
        
        return self._run_compose(*args)
    
    async def ps(self) -> List[ContainerInfo]:
        """List running containers"""
        result = self._run_compose("ps", "--format", "json")
        
        if not result.get("success"):
            return []
        
        containers = []
        try:
            # Parse JSON output (format varies by runtime)
            output = result.get("stdout", "")
            if output.strip():
                for line in output.strip().split("\n"):
                    if line.startswith("{"):
                        data = json.loads(line)
                        containers.append(ContainerInfo(
                            id=data.get("ID", data.get("id", ""))[:12],
                            name=data.get("Name", data.get("name", "")),
                            image=data.get("Image", data.get("image", "")),
                            status=data.get("Status", data.get("status", "")),
                            ports=data.get("Ports", data.get("ports", [])),
                            created=data.get("Created", "")
                        ))
        except:
            # Fallback: parse text output
            pass
        
        return containers
    
    async def pull(self, services: List[str] = None) -> Dict:
        """Pull latest images"""
        args = ["pull"]
        if services:
            args.extend(services)
        
        logger.info(f"📥 Pulling images: {services or 'all'}")
        return self._run_compose(*args)
    
    async def build(self, services: List[str] = None, no_cache: bool = False) -> Dict:
        """Build images"""
        args = ["build"]
        
        if no_cache:
            args.append("--no-cache")
        
        if services:
            args.extend(services)
        
        logger.info(f"🔨 Building images: {services or 'all'}")
        return self._run_compose(*args)
    
    async def exec(self, service: str, command: str) -> Dict:
        """Execute command in running container"""
        args = ["exec", service, "sh", "-c", command]
        return self._run_compose(*args)
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            "runtime": self.runtime,
            "compose_file": str(self.compose_file),
            "available": self.runtime != "none"
        }
    
    async def health_check(self) -> Dict[str, str]:
        """Check health of all services"""
        containers = await self.ps()
        health = {}
        
        for container in containers:
            status = container.status.lower()
            if "up" in status and "healthy" in status:
                health[container.name] = "healthy"
            elif "up" in status:
                health[container.name] = "running"
            else:
                health[container.name] = "unhealthy"
        
        return health


# Singleton instance
orchestrator = Orchestrator()
