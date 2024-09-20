from youtube_transcript_api import YouTubeTranscriptApi
from database.utils import (
    add_new_youtube_id,
    update_transcript_by_video_id,
    update_youtube_title,
    get_transcript_by_video_id
)

def get_transcript(title, video_id):
    """Retrieve the transcript for a given YouTube video title and ID.

    Tries to fetch the transcript from the database first, and if not found,
    it retrieves it from the YouTube API, updates the database, and returns the transcript.

    Args:
        title (str): The title of the YouTube video.
        video_id (str): The YouTube video ID.

    Returns:
        str or None: The transcript text if found, else None.
    """
    # Try to get the transcript from the database
    transcript = get_transcript_by_video_id(video_id=video_id)
    if transcript:
        return transcript
    
    # If not found in the database, fetch it from YouTube
    try:
        ts = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = "".join([_['text'] for _ in ts])

        # Attempt to add new entry to the database
        try:
            add_new_youtube_id(title=title, video_id=video_id, transcript=transcript)
        except Exception as db_error:
            print(f"Error adding new YouTube ID: {db_error}")

        return transcript

    except Exception as e:
        print(f"Error retrieving transcript from YouTube: {e}")

    return None
