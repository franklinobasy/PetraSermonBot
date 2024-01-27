# tools
from database.mongodb import (
    users_conversations_collections as conv_collection,
    users_collection,
)
from database.mongodb.models import (
    PromptModel,
    ConversationModel,
    UserConversionModel
)

from datetime import datetime
from typing import List, Tuple


def create_conversation(user_id: str) -> str:
    existing_user = users_collection.find_one({"user_id": user_id})
    
    if not existing_user:
        raise Exception(f"User with user_id: {user_id} not found")

    conversation_data = ConversationModel()
    
    user_conversation_data = conv_collection.find_one({"user_id": user_id})
    if user_conversation_data:
        conv_collection.update_one(
            {"user_id": user_id},
            {"$push": {"conversations": conversation_data.dict()}}
        )
    else:
        user_conversation_data = UserConversionModel(
            user_id=user_id,
            conversations=[conversation_data]
        )
        
        conv_collection.insert_one(user_conversation_data.dict())
    
    return conversation_data.conversation_id

def delete_conversation(
    user_id: str,
    conversation_id: str,
) -> bool:
    existing_user = users_collection.find_one({"user_id": user_id})
    
    if not existing_user:
        raise Exception(f"User with user_id: {user_id} not found")
    
    result = conv_collection.update_one(
        {"user_id": user_id},
        {"$pull": {"conversations": {"conversation_id": conversation_id}}}
    )
    if result.modified_count > 0:
        return True
    else:
        return False


def add_prompt_to_conversation(
    user_id: str,
    conversation_id: str,
    prompt: PromptModel,
) -> bool:
    
    current_time = datetime.utcnow()

    existing_user = users_collection.find_one({"user_id": user_id})
    if not existing_user:
        raise Exception(f"User with user_id: {user_id} not found")

    # Check if the conversation exists for the user
    conversation_exists = conv_collection.find_one({"user_id": user_id, "conversations.conversation_id": conversation_id})
    if not conversation_exists:
        # Add the conversation for the user
        conversation = ConversationModel(
            conversation_name=prompt.dict().get("question"),
            prompts=[prompt.dict()]
        )
        conv_collection.update_one(
            {"user_id": user_id},
            {"$push": {"conversations": conversation.dict()}}
        )
        return True
    else:
        # Update conversation_name based on the new prompt's question
        new_conversation_name = prompt.dict().get("question")
        
        user_converstions = conv_collection.find_one({"user_id": user_id})['conversations']
        for conv in user_converstions:
            if conv['conversation_id'] == conversation_id:
                conv_collection.update_one(
                    {"user_id": user_id, "conversations.conversation_id": conversation_id},
                    {
                        "$set": {
                            "conversations.$.conversation_name": new_conversation_name if conv['conversation_name'] == "New conversation" else "New conversation",
                            "conversations.$.date_modified": current_time
                        },
                        "$push": {
                            "conversations.$.prompts": prompt.dict()
                        }
                    }
                )
                return True

    return False


def get_user_conversations(
    user_id: str,
) -> List[ConversationModel]:
    
    existing_user = users_collection.find_one({"user_id": user_id})
    if not existing_user:
        raise Exception(f"User with user_id: {user_id} not found")
    
    user_conversations = conv_collection.find_one({"user_id": user_id})
    conversations = user_conversations.get("conversations", [])
    return [ConversationModel(**conv) for conv in conversations]
    


def process_prompt(prompt: PromptModel) -> tuple:
    '''process prompt to readable format'''
    prompt = prompt.dict()
    return (prompt["question"], prompt["answer"])


def get_prompts_from_conversation(
    user_id: str,
    conversation_id: str,
    use_model: bool = True,
) -> List[PromptModel] | List[Tuple]:
    
    conversations = get_user_conversations(user_id)
    if conversations:
        for target_conversation in conversations:
            if target_conversation.conversation_id == conversation_id:
                prompts = target_conversation.prompts
                if use_model:
                    return [PromptModel(**prompt.dict()) for prompt in prompts]
                return [process_prompt(PromptModel(**prompt.dict())) for prompt in prompts]
            
    return conversations
