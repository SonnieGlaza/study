from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4


def ensure_dir(path: str) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


class FileStorage:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def save_bytes(self, category: str, suffix: str, payload: bytes) -> str:
        folder = self.root / category / datetime.utcnow().strftime("%Y%m%d")
        folder.mkdir(parents=True, exist_ok=True)
        file_name = f"{uuid4().hex}{suffix}"
        path = folder / file_name
        path.write_bytes(payload)
        return str(path)

