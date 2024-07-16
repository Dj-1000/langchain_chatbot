from .prompts import GET_FOLDER_INTENT_PROMPT, GET_FILE_INTENT_PROMPT
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)
from langchain.memory import ConversationBufferMemory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.chains.openai_functions.qa_with_structure import create_qa_with_structure_chain
from langchain_core.pydantic_v1 import BaseModel, Field
# from langchain.memory import InMemoryVariableManager
from langchain_core.output_parsers import StrOutputParser

import random
from django.db.models import Q
import uuid
import json
import concurrent.futures
from .utils import *

parser = StrOutputParser()
model = ChatOpenAI(model="gpt-4")

from chat.models import Folder


class IntentScoreOutput(BaseModel):
    """description"""
    is_match: bool = Field(..., description="Boolean, set to True if the highest intent score is more than 0.5.")
    message: str = Field(..., description="A message asking for more details if 'is_match' is False.")
    category: int = Field(..., description="The id of the folder with the highest intent score.")
    intent_score : int = Field(..., description="The intent score of the folder with the highest intent score.")
class FileIntentScoreOutput(BaseModel):
    """dis"""
    is_match: bool = Field(..., description="Boolean, set to True if any file intent score is more than 0.7.")
    message: str = Field(..., description="A message asking for more details if 'is_match' is False or requesting confirmation if 'is_match' is True.")
    file_name: str = Field(..., description="The name of the file with the highest intent score, or null if no match.")
    file_id: int = Field(..., description="The ID of the file with the highest intent score, or null if no match")
    category: int = Field(..., description="The category of the parent folder, or null if no match.")


store={}
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

def message_to_dict(message):
    return {
        'type': message.__class__.__name__,
        'content': message.content,
        'additional_kwargs': message.additional_kwargs
    }


from langchain.schema import HumanMessage, AIMessage

def dict_to_message(message_dict):
    message_type = message_dict['type']
    content = message_dict['content']
    additional_fields = message_dict['additional_kwargs']
    if message_type == 'HumanMessage':
        return HumanMessage(content=content, additional_fields=additional_fields)
    elif message_type == 'AIMessage':
        return AIMessage(content=content, additional_fields=additional_fields)
    else:
        raise ValueError(f"Unknown message type: {message_type}")

def save_memory(memory_key, memory_buffer):
    messages = [message_to_dict(msg) for msg in memory_buffer.chat_memory.messages]
    with open(f"{memory_key}_memory.json", "w") as f:
        json.dump(messages, f)

def load_memory(memory_key):
    memory = ConversationBufferMemory(memory_key=memory_key, input_key='user_query')
    try:
        with open(f"{memory_key}_memory.json", "r") as f:
            buffer = json.load(f)
            for message_dict in buffer:
                message = dict_to_message(message_dict)
                memory.chat_memory.add_message(message)
    except FileNotFoundError:
        pass
    return memory

def call_model(prompt_template,django_objects,user_query,room_name,schema=IntentScoreOutput):
    # Create the chain with structured output
    # chain = prompt_template | model | parser

    chain = create_qa_with_structure_chain(
        llm=model,
        prompt=prompt_template,
        schema=schema
    )
    room_name = str(room_name)
    chain.memory = load_memory(room_name)
    # chain.memory = ConversationBufferMemory(memory_key=str(room_name),input_key='user_query')
    # config = {"configurable": {"session_id": f"{room_name}"}}
    # with_message_history = RunnableWithMessageHistory(
    #                         chain,
    #                         get_session_history(session_id=str(room_name))
    #                     )
    print(chain.memory)
    if schema==IntentScoreOutput:
        result = chain.invoke({"django_objects": django_objects, "user_query": user_query})
    else:
        result = chain.invoke({"file_objects": django_objects, "user_query": user_query})

    # chain.memory.save_context({"user_query": user_query}, result)

    result = json.loads(result.get('text'))
    save_memory(room_name, chain.memory)

    # Handle the structured output
    return result
    



async def get_intent_scores(user_query,room_name, host_url):

    category_set = await check_session(room_name)

    if category_set:
        return await bot_conversation(user_query,room_name=room_name, host_url=host_url)

    django_objects = await get_folder_objects()

    # print(django_objects)
    prompt =  GET_FOLDER_INTENT_PROMPT
     
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system",prompt),
            ("user","{user_query}")
        ]
    )
    prompt_template.input_variables
    # chain = prompt_template | model | parser
   
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit the function to the executor
        future = executor.submit(call_model,prompt_template=prompt_template,django_objects=django_objects, user_query=user_query,room_name=room_name)
        
        # Fetch the result from the future
        result = future.result()

    if result['is_match']:
        await room_session_update(room_name = room_name,category=result['category'],is_matched=True)
        return result['message']
    return result['message']




async def bot_conversation(user_query,room_name, host_url):
    room = await get_current_room(room_name)

    folder_id = room.category_id
    # folder = await get_folder_objects(id = folder_id)
    django_objects = await get_folder_files(folder_id)
    prompt = GET_FILE_INTENT_PROMPT
    # Define the prompt template
    prompt_template = ChatPromptTemplate.from_messages(
        [ ("system", GET_FILE_INTENT_PROMPT), 
        ("user", "{user_query}")]
    )

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit the function to the executor
        future = executor.submit(call_model,prompt_template, django_objects, user_query,room_name,schema = FileIntentScoreOutput)
        
        # Fetch the result from the future
        result = future.result()

    if result['is_match']:
        id = result['file_id']
        file = await get_file_objects(id)
        # message  = result['message']
        result['file_url'] = file.file.url if file else None
        return result
    else:
        await room_session_update(room_name = room_name,is_matched=False,)
        return result


    

    