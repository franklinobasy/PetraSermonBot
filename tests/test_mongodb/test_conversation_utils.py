import pytest
from database.mongodb.utils import *
from tests.test_mongodb.test_user_utils import sample_user


user_data = {"email": "testuser@example.com", "first_name": "Test", "last_name": "User", "picture": "test_url"}
sample_user = create_user(User(**user_data))
sample_conversation_id = create_conversation(sample_user.user_id)


def test_create_conversation():
    conversation_id = create_conversation(sample_user.user_id)
    assert conversation_id is not None


def test_delete_conversation():
    result = delete_conversation(sample_user.user_id, sample_conversation_id)
    assert result is True


def test_add_prompt_to_conversation():
    prompt_data = {"question": "What is your name?", "answer": "My name is Test."}
    prompt = PromptModel(**prompt_data)
    
    result = add_prompt_to_conversation(sample_user.user_id, sample_conversation_id, prompt)
    assert result is True


def test_get_user_conversations():
    conversations = get_user_conversations(sample_user.user_id)
    assert len(conversations) > 0


def test_get_prompts_from_conversation_model():
    prompts = get_prompts_from_conversation(sample_user.user_id, sample_conversation_id, use_model=True)
    assert len(prompts) > 0
    # assert isinstance(prompts[0],)


def test_get_prompts_from_conversation_processed():
    prompts = get_prompts_from_conversation(sample_user.user_id, sample_conversation_id, use_model=False)
    assert len(prompts) > 0
    # assert isinstance(prompts[0], PromptModel)
