from typing import List
from petrabot.reasoning.types import LLMMetadata
from petrabot.utils.constants import LLMClientTypes

from google.genai.types import Content


def groq_chat_completions_create(client, messages: list, model: str, sys_instruct: str, **kwargs) -> str:
    """
    Sends a request to the client's `completions.create` method to interact with the language model.

    Args:
        client (Groq): The Groq client object
        messages (list[dict]): A list of message objects containing chat history for the model.
        model (str): The model to use for generating tool calls and responses.

    Returns:
        str: The content of the model's response.
    """
    response = client.chat.completions.create(messages=messages, model=model)
    return str(response.choices[0].message.content)


def google_chat_completions_create(client, messages: List[Content], model: str, sys_instruct: str, **kwargs) -> str:
    """
    Sends a request to the client's `completions.create` method to interact with the language model.

    Args:
        client (Google): The Google client object
        messages (list[dict]): A list of message objects containing chat history for the model.
        model (str): The model to use for generating tool calls and responses.

    Returns:
        str: The content of the model's response.
    """
    chat = client.chats.create(history=messages, model=model)
    response = chat.send_message(messages[-1])
    return response.text


def google_completions_create(client, content, sys_instruct: str,  model: str) -> str:
    """
    Sends a request to the client's `completions.create` method to interact with the language model.

    Args:
        client (Google): The Google client object
        sys_instruct (str): The system instruction to send to the model.
        model (str): The model to use for generating tool calls and responses.

    Returns:
        str: The content of the model's response.
    """
    response = client.models.generate_content(
        model=model,
        content=content
    )
    return response.choices[0].message.content


def create_completion(
    llm_metadata: LLMMetadata,
    sys_instruct: str,
    messages: list,
    **kwargs
) -> str:
    """
    Creates a completion for the specified language model.
    """
    client_type = llm_metadata.client_type
    if client_type == LLMClientTypes.GOOGLE:
        return google_completions_create


def create_chat_completion(
    llm_metadata: LLMMetadata,
    sys_instruct: str,
    messages: list,
    **kwargs
) -> str:
    """
    Creates a completion for the specified language model.
    """
    client_type = llm_metadata.client_type
    client = llm_metadata.client
    model = llm_metadata.model
    if client_type == LLMClientTypes.GROQ.value:
        return groq_chat_completions_create(client, messages, model, sys_instruct, **kwargs)
    elif client_type == LLMClientTypes.GOOGLE.value:
        return google_chat_completions_create(client, messages, model, sys_instruct, **kwargs)
    else:
        raise ValueError(f"Unsupported client type: {client_type}")

