from __future__ import annotations

import json

from backend.app.api.schemas.contracts import (
    ActorRef,
    AttachmentManifestEntry,
    AttachmentManifestResponse,
    AttachmentMetadataResponse,
    AuditEventPageResponse,
    AuditEventResponse,
)
from backend.app.infrastructure.db.session import get_session_factory
from backend.app.infrastructure.files.zip_storage import InvalidZipFileError, ZipStorage
from backend.app.infrastructure.repositories.attachments import (
    AttachmentCreateData,
    AttachmentRecord,
    SqlAlchemyAttachmentsRepository,
)
from backend.app.infrastructure.repositories.audit_events import AuditEventWrite, AuditEventWriter


class AttachmentValidationError(Exception):
    pass


class AttachmentNotFoundError(Exception):
    pass


class AttachmentService:
    def __init__(self) -> None:
        session_factory = get_session_factory()
        self._repository = SqlAlchemyAttachmentsRepository(session_factory)
        self._audit_writer = AuditEventWriter(session_factory)
        self._storage = ZipStorage()

    def upload_attachment(
        self,
        *,
        request_id: str,
        filename: str,
        content_type: str,
        content: bytes,
        actor_user_id: str,
        actor_username: str,
    ) -> AttachmentMetadataResponse:
        normalized_filename = filename.strip()
        if not normalized_filename.lower().endswith(".zip"):
            raise AttachmentValidationError("Solo se permiten archivos ZIP.")
        if not self._repository.request_exists(request_id=request_id):
            raise AttachmentNotFoundError(f"Credit request '{request_id}' was not found.")

        attachment_id = self._repository.next_attachment_id()
        try:
            storage_path, manifest = self._storage.save(
                request_id=request_id,
                attachment_id=attachment_id,
                original_filename=normalized_filename,
                content=content,
            )
        except InvalidZipFileError as exc:
            raise AttachmentValidationError(str(exc)) from exc

        record = self._repository.create(
            AttachmentCreateData(
                attachment_id=attachment_id,
                request_id=request_id,
                storage_path=storage_path,
                original_filename=normalized_filename,
                mime_type=content_type or "application/zip",
                uploaded_by_user_id=actor_user_id,
            )
        )
        self._audit_writer.write(
            AuditEventWrite(
                aggregate_id=record.attachment_id,
                aggregate_type="credit_request_attachment",
                event_type="attachment_uploaded",
                event_payload=json.dumps(
                    {
                        "request_id": request_id,
                        "evaluation_id": None,
                        "original_filename": record.original_filename,
                        "entry_count": len(manifest),
                    }
                ),
                created_by=actor_user_id,
            )
        )
        return _map_attachment_metadata(record, entry_count=len(manifest))

    def list_attachments(self, *, request_id: str) -> list[AttachmentMetadataResponse]:
        if not self._repository.request_exists(request_id=request_id):
            raise AttachmentNotFoundError(f"Credit request '{request_id}' was not found.")
        records = self._repository.list(request_id=request_id)
        return [
            _map_attachment_metadata(record, entry_count=len(self._storage.read_manifest(record.storage_path)))
            for record in records
        ]

    def get_manifest(self, *, request_id: str, attachment_id: str) -> AttachmentManifestResponse:
        record = self._get_attachment(request_id=request_id, attachment_id=attachment_id)
        manifest = self._storage.read_manifest(record.storage_path)
        return AttachmentManifestResponse(
            attachment_id=record.attachment_id,
            request_id=record.request_id,
            original_filename=record.original_filename,
            entries=[
                AttachmentManifestEntry(
                    path=item.path,
                    size=item.size,
                    compressed_size=item.compressed_size,
                )
                for item in manifest
            ],
        )

    def download_attachment(
        self,
        *,
        request_id: str,
        attachment_id: str,
        actor_user_id: str,
    ) -> tuple[AttachmentRecord, bytes]:
        record = self._get_attachment(request_id=request_id, attachment_id=attachment_id)
        payload = self._storage.read_bytes(record.storage_path)
        self._audit_writer.write(
            AuditEventWrite(
                aggregate_id=record.attachment_id,
                aggregate_type="credit_request_attachment",
                event_type="attachment_downloaded",
                event_payload=json.dumps(
                    {
                        "request_id": request_id,
                        "evaluation_id": None,
                        "original_filename": record.original_filename,
                    }
                ),
                created_by=actor_user_id,
            )
        )
        return record, payload

    def list_audit_events(
        self,
        *,
        request_id: str | None,
        evaluation_id: str | None,
        page: int,
        page_size: int,
    ) -> AuditEventPageResponse:
        total, records = self._repository.list_audit_events(
            request_id=request_id,
            evaluation_id=evaluation_id,
            page=page,
            page_size=page_size,
        )
        return AuditEventPageResponse(
            page=page,
            page_size=page_size,
            total=total,
            items=[
                AuditEventResponse(
                    event_id=item.event_id,
                    aggregate_id=item.aggregate_id,
                    aggregate_type=item.aggregate_type,
                    event_type=item.event_type,
                    event_payload=item.event_payload,
                    created_by=ActorRef(user_id=item.created_by_user_id, username=item.created_by_username),
                    created_at=item.created_at,
                )
                for item in records
            ],
        )

    def _get_attachment(self, *, request_id: str, attachment_id: str) -> AttachmentRecord:
        record = self._repository.get(request_id=request_id, attachment_id=attachment_id)
        if record is None:
            raise AttachmentNotFoundError(f"Attachment '{attachment_id}' was not found for request '{request_id}'.")
        return record


def _map_attachment_metadata(record: AttachmentRecord, *, entry_count: int) -> AttachmentMetadataResponse:
    return AttachmentMetadataResponse(
        attachment_id=record.attachment_id,
        request_id=record.request_id,
        original_filename=record.original_filename,
        mime_type=record.mime_type,
        uploaded_at=record.uploaded_at,
        uploaded_by=ActorRef(user_id=record.uploaded_by_user_id, username=record.uploaded_by_username),
        entry_count=entry_count,
    )
