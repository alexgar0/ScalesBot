from pathlib import Path
import subprocess
from typing import List, Optional

import logfire

from core.config import settings
from core.security import validate_path

class DockerComposeError(Exception):
    """Custom exception for docker compose errors"""
    pass

class DockerComposeManager:
    def __init__(self) -> None:
        self.modules_root: Path = settings.root_path / "docker"
        self.modules_root.mkdir(parents=True, exist_ok=True)

    def _validate_module_name(self, module_name: str) -> None:
        """Защита от path traversal и пустых имён"""
        if not module_name.strip():
            raise ValueError("Module name cannot be empty")
        if any(sep in module_name for sep in ("/", "\\", "..")):
            raise ValueError(f"Wrong module name: {module_name}")

    def _get_compose_file(self, module_name: str) -> Path:
        compose_path = Path(module_name) / "docker-compose.yml"
        validated_compose_path = validate_path(compose_path, self.modules_root)
        self._validate_module_name(module_name)
        if not validated_compose_path.exists():
            raise FileNotFoundError(f"docker-compose.yml not found: {compose_path}")
        return validated_compose_path

    def _run_compose(self, module_name: str, args: List[str], capture_output: bool = False) -> subprocess.CompletedProcess[str]:
        compose_file = self._get_compose_file(module_name)
        cmd = ["docker", "compose", "-f", str(compose_file)] + args
        try:
            logfire.info(f"Executing: {' '.join(cmd)}")
            return subprocess.run(
                cmd,
                cwd=str(compose_file.parent),
                capture_output=capture_output,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            logfire.error(f"docker compose failed for {module_name}: {e.stderr}")
            raise DockerComposeError(f"Command returned with an error: {' '.join(cmd)}") from e
        except FileNotFoundError:
            raise DockerComposeError("Docker is not installed or not found in PATH")

    def up(self, module_name: str, detach: bool = True, build: bool = False) -> subprocess.CompletedProcess[str]:
        args = ["up"]
        if detach: args.append("-d")
        if build: args.append("--build")
        return self._run_compose(module_name, args)

    def down(self, module_name: str, remove_volumes: bool = False) -> subprocess.CompletedProcess[str]:
        args = ["down"]
        if remove_volumes: args.append("-v")
        return self._run_compose(module_name, args)

    def restart(self, module_name: str) -> subprocess.CompletedProcess[str]:
        return self._run_compose(module_name, ["restart"])

    def logs(self, module_name: str, tail: Optional[int] = 100) -> str:
        args = ["logs"]
        if tail is not None:
            args.extend(["--tail", str(tail)])
        return self._run_compose(module_name, args, capture_output=True).stdout

    def ps(self, module_name: str) -> str:
        return self._run_compose(module_name, ["ps"], capture_output=True).stdout
    
    def list_modules(self) -> List[str]:
        return sorted([
            d.name for d in self.modules_root.iterdir()
            if d.is_dir() and (d / "docker-compose.yml").exists()
        ])