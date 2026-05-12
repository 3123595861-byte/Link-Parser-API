import logging
from fastapi import APIRouter, HTTPException

from app.core.schemas import ExtractRequest, ExtractResponse
from app.services.parser import extract_metadata, ParserError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/extract", response_model=ExtractResponse)
async def extract_endpoint(payload: ExtractRequest) -> ExtractResponse:
    try:
        logger.info("Received extract request for url=%s", payload.url)

        result = await extract_metadata(str(payload.url))

        logger.info("Extract request completed for url=%s", payload.url)
        return result
    except ParserError as exc:
        # 这里表示目标网页本身不可解析，属于可预期业务错误，不视为服务崩溃。
        logger.warning("Parser error for url=%s: %s", payload.url, exc)
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("Extract request failed for url=%s", payload.url)
        raise HTTPException(
            status_code=500,
            detail="Failed to extract metadata",
        ) from exc
