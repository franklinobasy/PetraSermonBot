from datetime import datetime
from pydantic import BaseModel, Field
from uuid import uuid4
from typing import List


class PromptModel(BaseModel):
    question: str
    answer: str
    

class ConversationModel(BaseModel):
    date_created: datetime = Field(default_factory=datetime.utcnow)
    date_modified: datetime = Field(default_factory=datetime.utcnow)
    conversation_name: str = "New conversation"
    conversation_id: str = Field(default_factory=lambda: uuid4().hex)
    prompts: List[PromptModel] = []


class UserConversionModel(BaseModel):
    user_id: str = Field(default_factory=lambda: uuid4().hex)
    conversations: List[ConversationModel] = []
