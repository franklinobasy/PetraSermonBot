import logging
from typing import Optional, List, Dict, Any

from sqlalchemy.exc import IntegrityError
from youtube_transcript_api import YouTubeTranscriptApi
from .models import SermonYtId

# Configure a logger for the module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Adjust as needed

# You can configure a console handler if desired:
if not logger.handlers:
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def _get_video(session, **filters) -> Optional[SermonYtId]:
    """Helper function to retrieve a video using filter criteria."""
    return session.query(SermonYtId).filter_by(**filters).first()


def add_new_youtube_id(
    session, 
    title: str, 
    preacher: str, 
    video_id: str, 
    transcript: str
) -> Optional[str]:
    """
    Add a new YouTube video entry to the database.
    Returns the video_id on success or None on failure.
    """
    if not all([title, preacher, video_id, transcript]):
        raise ValueError("All fields (title, preacher, video_id, transcript) must be provided.")
    
    # Avoid duplicates based on the unique video_id field.
    if _get_video(session, video_id=video_id):
        raise ValueError("Video ID already exists!")
    
    new_video = SermonYtId(
        title=title, 
        preacher=preacher, 
        video_id=video_id, 
        transcript=transcript
    )
    session.add(new_video)
    try:
        session.commit()
        logger.info("Added new YouTube video with primary key %s", new_video.id)
        return new_video.video_id
    except IntegrityError as e:
        session.rollback()
        logger.error("Error while adding new video: %s", e)
        return None


def get_youtube_video_by_id(session, video_id: str) -> Optional[SermonYtId]:
    """Retrieve a YouTube video record by its video ID."""
    video = _get_video(session, video_id=video_id)
    if not video:
        logger.warning("No video found with video ID: %s", video_id)
    return video


def get_video_id_by_title(session, title: str) -> Optional[str]:
    """Retrieve the video ID associated with a given title."""
    video = _get_video(session, title=title)
    if not video:
        logger.warning("No video found with title: %s", title)
        return None
    return video.video_id


def get_transcript_by_title(session, title: str) -> Optional[str]:
    """Retrieve the transcript of a video by its title."""
    video = _get_video(session, title=title)
    if not video:
        logger.warning("No transcript found for title: %s", title)
        return None
    return video.transcript


def get_transcript_by_video_id(session, video_id: str) -> Optional[str]:
    """Retrieve the transcript of a video by its video ID."""
    video = _get_video(session, video_id=video_id)
    if not video:
        logger.warning("No transcript found for video ID: %s found in database", video_id)
        return None
    return video.transcript


def update_youtube_title(session, video_id: str, new_title: str) -> bool:
    """Update the title of an existing YouTube video."""
    video = _get_video(session, video_id=video_id)
    if not video:
        logger.warning("No video found with video ID: %s", video_id)
        return False

    video.title = new_title
    try:
        session.commit()
        logger.info("Updated video title to '%s' for video ID: %s", new_title, video_id)
        return True
    except Exception as e:
        session.rollback()
        logger.error("Error updating video title: %s", e)
        return False


def update_transcript(session, video_filter: Dict[str, Any], new_transcript: str) -> bool:
    """
    General helper to update a video's transcript based on a filter dictionary.
    """
    video = _get_video(session, **video_filter)
    if not video:
        logger.warning("No video found with filter: %s", video_filter)
        return False

    video.transcript = new_transcript
    try:
        session.commit()
        logger.info("Updated transcript for video with filter: %s", video_filter)
        return True
    except Exception as e:
        session.rollback()
        logger.error("Error updating transcript: %s", e)
        return False


def update_transcript_by_title(session, title: str, new_transcript: str) -> bool:
    """Update the transcript of a video by its title."""
    return update_transcript(session, {"title": title}, new_transcript)


def update_transcript_by_video_id(session, video_id: str, new_transcript: str) -> bool:
    """Update the transcript of a video by its video ID."""
    return update_transcript(session, {"video_id": video_id}, new_transcript)


