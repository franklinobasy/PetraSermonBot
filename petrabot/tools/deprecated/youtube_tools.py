from typing import Optional, Type

from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker
from database.vectorstore.chromadb.vector import get_retriever

from database.youtube_utils import get_transcript_by_title, get_video_id_by_title

from .args_schemas import SermonQueryInput
from database import engine


class SermonTrascriptTool(BaseTool):
    name: str="SermonTranscript"
    description: str="Use this tool to retrive contents from the transcripts of a given sermon title based on a query."
    args_schema: Type[BaseModel] = SermonQueryInput
    return_direct: bool = True
    
    def _run(
        self, title: str, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        Session = sessionmaker(bind=engine)
        session = Session()
        
        ts = get_transcript_by_title(
            session, title
        )
        
        video_id = get_video_id_by_title(
            session,
            title
        )[:10]
        
        session.close()
        
        if not ts:
            return "No contents was found for this title"
        
        retriever = get_retriever(
            id=video_id,
            text=ts
        )
        
        answer = retriever.invoke(query)
        return answer
        