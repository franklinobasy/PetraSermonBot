from pydantic import BaseModel, Field
from uuid import uuid4


class Sermon(BaseModel):
    sermon_id: str = Field(default_factory=lambda: uuid4().hex)
    title: str
    cover_url: str
    document_url: str
    minister: str
    description: str = None
