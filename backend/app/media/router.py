"""Media API: audio requests and range-capable streaming (spec 02 §6, 04 §2)."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Header, Request, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.auth.deps import optional_user
from app.common.errors import forbidden, not_found
from app.db.client import get_db, gridfs_bucket
from app.media import service

router = APIRouter(prefix="/api/v1", tags=["media"])


class ContentRef(BaseModel):
    item_id: str
    revision: int


class AudioRequestIn(BaseModel):
    content_ref: ContentRef
    turn_id: str
    language_tag: str = "gsw-CH"


@router.post("/audio/requests")
async def post_audio_request(payload: AudioRequestIn, response: Response,
                             user: Optional[dict] = Depends(optional_user)):
    result = await service.request_audio(
        content_ref=payload.content_ref.model_dump(), turn_id=payload.turn_id, user=user
    )
    if result.get("status") != "ready":
        response.status_code = 202
    return {"data": result}


@router.get("/audio/requests/{request_id}")
async def get_audio_request(request_id: str, user: Optional[dict] = Depends(optional_user)):
    return {"data": await service.audio_request_status(request_id)}


def _parse_range(range_header: str, size: int):
    try:
        units, _, rng = range_header.partition("=")
        if units.strip() != "bytes":
            return None
        start_s, _, end_s = rng.partition("-")
        start = int(start_s) if start_s else 0
        end = int(end_s) if end_s else size - 1
        if start > end or end >= size:
            end = size - 1
        return start, end
    except Exception:
        return None


@router.api_route("/media/{media_id}/stream", methods=["GET", "HEAD"])
async def stream_media(media_id: str, request: Request,
                       range_header: Optional[str] = Header(default=None, alias="Range"),
                       user: Optional[dict] = Depends(optional_user)):
    db = get_db()
    asset = await db["media_assets"].find_one({"_id": media_id})
    if not asset or asset.get("status") != "ready" or not asset.get("gridfs_file_id"):
        raise not_found("Media not available.")
    # Withdrawn/quarantined or private drafts fail public delivery.
    if asset.get("status") == "quarantined" or asset.get("visibility") != "public":
        raise forbidden("This media is not available.")

    size = int(asset.get("bytes") or 0)
    mime = asset.get("mime") or "application/octet-stream"
    etag = f'"{asset.get("content_checksum")}"'
    bucket = gridfs_bucket("media")
    file_id = asset["gridfs_file_id"]

    base_headers = {
        "ETag": etag,
        "Accept-Ranges": "bytes",
        "Cache-Control": "public, max-age=31536000, immutable",
        "Content-Type": mime,
    }

    if request.method == "HEAD":
        return Response(status_code=200, headers={**base_headers, "Content-Length": str(size)})

    rng = _parse_range(range_header, size) if range_header else None

    async def _iter(start: int, length: int):
        stream = await bucket.open_download_stream(file_id)
        try:
            if start:
                await stream.seek(start)
            remaining = length
            chunk_size = 64 * 1024
            while remaining > 0:
                data = await stream.read(min(chunk_size, remaining))
                if not data:
                    break
                remaining -= len(data)
                yield data
        finally:
            await stream.close()

    if rng:
        start, end = rng
        length = end - start + 1
        headers = {**base_headers, "Content-Range": f"bytes {start}-{end}/{size}",
                   "Content-Length": str(length)}
        return StreamingResponse(_iter(start, length), status_code=206, headers=headers, media_type=mime)

    headers = {**base_headers, "Content-Length": str(size)}
    return StreamingResponse(_iter(0, size), status_code=200, headers=headers, media_type=mime)
