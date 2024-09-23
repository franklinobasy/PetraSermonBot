from sqlalchemy.exc import IntegrityError
from youtube_transcript_api import YouTubeTranscriptApi
from .models import SermonYtId

# Add a new YouTube video entry
def add_new_youtube_id(session, title, preacher, video_id, transcript):
    """Add a new YouTube video entry to the database."""
    if not all([title, preacher, video_id, transcript]):
        raise ValueError("All fields (title, preacher, video_id, transcript) must be provided.")
    
    if session.query(SermonYtId).filter_by(video_id=video_id).first():
        raise ValueError("Video ID already exists!")
    
    try:
        new_video = SermonYtId(title=title, preacher=preacher, video_id=video_id, transcript=transcript)
        session.add(new_video)
        session.commit()
        print(f"Added new YouTube video with ID {new_video.id}")
        return new_video.video_id
    except IntegrityError:
        session.rollback()
        print("Error while adding new data.")
        return None

# Retrieve a YouTube video by its ID
def get_youtube_video_by_id(session, video_id):
    """Retrieve a YouTube video record by its video ID."""
    video = session.query(SermonYtId).filter_by(video_id=video_id).first()
    if video:
        return video
    print(f"No video found with video ID: {video_id}")
    return None

# Retrieve video ID by its title
def get_video_id_by_title(session, title):
    """Retrieve the video ID associated with a given title."""
    video = session.query(SermonYtId).filter_by(title=title).first()
    if video:
        return video.video_id
    print(f"No video found with title: {title}")
    return None

# Retrieve transcript by title
def get_transcript_by_title(session, title):
    """Retrieve the transcript of a video by its title."""
    video = session.query(SermonYtId).filter_by(title=title).first()
    if video:
        return video.transcript
    print(f"No transcript found for title: {title}")
    return None

# Retrieve transcript by video ID
def get_transcript_by_video_id(session, video_id):
    """Retrieve the transcript of a video by its video ID."""
    video = session.query(SermonYtId).filter_by(video_id=video_id).first()
    if video:
        return video.transcript
    print(f"No transcript found for video ID: {video_id}")
    return None

# Update the title of an existing YouTube video
def update_youtube_title(session, video_id, new_title):
    """Update the title of an existing YouTube video."""
    video = session.query(SermonYtId).filter_by(video_id=video_id).first()
    if video:
        video.title = new_title
        session.commit()
        print(f"Updated video title to '{new_title}' for video ID: {video_id}")
    else:
        print(f"No video found with video ID: {video_id}")

# Update transcript by title
def update_transcript_by_title(session, title, new_transcript):
    """Update the transcript of a video by its title."""
    video = session.query(SermonYtId).filter_by(title=title).first()
    if video:
        video.transcript = new_transcript
        session.commit()
        print(f"Updated transcript for video titled '{title}'")
    else:
        print(f"No video found with title: {title}")

# Update transcript by video ID
def update_transcript_by_video_id(session, video_id, new_transcript):
    """Update the transcript of a video by its video ID."""
    video = session.query(SermonYtId).filter_by(video_id=video_id).first()
    if video:
        video.transcript = new_transcript
        session.commit()
        print(f"Updated transcript for video ID: {video_id}")
    else:
        print(f"No video found with video ID: {video_id}")

# Delete a YouTube video by its ID
def delete_youtube_video(session, video_id):
    """Delete a YouTube video from the database using its ID."""
    video = session.query(SermonYtId).filter_by(video_id=video_id).first()
    if video:
        session.delete(video)
        session.commit()
        print(f"Deleted video with ID: {video_id}")
    else:
        print(f"No video found with video ID: {video_id}")

def delete_youtube_video_by_pk(session, pk):
    """Delete a YouTube video from the database using its primary key."""
    video = session.query(SermonYtId).filter_by(id=pk).first()
    if video:
        session.delete(video)
        session.commit()
        print(f"Deleted video with primary key: {pk}")
    else:
        print(f"No video found with primary key: {pk}")

# Retrieve all videos in the database
def get_all_videos(session):
    """Retrieve all YouTube videos in the database."""
    return session.query(SermonYtId).all() or []

# Check if a YouTube video exists by its title
def video_exists_by_title(session, title):
    """Check if a video exists in the database based on its title."""
    return session.query(SermonYtId).filter_by(title=title).first() is not None

# Retrieve transcript from the database or YouTube API
def get_transcript(session, title, preacher, video_id):
    """Retrieve the transcript for a given YouTube video.

    Tries to fetch the transcript from the database first, if not found,
    it retrieves it from the YouTube API, updates the database, and returns the transcript.
    
    Args:
        title (str): The title of the YouTube video.
        preacher (str): The preacher's name.
        video_id (str): The YouTube video ID.
    
    Returns:
        str or None: The transcript text if found, else None.
    """
    transcript = get_transcript_by_video_id(session, video_id)
    if transcript:
        return transcript
    
    # Fetch transcript from YouTube API if not found in the database
    try:
        ts = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = "".join([entry['text'] for entry in ts])
        add_new_youtube_id(session, title=title, preacher=preacher, video_id=video_id, transcript=transcript)
        return transcript
    except Exception as e:
        print(f"Error retrieving transcript from YouTube: {e}")
        return None

# List all video titles
def list_all_titles(session):
    """Retrieve the titles of all YouTube videos in the database."""
    return [video.title for video in session.query(SermonYtId).all()]
