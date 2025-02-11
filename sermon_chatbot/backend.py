from petrabot.reasoning.agents import ReactAgent
from petrabot.reasoning.types import LLMMetadata
from petrabot.tools.tool import tool
from database.youtube_utils import get_video_metadata
from database.sqlite.vars import sqlite_engine as engine
from cli_tool.tool import create_db_session
from petrabot.utils.agent_utils import ChatHistory, update_chat_history

from google import genai
from dotenv import load_dotenv
from os import getenv

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

def process_streamlit_messages_to_petrasermonbot_chat_history(messages: list, chat_history: ChatHistory):
    message = messages[-1]
    role = message["role"]
    if role == 'assistant':
        role = 'model'
    prompt = message["content"]
    
    update_chat_history(
        history=chat_history,
        role = role,
        msg = prompt
    )
    
    return chat_history

def initialize_chat_requirements():
    chat_history = ChatHistory()
    client = genai.Client(
        api_key=getenv("GEMINI_API_KEY"),
        http_options={
            'api_version': 'v1beta'
        }
    )
    llm_metadata = LLMMetadata(
        client=client,
        model="gemini-2.0-flash-exp",
        client_type="google",
    )
    
    tools = [get_transcript]
    
    return {
        'chat_history': chat_history,
        'llm_metadata': llm_metadata,
        'tools': tools
    }

def update_system_prompt(agent: ReactAgent, title: str):
    """
    Updates the system prompt of the ReactAgent with the given title.

    Args:
        agent (ReactAgent): The agent whose system prompt is to be updated.
        title (str): The title to be included in the system prompt.

    Returns:
        ReactAgent: The agent with the updated system prompt.
    """
    agent.system_prompt = agent.system_prompt % title
    return agent

def update_streamlit_messages_with_petrasermonbot_responses(messages: list, response: str):
    messages.append({
        'role': 'assistant',
        'content': response
    })
    return messages

def get_all_sermon_titles():
    session = create_db_session(engine)
    sermons = get_video_metadata(session)
    session.close()
    
    return [sermon['title'] for sermon in sermons]