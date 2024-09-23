# import argparse
# from petrabot.youtube.utils import get_transcript

# def main():
#     # Set up argument parser
#     parser = argparse.ArgumentParser(description='Get YouTube transcript by title and video ID.')
    
#     # Add arguments for title and video ID
#     parser.add_argument('--title', type=str, required=True, help='The title of the YouTube video')
#     parser.add_argument('--video_id', type=str, required=True, help='The YouTube video ID')

#     # Parse the arguments
#     args = parser.parse_args()
    
#     # Call the get_transcript function
#     transcript = get_transcript(title=args.title, video_id=args.video_id)

#     # Print the result
#     if transcript:
#         print(f"Transcript for '{args.title}' (Video ID: {args.video_id}):\n")
#         print(transcript)
#     else:
#         print(f"No transcript found for '{args.title}' (Video ID: {args.video_id}).")

# if __name__ == '__main__':
#     main()
