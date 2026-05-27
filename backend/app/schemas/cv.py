from pydantic import BaseModel


class CVIngestResponse(BaseModel):
    file_name: str
    chunk_count: int
    collection: str
    ids: list[str]


class CVUploadResponse(BaseModel):
    file_id: str
    file_name: str
