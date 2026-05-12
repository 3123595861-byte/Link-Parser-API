import logging
import httpx
from bs4 import BeautifulSoup
from app.core.schemas import ExtractResponse

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent":(
        "Mozilla/5.0 (Windows NT 10.0;Win64;x64) "
        "AppleWebkit/537.36 (KHTML,Like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept":"text/html,application/xhtml+xml,allpication/xml;q=0.9,*/*;q=0.8"
}

class ParserError(Exception):
    """解析链接过程中可预期的业务异常。"""

    pass


async def _fetch_html(url: str, client: httpx.AsyncClient | None = None) -> str:
    try:
        # 测试时允许注入自定义 client，避免真实联网。
        if client is not None:
            response = await client.get(url,headers = DEFAULT_HEADERS)
        else:
            async with httpx.AsyncClient(timeout=10.0) as default_client:
                response = await default_client.get(url,headers = DEFAULT_HEADERS)

        response.raise_for_status()

        content_type = response.headers.get("content-type", "")
        # 当前解析器只处理 HTML 页面，非 HTML 内容直接拒绝。
        if "text/html" not in content_type.lower():
            raise ParserError(f"URL did not return HTML content: {url}")

        return response.text
    except httpx.TimeoutException as exc:
        raise ParserError(f"Request timed out: {url}") from exc
    except httpx.HTTPStatusError as exc:
        raise ParserError(
            f"HTTP error while fetching {url}: {exc.response.status_code}"
        ) from exc
    except httpx.RequestError as exc:
        raise ParserError(f"Request error while fetching {url}") from exc


def _extract_title(html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    if soup.title and soup.title.string.strip():
        return soup.title.string.strip()
    return None


def _extract_description(html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")

    # 优先使用 Open Graph 描述，通常比普通 description 更适合做链接卡片展示。
    og_description = soup.find("meta", property="og:description")
    if og_description:
        content = og_description.get("content")
        if content:
            return content.strip()

    # 如果没有 og:description，再回退到标准 description。
    normal_description = soup.find("meta", attrs={"name": "description"})
    if normal_description:
        content = normal_description.get("content")
        if content:
            return content.strip()

    return None


def _extract_image(html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    og_image = soup.find("meta", property="og:image")
    if og_image:
        content = og_image.get("content")
        if content:
            return content.strip()
    return None


async def extract_metadata(
    url: str,
    client: httpx.AsyncClient | None = None,
) -> ExtractResponse:
    try:
        logger.info("Start extracting metadata for url=%s", url)

        html = await _fetch_html(url, client)
        title = _extract_title(html)
        description = _extract_description(html)
        image = _extract_image(html)

        result = ExtractResponse(
            url=url,
            title=title,
            description=description,
            image=image,
        )
        logger.info("Successfully extracted metadata for url=%s", url)
        return result
    except Exception:
        logger.exception("Failed to extract metadata for url=%s", url)
        raise
