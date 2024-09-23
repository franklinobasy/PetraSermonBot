import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import SermonYtId, Base
from database.youtube_utils import (
    add_new_youtube_id, get_youtube_video_by_id, get_video_id_by_title,
    get_transcript_by_title, get_transcript_by_video_id, update_youtube_title,
    update_transcript_by_title, update_transcript_by_video_id, delete_youtube_video,
    get_all_videos, video_exists_by_title, get_transcript, list_all_titles
)

# Setup for the test database (SQLite in-memory database)
@pytest.fixture(scope='function')
def session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()
    Base.metadata.drop_all(engine)


def test_add_new_youtube_id(session):
    # Adding a new YouTube video record
    video_id = "test_video_id"
    title = "Test Video"
    preacher = "Test Preacher"
    transcript = "Test transcript content."

    add_new_youtube_id(session, title, preacher, video_id, transcript)
    
    # Retrieve from the database and assert the data is correct
    video = session.query(SermonYtId).filter_by(video_id=video_id).first()
    assert video is not None
    assert video.title == title
    assert video.preacher == preacher
    assert video.transcript == transcript


def test_add_existing_youtube_id(session):
    # Adding the same YouTube video twice should raise an error
    video_id = "duplicate_video_id"
    title = "Duplicate Video"
    preacher = "Test Preacher"
    transcript = "Test transcript content."
    
    add_new_youtube_id(session, title, preacher, video_id, transcript)
    
    with pytest.raises(ValueError, match="Video ID already exists!"):
        add_new_youtube_id(session, title, preacher, video_id, transcript)


def test_get_youtube_video_by_id(session):
    # Add a video and retrieve it
    video_id = "video_to_find"
    title = "Find This Video"
    preacher = "Preacher"
    transcript = "Transcript"
    
    add_new_youtube_id(session, title, preacher, video_id, transcript)
    
    video = get_youtube_video_by_id(session, video_id)
    
    assert video is not None
    assert video.title == title
    assert video.preacher == preacher
    assert video.transcript == transcript

def test_get_video_id_by_title(session):
    # Add a video and retrieve it by title
    video_id = "title_video_id"
    title = "Find By Title"
    preacher = "Preacher"
    transcript = "Transcript"

    add_new_youtube_id(session, title, preacher, video_id, transcript)
    
    found_video_id = get_video_id_by_title(session, title)
    
    assert found_video_id == video_id


def test_get_transcript_by_title(session):
    title = "Test Transcript Title"
    video_id = "transcript_video_id"
    preacher = "Test Preacher"
    transcript = "Sample transcript."
    
    add_new_youtube_id(session, title, preacher, video_id, transcript)
    
    result_transcript = get_transcript_by_title(session, title)
    
    assert result_transcript == transcript

def test_delete_youtube_video(session):
    video_id = "video_to_delete"
    title = "Delete Video"
    preacher = "Preacher"
    transcript = "Transcript to be deleted"
    
    add_new_youtube_id(session, title, preacher, video_id, transcript)
    
    delete_youtube_video(session, video_id)
    
    # Ensure it's deleted
    video = get_youtube_video_by_id(session, video_id)
    assert video is None


def test_add_new_youtube_id_missing_params(session):
    # Add a YouTube video with missing or invalid parameters
    with pytest.raises(ValueError, match="All fields .* must be provided."):
        add_new_youtube_id(session, None, None, None, None)


def test_get_non_existent_youtube_video_by_id(session):
    video = get_youtube_video_by_id(session, "non_existent_id")
    assert video is None
