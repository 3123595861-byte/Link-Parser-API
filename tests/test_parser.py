from typing import Any
import httpx
import pytest
from fastapi.testclient import TestClient
from app.core.schemas import ExtractResponse
from app.main import app
from app.services.parser import ParserError, extract_metadata

client = TestClient(app)

@pytest.mark.asyncio
async def test_extract_metadata_with_mock_http_client() -> None:
    html = """
    <html>
        <head>
            <title>Example Domain</title>
            <meta property="og:description" content="Example OG Description">
            <meta name="description" content="Example Normal Description">
            <meta property="og:image" content="https://example.com/image.png">
        </head>
        <body>
            <p>Hello</p>
        </body>
    </html>
    """
    def handler(request: httpx.Request) -> httpx.Response:
        assert "Mozilla/5.0" in request.headers["user-agent"]
        return httpx.Response(
            200,
            text=html,
            headers={"content-type": "text/html; charset=utf-8"},
        )
    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(transport = transport) as mock_client:
        result = await extract_metadata(
            "https://example.com",
            client = mock_client
        )
    assert result.url == "https://example.com"
    assert result.title == "Example Domain"
    assert result.description == "Example OG Description"
    assert result.image == "https://example.com/image.png"

@pytest.mark.asyncio
async def test_extract_metadata_rejects_non_html_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"message": "not html"},
            headers={"content-type": "application/json"},
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(transport=transport) as mock_client:
        with pytest.raises(ParserError):
            await extract_metadata(
                "https://example.com/api",
                client=mock_client,
            )

def test_extract_endpoint_with_mock_service(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_extract_metadata(url: str) -> ExtractResponse:
        return ExtractResponse(
        url=url,
        title="Fake Title",
        description="Fake Description",
        image="https://fake.example/image.png",
        )
    monkeypatch.setattr(
        "app.api.endpoints.extract_metadata",
        fake_extract_metadata,
    )
    response = client.post(
        "/extract",
        json={"url": "https://example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["url"] == "https://example.com/"
    assert data["title"] == "Fake Title"
    assert data["description"] == "Fake Description"
    assert data["image"] == "https://fake.example/image.png"

def test_extract_endpoint_returns_400_for_parser_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_extract_metadata(url:str) -> ExtractResponse:
        raise ParserError("Request timed out: https://example.com/")
    monkeypatch.setattr(
        "app.api.endpoints.extract_metadata",
        fake_extract_metadata,
    )
    response = client.post(
        "/extract",
        json = {"url":"https://example.com"},
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail" : "Request timed out: https://example.com/",
    }