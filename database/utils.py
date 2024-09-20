from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from database import engine
from models import SermonYtId

Session = sessionmaker(bind=engine)

# Add new YouTube ID
def add_new_youtube_id(title, video_id, transcript):
    """Add a new YouTube video ID to the database."""
    with Session() as session:
        if session.query(SermonYtId).filter_by(video_id=video_id).first():
            raise Exception("Video ID already exists!")
        
        try:
            data = SermonYtId(title=title, video_id=video_id, transcript=transcript)
            session.add(data)
            session.commit()
            print(f"Added new YouTube video with ID {data.id}")
            return data.id
        except IntegrityError:
            session.rollback()
            print("Error while adding new data.")
            return None

# Retrieve YouTube video by ID
def get_youtube_video_by_id(video_id):
    """Retrieve a YouTube video record by its video ID."""
    with Session() as session:
        result = session.query(SermonYtId).filter_by(video_id=video_id).first()
        if result:
            return result
        else:
            print(f"No video found with video ID: {video_id}")
            return None

# Function to get video_id by title
def get_video_id_by_title(title):
    """Get the video ID associated with a given title."""
    with Session() as session:
        video = session.query(SermonYtId).filter_by(title=title).first()
        if video:
            return video.video_id
        else:
            print(f"No video found with title: {title}")
            return None

# Retrieve transcript by Title
def get_transcript_by_title(title):
    """Retrieve the transcript of a video by its title."""
    with Session() as session:
        video = session.query(SermonYtId).filter_by(title=title).first()
        if video:
            return video.transcript
        else:
            print(f"No transcript found for title: {title}")
            return None

# Retrieve transcript by Video ID
def get_transcript_by_video_id(video_id):
    """Retrieve the transcript of a video by its video ID."""
    with Session() as session:
        video = session.query(SermonYtId).filter_by(video_id=video_id).first()
        if video:
            return video.transcript
        else:
            print(f"No transcript found for video ID: {video_id}")
            return None

# Update YouTube video title
def update_youtube_title(video_id, new_title):
    """Update the title of an existing YouTube video."""
    with Session() as session:
        video = session.query(SermonYtId).filter_by(video_id=video_id).first()
        if video:
            video.title = new_title
            session.commit()
            print(f"Updated video title to '{new_title}' for video ID: {video_id}")
        else:
            print(f"No video found with video ID: {video_id}")

# Update transcript by title
def update_transcript_by_title(title, new_transcript):
    """Update the transcript of a video using its title."""
    with Session() as session:
        video = session.query(SermonYtId).filter_by(title=title).first()
        if video:
            video.transcript = new_transcript
            session.commit()
            print(f"Updated transcript for video titled '{title}'")
        else:
            print(f"No video found with title: {title}")

# Update transcript by video ID
def update_transcript_by_video_id(video_id, new_transcript):
    """Update the transcript of a video using its video ID."""
    with Session() as session:
        video = session.query(SermonYtId).filter_by(video_id=video_id).first()
        if video:
            video.transcript = new_transcript
            session.commit()
            print(f"Updated transcript for video ID: {video_id}")
        else:
            print(f"No video found with video ID: {video_id}")

# Delete YouTube video by ID
def delete_youtube_video(video_id):
    """Delete a YouTube video from the database using its ID."""
    with Session() as session:
        video = session.query(SermonYtId).filter_by(video_id=video_id).first()
        if video:
            session.delete(video)
            session.commit()
            print(f"Deleted video with ID: {video_id}")
        else:
            print(f"No video found with video ID: {video_id}")

# Retrieve all videos
def get_all_videos():
    """Retrieve all YouTube videos in the database."""
    with Session() as session:
        videos = session.query(SermonYtId).all()
        return videos if videos else []

# Check if YouTube video exists by title
def video_exists_by_title(title):
    """Check if a video exists in the database based on its title."""
    with Session() as session:
        return session.query(SermonYtId).filter_by(title=title).first() is not None