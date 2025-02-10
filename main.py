
from os import getenv
from dotenv import load_dotenv
from petrabot.reasoning.types import LLMMetadata
from petrabot.tools.tool import tool
from petrabot.utils.agent_utils import ChatHistory, build_prompt_structure
from petrabot.reasoning.agents import ReactAgent
from database.sqlite.vars import sqlite_engine as engine
from database.youtube_utils import get_video_metadata
from cli_tool.tool import create_db_session

from google import genai
from google.genai import types

load_dotenv()

@tool
def get_transcript(teaching_title: str) -> dict:
    """
    Gets the transcript of the teaching video.

    Args:
        teaching_title (str): The title of the teaching video.

    Returns:
        dict: The name of the Teacher and The transcript of the teaching video.
    """
    
    session = create_db_session(engine)
    video = get_video_metadata(session, title=teaching_title)[0]
    transcript = video["transcript"]
    preacher = video["preacher"]
    session.close()
    
    return {
        "preacher": preacher,
        "transcript": transcript
    }
    
system_prompt = "The title of the teaching video is 'That I May Know Him'. "

chat_history = ChatHistory()

client = genai.Client(
    api_key=getenv("GEMINI_API_KEY"),
    http_options={
        'api_version': 'v1beta'
    }
)

llm_medata = LLMMetadata(
    client=client,
    model="gemini-2.0-flash-exp",
    client_type="google",
)

agent = ReactAgent(llm_medata, tools=[get_transcript], system_prompt=system_prompt)

print("You are now in a conversation with Petra Sermon Bot. Type 'exit' to end the conversation.")
while True:
    user_msg = input("User: ")
    if user_msg == "exit":
        break
    response = agent.run(user_msg, chat_history)
    print("Bot:", response)
