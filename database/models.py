from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class SermonYtId(Base):
    """Model representing a YouTube sermon video with its title, ID, and transcript."""
    __tablename__ = 'sermon_youtube_id'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    video_id = Column(String, nullable=False, unique=True, index=True)
    transcript = Column(Text, nullable=False)
