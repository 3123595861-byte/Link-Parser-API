from pydantic import BaseModel ,HttpUrl

class ExtractRequest(BaseModel):
    url: HttpUrl

class ExtractResponse(BaseModel):
    url: str
    title: str | None = None
    description: str | None =None
    image: str | None = None