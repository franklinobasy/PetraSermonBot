import argparse
import logging

from sqlalchemy.orm import sessionmaker

from database.sqlite.vars import sqlite_engine as engine
from database.youtube_utils import (
    add_new_youtube_id,
    get_youtube_video_by_id,
    get_video_id_by_title,
    get_transcript_by_title,
    get_transcript_by_video_id,
    update_youtube_title,
    update_transcript_by_title,
    update_transcript_by_video_id,
    delete_youtube_video,
    delete_youtube_video_by_pk,
    get_all_videos,
    list_all_titles,
    video_exists_by_title,
    get_transcript,
    get_video_metadata,
)
from database.models import Base

# Configure logging for CLI output.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_db_session(engine):
    """
    Create the SQLAlchemy engine and session, and initialize the database.
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.create_all(engine)
    return session


def main():
    parser = argparse.ArgumentParser(
        description="CLI tool for interacting with the YouTube Sermon Database."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ----------------------
    # Add a new video
    # ----------------------
    parser_add = subparsers.add_parser("add", help="Add a new video entry")
    parser_add.add_argument("--title", required=True, help="Title of the video")
    parser_add.add_argument("--preacher", required=True, help="Preacher's name")
    parser_add.add_argument("--video_id", required=True, help="YouTube video ID")
    parser_add.add_argument(
        "--transcript",
        help=(
            "Transcript text for the video. "
            "If omitted, the CLI will attempt to fetch the transcript from the YouTube API."
        ),
    )

    # ----------------------
    # Get video details
    # ----------------------
    parser_get_video = subparsers.add_parser(
        "get-video", help="Get video details by video ID or title"
    )
    group_get_video = parser_get_video.add_mutually_exclusive_group(required=True)
    group_get_video.add_argument("--video_id", help="YouTube video ID")
    group_get_video.add_argument("--title", help="Title of the video")

    # ----------------------
    # Get transcript
    # ----------------------
    parser_get_transcript = subparsers.add_parser(
        "get-transcript", help="Get transcript by video ID or title"
    )
    group_get_transcript = parser_get_transcript.add_mutually_exclusive_group(required=True)
    group_get_transcript.add_argument("--video_id", help="YouTube video ID")
    group_get_transcript.add_argument("--title", help="Title of the video")

    # ----------------------
    # List videos
    # ----------------------
    parser_list = subparsers.add_parser("list", help="List videos in the database")
    parser_list.add_argument(
        "--titles",
        action="store_true",
        help="If provided, only list the video titles.",
    )

    # ----------------------
    # Update video title
    # ----------------------
    parser_update_title = subparsers.add_parser("update-title", help="Update video title")
    parser_update_title.add_argument("--video_id", required=True, help="YouTube video ID")
    parser_update_title.add_argument("--new-title", required=True, help="New title for the video")

    # ----------------------
    # Update transcript
    # ----------------------
    parser_update_transcript = subparsers.add_parser("update-transcript", help="Update video transcript")
    group_update_transcript = parser_update_transcript.add_mutually_exclusive_group(required=True)
    group_update_transcript.add_argument("--video_id", help="YouTube video ID")
    group_update_transcript.add_argument("--title", help="Title of the video")
    parser_update_transcript.add_argument("--new-transcript", required=True, help="New transcript text")

    # ----------------------
    # Delete a video
    # ----------------------
    parser_delete = subparsers.add_parser("delete", help="Delete a video entry")
    group_delete = parser_delete.add_mutually_exclusive_group(required=True)
    group_delete.add_argument("--video_id", help="YouTube video ID")
    group_delete.add_argument("--pk", type=int, help="Primary key of the video entry")

    # ----------------------
    # Check existence of a video by title
    # ----------------------
    parser_exists = subparsers.add_parser("exists", help="Check if a video exists by title")
    parser_exists.add_argument("--title", required=True, help="Title of the video")

    # ----------------------
    # Fetch transcript (DB or API)
    # ----------------------
    parser_fetch_transcript = subparsers.add_parser(
        "fetch-transcript",
        help="Fetch transcript for a video (from DB or YouTube API)",
    )
    parser_fetch_transcript.add_argument("--title", required=True, help="Title of the video")
    parser_fetch_transcript.add_argument("--preacher", required=True, help="Preacher's name")
    parser_fetch_transcript.add_argument("--video_id", required=True, help="YouTube video ID")

    # ----------------------
    # Get video metadata (single or all)
    # ----------------------
    parser_metadata = subparsers.add_parser("metadata", help="Get video metadata (single or all)")
    parser_metadata.add_argument("--title", help="Title of the video (optional)")
    parser_metadata.add_argument("--video_id", help="YouTube video ID (optional)")

    args = parser.parse_args()

    # Create a DB session
    session = create_db_session(engine)

    if args.command == "add":
        transcript = args.transcript
        if transcript is None:
            # If no transcript was provided, try fetching it via the YouTube API.
            transcript = get_transcript(session, args.title, args.preacher, args.video_id)
            if transcript is None:
                print("Transcript could not be retrieved.")
                return

        result = add_new_youtube_id(session, args.title, args.preacher, args.video_id, transcript)
        if result:
            print(f"Video added successfully with video ID: {result}")
        else:
            print("Failed to add video.")

    elif args.command == "get-video":
        if args.video_id:
            video = get_youtube_video_by_id(session, args.video_id)
        else:
            vid_id = get_video_id_by_title(session, args.title)
            video = get_youtube_video_by_id(session, vid_id) if vid_id else None
        if video:
            print("Video Details:")
            print(f"  Primary Key: {video.id}")
            print(f"  Title: {video.title}")
            print(f"  Preacher: {video.preacher}")
            print(f"  Video ID: {video.video_id}")
            # Limit transcript preview to first 100 characters.
            transcript_preview = video.transcript[:100] + ("..." if len(video.transcript) > 100 else "")
            print(f"  Transcript: {transcript_preview}")
        else:
            print("Video not found.")

    elif args.command == "get-transcript":
        transcript = None
        if args.video_id:
            transcript = get_transcript_by_video_id(session, args.video_id)
        else:
            transcript = get_transcript_by_title(session, args.title)
        if transcript:
            print("Transcript:")
            print(transcript)
        else:
            print("Transcript not found.")

    elif args.command == "list":
        if args.titles:
            titles = list_all_titles(session)
            print("Video Titles:")
            for t in titles:
                print(f"  - {t}")
        else:
            videos = get_all_videos(session)
            print("Videos in Database:")
            for video in videos:
                print(
                    f"PK: {video.id} | Title: {video.title} | Preacher: {video.preacher} | Video ID: {video.video_id}"
                )

    elif args.command == "update-title":
        success = update_youtube_title(session, args.video_id, args.new_title)
        if success:
            print("Video title updated successfully.")
        else:
            print("Failed to update video title.")

    elif args.command == "update-transcript":
        if args.video_id:
            success = update_transcript_by_video_id(session, args.video_id, args.new_transcript)
        else:
            success = update_transcript_by_title(session, args.title, args.new_transcript)
        if success:
            print("Transcript updated successfully.")
        else:
            print("Failed to update transcript.")

    elif args.command == "delete":
        if args.video_id:
            success = delete_youtube_video(session, args.video_id)
        else:
            success = delete_youtube_video_by_pk(session, args.pk)
        if success:
            print("Video deleted successfully.")
        else:
            print("Failed to delete video.")

    elif args.command == "exists":
        if video_exists_by_title(session, args.title):
            print(f"Video titled '{args.title}' exists in the database.")
        else:
            print(f"Video titled '{args.title}' does not exist.")

    elif args.command == "fetch-transcript":
        transcript = get_transcript(session, args.title, args.preacher, args.video_id)
        if transcript:
            print("Transcript:")
            print(transcript)
        else:
            print("Transcript not available.")

    elif args.command == "metadata":
        # Retrieve metadata using the new helper function.
        metadata_list = get_video_metadata(session, title=args.title, video_id=args.video_id)
        if metadata_list:
            print("Video Metadata:")
            for meta in metadata_list:
                print(
                    f"PK: {meta['id']} | Title: {meta['title']} | Preacher: {meta['preacher']} | "
                    f"Video ID: {meta['video_id']}"
                )
        else:
            print("No video metadata found.")

    else:
        parser.print_help()