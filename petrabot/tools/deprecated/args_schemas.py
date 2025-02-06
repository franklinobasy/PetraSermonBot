from pydantic import BaseModel, Field


class SermonQueryInput(BaseModel):
    title: str=Field(description="Title of sermon")
    query: str=Field(description="User's query about sermon")
