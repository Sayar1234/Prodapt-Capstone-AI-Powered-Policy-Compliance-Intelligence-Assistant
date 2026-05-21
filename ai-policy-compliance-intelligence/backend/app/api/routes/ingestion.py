from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Depends, Request

from app.api.dependencies import get_ingestion_service
from app.core.exceptions import ValidationAppError
from app.models.request_models import TextIngestionRequest
from app.models.response_models import IngestionResponse
from app.security.validators import validate_upload
from app.services.ingestion_service import IngestionService
from app.utils.document_utils import safe_filename

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


@router.post("/text", response_model=IngestionResponse)
async def ingest_text(request: TextIngestionRequest, service: IngestionService = Depends(get_ingestion_service)) -> IngestionResponse:
    result = service.ingest_text_document(
        title=request.title,
        text=request.text,
        source=request.source,
        policy_type=request.policy_type,
        metadata=request.metadata,
    )
    return IngestionResponse(results=[result])


@router.post("/files", response_model=IngestionResponse)
async def ingest_files(
    request: Request,
    service: IngestionService = Depends(get_ingestion_service),
) -> IngestionResponse:
    try:
        form = await request.form()
    except AssertionError as exc:
        raise ValidationAppError("Install python-multipart to use file uploads") from exc

    policy_type = str(form.get("policy_type") or "general")
    uploads = form.getlist("files")
    if not uploads:
        raise ValidationAppError("Upload at least one file in the 'files' form field")

    results = []
    for upload in uploads:
        content = await upload.read()
        validate_upload(upload.filename or "document.txt", len(content))
        suffix = Path(upload.filename or "document.txt").suffix
        with NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            temp.write(content)
            temp_path = Path(temp.name)
        try:
            metadata = {"uploaded_filename": safe_filename(upload.filename or temp_path.name)}
            results.append(service.ingest_path(temp_path, policy_type=policy_type, metadata=metadata))
        finally:
            temp_path.unlink(missing_ok=True)
    return IngestionResponse(results=results)