def delete_youtube_video(session, video_id: str) -> bool:
    """Delete a YouTube video from the database using its video ID."""
    video = _get_video(session, video_id=video_id)
    if not video:
        logger.warning("No video found with video ID: %s", video_id)
        return False

    session.delete(video)
    try:
        session.commit()
        logger.info("Deleted video with video ID: %s", video_id)
        return True
    except Exception as e:
        session.rollback()
        logger.error("Error deleting video: %s", e)
        return False


def delete_youtube_video_by_pk(session, pk: int) -> bool:
    """Delete a YouTube video from the database using its primary key."""
    video = _get_video(session, id=pk)
    if not video:
        logger.warning("No video found with primary key: %s", pk)
        return False

    session.delete(video)
    try:
        session.commit()
        logger.info("Deleted video with primary key: %s", pk)
        return True
    except Exception as e:
        session.rollback()
        logger.error("Error deleting video: %s", e)
        return False


def get_all_videos(session) -> List[SermonYtId]:
    """Retrieve all YouTube videos in the database."""
    return session.query(SermonYtId).all()


def list_all_titles(session) -> List[str]:
    """Retrieve the titles of all YouTube videos in the database."""
    videos = get_all_videos(session)
    return [video.title for video in videos]


def video_exists_by_title(session, title: str) -> bool:
    """Check if a video exists in the database based on its title."""
    return _get_video(session, title=title) is not None


def get_transcript(session, title: str, preacher: str, video_id: str) -> Optional[str]:
    """
    Retrieve the transcript for a given YouTube video.
    
    Tries to fetch the transcript from the database first; if not found,
    it retrieves it from the YouTube API, updates the database, and returns the transcript.
    """
    transcript = get_transcript_by_video_id(session, video_id)
    if transcript:
        return transcript

    # Fetch transcript from the YouTube API if not found in the database.
    try:
        logger.info("Fetching transcript from YouTube for video ID: %s", video_id)
        transcript_entries = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join(entry['text'] for entry in transcript_entries)
        # add_new_youtube_id(
        #     session,
        #     title=title,
        #     preacher=preacher,
        #     video_id=video_id,
        #     transcript=transcript_text
        # )
        return transcript_text
    except Exception as e:
        logger.error("Error retrieving transcript from YouTube for video_id %s: %s", video_id, e)
        return None


def get_video_metadata(
    session,
    title: Optional[str] = None,
    video_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve video metadata by title or video_id.
    
    If both title and video_id are provided, the function filters on both.
    If neither is provided, the function retrieves metadata for all videos.
    
    Args:
        session (Session): The SQLAlchemy database session.
        title (Optional[str]): The title of the video.
        video_id (Optional[str]): The YouTube video ID.
        
    Returns:
        List[Dict[str, Any]]: A list of dictionaries where each dictionary contains
                              metadata for a video (id, title, preacher, video_id, transcript).
                              Returns an empty list if no videos are found.
    """
    try:
        # If no filters are provided, retrieve all videos.
        if title is None and video_id is None:
            videos = session.query(SermonYtId).all()
            logger.info("No filters provided. Retrieving all videos (%d found).", len(videos))
        else:
            filters = {}
            if title:
                filters["title"] = title
            if video_id:
                filters["video_id"] = video_id

            videos = session.query(SermonYtId).filter_by(**filters).all()
            logger.info("Filters %s applied. %d video(s) found.", filters, len(videos))

        # Construct a list of metadata dictionaries.
        metadata_list = []
        for video in videos:
            metadata_list.append({
                "id": video.id,
                "title": video.title,
                "preacher": video.preacher,
                "video_id": video.video_id,
                "transcript": video.transcript,
            })
        return metadata_list

    except Exception as e:
        logger.error("Error retrieving video metadata: %s", e)
        return []