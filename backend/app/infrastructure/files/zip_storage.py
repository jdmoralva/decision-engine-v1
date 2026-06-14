from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from backend.app.config.settings import get_settings


class InvalidZipFileError(Exception):
    pass


@dataclass(frozen=True)
class ZipManifestEntry:
    path: str
    size: int
    compressed_size: int


class ZipStorage:
    def __init__(self) -> None:
        self._root = Path(get_settings().attachments_storage_dir)
        self._root.mkdir(parents=True, exist_ok=True)

    def save(self, *, request_id: str, attachment_id: str, original_filename: str, content: bytes) -> tuple[str, list[ZipManifestEntry]]:
        manifest = self._read_manifest(content)
        suffix = Path(original_filename).suffix or ".zip"
        storage_dir = self._root / request_id
        storage_dir.mkdir(parents=True, exist_ok=True)
        storage_path = storage_dir / f"{attachment_id}{suffix}"
        storage_path.write_bytes(content)
        return str(storage_path), manifest

    def read_bytes(self, storage_path: str) -> bytes:
        return Path(storage_path).read_bytes()

    def read_manifest(self, storage_path: str) -> list[ZipManifestEntry]:
        return self._read_manifest(Path(storage_path).read_bytes())

    def _read_manifest(self, content: bytes) -> list[ZipManifestEntry]:
        try:
            with ZipFile(BytesIO(content)) as archive:
                entries = [
                    ZipManifestEntry(
                        path=item.filename,
                        size=item.file_size,
                        compressed_size=item.compress_size,
                    )
                    for item in archive.infolist()
                    if not item.is_dir()
                ]
        except BadZipFile as exc:
            raise InvalidZipFileError("El archivo debe ser un ZIP valido.") from exc

        if not entries:
            raise InvalidZipFileError("El archivo ZIP no contiene archivos.")
        return sorted(entries, key=lambda item: item.path)
