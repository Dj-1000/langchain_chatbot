from chat.prompts import GET_FOLDER_INTENT_PROMPT_, GET_FILE_INTENT_PROMPT,BOT_PROMPT
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.chains.openai_functions.qa_with_structure import create_qa_with_structure_chain
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import ChatMessageHistory
from .schema import BotOuput 
from jinja2 import Template
from django.db.models import Q
from chat.models import Folder,Room

import json
from .utils import *

parser = StrOutputParser()
model = ChatOpenAI(model="gpt-4")

async def call_model(input,room_name):
    '''Function to call gpt model'''

    db_data = await get_db_data()
    history = await get_message_history(room_name)
    chat_history = ChatMessageHistory()
    prompt_template = ChatPromptTemplate.from_messages([
            (
                "system",
                f"{BOT_PROMPT}",
            ),
            MessagesPlaceholder(variable_name='messages'),
        ])
    
    qa_chain = create_qa_with_structure_chain(
        llm=model,
        prompt=prompt_template,
        schema=BotOuput,
    )
    
    if history is not None:
        chat_history = await load_chat_messages(room_name=room_name)

    chat_history.add_user_message(input)
    response = await qa_chain.ainvoke(input = {"messages" : list(chat_history.messages),"data" : db_data})
    result = json.loads(response.get('text'))
    chat_history.add_ai_message(result.get('message'))

    await save_chat_messages(chat_history.messages, room_name)
    return result
    

async def get_intent_scores(user_query,room_name):
    '''Function to start conversation'''
    category_set = await check_session(room_name)
    if category_set:
        return await bot_conversation(user_query,room_name=room_name)
    
    django_objects = await get_folder_objects()
    prompt =  GET_FOLDER_INTENT_PROMPT_
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system",prompt),
            ("user","{user_query}")
        ]
    )
    result = await call_model(prompt_template=prompt_template,django_objects=django_objects, user_query=user_query,room_name=room_name)
    if result['is_match']:
        await room_session_update(room_name = room_name,category=result['category'],is_matched=True)
        return result['message']
    
    return result['message']


async def bot_conversation(user_query,room_name):
    '''Function to get conversation ongoing.'''

    room = await get_current_room(room_name)
    folder_id = room.category_id

    result = await call_model(input=user_query,room_name=room_name)

    if result['is_match']:
        if result['file_name']:
            id = result['category']
            file = await get_file_objects(id)
            
            result['file_url'] = file.file.url if file else None
            return result
        else:
            await room_session_update(room_name = room_name,category=result['category'],is_matched=True)
            return result['message']
    else:
        await room_session_update(room_name = room_name,is_matched=False)

        return result




    
