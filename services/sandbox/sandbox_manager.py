"""
Sandbox Manager - Isolated execution environment for apps
Provides secure sandboxing using containers (Podman/Docker) or process isolation
"""

import asyncio
import os
import json
import shutil
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger("streamware.sandbox")


class SandboxType(str, Enum):
    PROCESS = "process"      # Simple process isolation
    CONTAINER = "container"  # Docker/Podman container
    ROOTLESS = "rootless"    # Rootless container (Podman)


class SandboxStatus(str, Enum):
    IDLE = "idle"
    CREATING = "creating"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class SandboxConfig:
    """Sandbox configuration"""
    id: str
    app_id: str
    type: SandboxType = SandboxType.PROCESS
    memory_limit: str = "512m"
    cpu_limit: float = 1.0
    timeout: int = 300  # seconds
    network: bool = False
    read_only: bool = True
    allowed_paths: List[str] = field(default_factory=list)
    environment: Dict[str, str] = field(default_factory=dict)


@dataclass
class SandboxState:
    """Sandbox runtime state"""
    status: SandboxStatus = SandboxStatus.IDLE
    container_id: Optional[str] = None
    pid: Optional[int] = None
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    output: str = ""
    error: str = ""
    exit_code: Optional[int] = None


class SandboxManager:
    """
    Manages isolated sandbox environments for app execution
    Supports Podman (preferred), Docker, and process-based isolation
    """
    
    def __init__(self):
        self.sandboxes: Dict[str, SandboxConfig] = {}
        self.states: Dict[str, SandboxState] = {}
        self.runtime = self._detect_runtime()
        self.base_image = "python:3.11-slim"
        logger.info(f"🔒 SandboxManager initialized (runtime: {self.runtime})")
    
    def _detect_runtime(self) -> str:
        """Detect available container runtime"""
        if shutil.which("podman"):
            return "podman"
        elif shutil.which("docker"):
            return "docker"
        return "process"
    
    def create_sandbox(self, app_id: str, config: Optional[Dict] = None) -> str:
        """Create a new sandbox for an app"""
        sandbox_id = f"{app_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        sandbox_config = SandboxConfig(
            id=sandbox_id,
            app_id=app_id,
            **(config or {})
        )
        
        self.sandboxes[sandbox_id] = sandbox_config
        self.states[sandbox_id] = SandboxState(
            status=SandboxStatus.IDLE,
            created_at=datetime.now().isoformat()
        )
        
        logger.info(f"🔒 Sandbox created: {sandbox_id} for app {app_id}")
        return sandbox_id
    
    async def run_in_sandbox(
        self,
        sandbox_id: str,
        command: str,
        working_dir: str = "/app",
        env: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """Run a command in sandbox"""
        config = self.sandboxes.get(sandbox_id)
        state = self.states.get(sandbox_id)
        
        if not config or not state:
            return {"success": False, "error": f"Sandbox not found: {sandbox_id}"}
        
        state.status = SandboxStatus.RUNNING
        state.started_at = datetime.now().isoformat()
        
        try:
            if self.runtime in ["podman", "docker"]:
                result = await self._run_container(config, command, working_dir, env)
            else:
                result = await self._run_process(config, command, working_dir, env)
            
            state.output = result.get("stdout", "")
            state.error = result.get("stderr", "")
            state.exit_code = result.get("exit_code", 0)
            state.status = SandboxStatus.STOPPED if result.get("success") else SandboxStatus.ERROR
            
            return result
            
        except Exception as e:
            state.status = SandboxStatus.ERROR
            state.error = str(e)
            return {"success": False, "error": str(e)}
    
    async def _run_container(
        self,
        config: SandboxConfig,
        command: str,
        working_dir: str,
        env: Dict[str, str] = None
    ) -> Dict:
        """Run command in container sandbox"""
        cmd = [
            self.runtime, "run", "--rm",
            "--memory", config.memory_limit,
            "--cpus", str(config.cpu_limit),
            "--workdir", working_dir,
        ]
        
        # Network isolation
        if not config.network:
            cmd.extend(["--network", "none"])
        
        # Read-only filesystem
        if config.read_only:
            cmd.append("--read-only")
            cmd.extend(["--tmpfs", "/tmp:rw,noexec,nosuid,size=64m"])
        
        # Environment variables
        combined_env = {**config.environment, **(env or {})}
        for key, value in combined_env.items():
            cmd.extend(["-e", f"{key}={value}"])
        
        # Mount allowed paths
        for path in config.allowed_paths:
            if Path(path).exists():
                cmd.extend(["-v", f"{path}:{path}:ro"])
        
        # Image and command
        cmd.append(self.base_image)
        cmd.extend(["sh", "-c", command])
        
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=config.timeout
                )
                
                return {
                    "success": proc.returncode == 0,
                    "stdout": stdout.decode()[:10000],
                    "stderr": stderr.decode()[:2000],
                    "exit_code": proc.returncode
                }
            except asyncio.TimeoutError:
                proc.kill()
                return {
                    "success": False,
                    "error": f"Timeout after {config.timeout}s",
                    "exit_code": -1
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _run_process(
        self,
        config: SandboxConfig,
        command: str,
        working_dir: str,
        env: Dict[str, str] = None
    ) -> Dict:
        """Run command with process isolation (fallback)"""
        combined_env = {**os.environ, **config.environment, **(env or {})}
        
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir if Path(working_dir).exists() else None,
                env=combined_env
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=config.timeout
                )
                
                return {
                    "success": proc.returncode == 0,
                    "stdout": stdout.decode()[:10000],
                    "stderr": stderr.decode()[:2000],
                    "exit_code": proc.returncode
                }
            except asyncio.TimeoutError:
                proc.kill()
                return {
                    "success": False,
                    "error": f"Timeout after {config.timeout}s",
                    "exit_code": -1
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def destroy_sandbox(self, sandbox_id: str) -> bool:
        """Destroy a sandbox"""
        if sandbox_id in self.sandboxes:
            del self.sandboxes[sandbox_id]
        if sandbox_id in self.states:
            del self.states[sandbox_id]
        logger.info(f"🗑️ Sandbox destroyed: {sandbox_id}")
        return True
    
    def get_sandbox_state(self, sandbox_id: str) -> Optional[Dict]:
        """Get sandbox state"""
        state = self.states.get(sandbox_id)
        if state:
            return {
                "status": state.status.value,
                "created_at": state.created_at,
                "started_at": state.started_at,
                "exit_code": state.exit_code,
                "output_length": len(state.output),
                "error_length": len(state.error)
            }
        return None
    
    def list_sandboxes(self) -> List[Dict]:
        """List all sandboxes"""
        return [
            {
                "id": sid,
                "app_id": config.app_id,
                "type": config.type.value,
                "status": self.states[sid].status.value
            }
            for sid, config in self.sandboxes.items()
        ]


# Singleton instance
sandbox_manager = SandboxManager()
