from jinja2 import Template
from .models import Folder, File, Room, Messages, ChatMessage
from django.db.models import Q
from accounts.models import ChatUser
from asgiref.sync import sync_to_async
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from .prompts import BOT_PROMPT
import json
import asyncio

@sync_to_async
def get_folder_objects(id=None):
    folders_with_files = Folder.objects.prefetch_related('files').all()
    if id is not None:
        obj = Folder.objects.filter(id=id).first()
        return obj
    return list(Folder.objects.all())

@sync_to_async
def get_folder_files(folder_id):
    if folder_id:
        files = File.objects.filter(folder_id = folder_id).all()
        return files

@sync_to_async
def room_session_update(room_name,category=None,is_matched=False):
    room_name = str(room_name)

    ##first you have to get a room with an id to update and for that you must save id somewhere 
    session = Room.objects.filter(id = room_name).first()

    if is_matched and session:
        session.category = Folder.objects.filter(id=category).first()
        session.is_matched=True
    else:
       session.is_matched = False
       session.category = None

    session.save()
    return


@sync_to_async
def check_session(room_name = None):
    room = Room.objects.filter(id = room_name).first()
    if room:
        return room.is_matched
    

@sync_to_async
def get_current_room(room_name):
    room = Room.objects.filter(id = room_name).first()
    return room


@sync_to_async
def get_file_objects(id):
    obj = File.objects.filter(id=id).first()
    if obj:
        return obj
    return None

@sync_to_async
def get_user(email=None):
    if not email:
        bot = ChatUser.objects.filter(email = 'bot@procare.com').first()
        if not bot:
            bot = ChatUser.objects.create(
                email = 'bot@procare.com',
                first_name = 'Bot',
                last_name = 'Procare',
                password = 'bot123'
            )
        return bot 
    user = ChatUser.objects.filter(email = email).first()
    return user

@sync_to_async
def get_db_data():
    data = []
    folders = Folder.objects.all()
    for folder_index, folder in enumerate(folders):
        folder_data = {
            'folder_id': folder.id,
            'folder_name': folder.name,
            'description': folder.description,
            'parent': folder.parent.name if folder.parent else None,
            'files': []
        }
        
        files = File.objects.filter(folder=folder)
        for file_index, file in enumerate(files):
            folder_data['files'].append({
                'file_id': file.id,
                'file_name': file.name,
                'description': file.description,
                'file_url': file.file.url,
            })
        
        data.append(folder_data)
        
    return data

def message_to_dict(message):
    return {
        'type': message.__class__.__name__,
        'content': message.content,
        'additional_kwargs': message.additional_kwargs
    }


def dict_to_message(message_dict):
    message_type = message_dict['type']
    content = message_dict['content']
    additional_fields = message_dict['additional_kwargs']
    if message_type == 'HumanMessage':
        return HumanMessage(content=content, additional_fields=additional_fields)
    elif message_type == 'AIMessage':
        return AIMessage(content=content, additional_fields=additional_fields)
    elif message_type == 'SystemMessage':
        return SystemMessage(content=content, additional_fields=additional_fields)
    else:
        raise ValueError(f"Unknown message type: {message_type}")
    

def save_memory(memory_key, memory_buffer):
    messages = [message_to_dict(msg) for msg in memory_buffer.chat_memory.messages]
    with open(f"buffer/{memory_key}_memory.json", "w") as f:
        json.dump(messages, f)

def fetch_data_from_db():
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(get_db_data())

def load_memory(memory_key):
    memory = ConversationBufferMemory(memory_key=memory_key, input_key='user_query')
    try:
        with open(f"buffer/{memory_key}_memory.json", "r") as f:
            buffer = json.load(f)
            for message_dict in buffer:
                message = dict_to_message(message_dict)
                memory.chat_memory.add_message(message)
    except FileNotFoundError:
        pass
    return memory


async def get_render_txt():
    data = await get_db_data()
    template = Template(BOT_PROMPT)
    render_txt = template.render(data = data)
    return render_txt


@sync_to_async
def get_message_history(room_name):
    history = ChatMessage.objects.filter(room__id = room_name).first()
    return history

@sync_to_async

def save_chat_messages(chat_messages,room_name):
    room = Room.objects.filter(id = room_name).first()
    for message in chat_messages:
        if isinstance(message, HumanMessage):
            ChatMessage.objects.create(
                room = room,
                message_type='human',
                content=message.content,
            )
        elif isinstance(message, AIMessage):
            ChatMessage.objects.create(
                room = room,
                message_type='ai',
                content=message.content
            )

@sync_to_async
def load_chat_messages(room_name):
    history = ChatMessageHistory()
    chat_messages = ChatMessage.objects.filter(room__id = room_name).all().order_by('-created_at')[:10]
    for chat_message in chat_messages:
        if chat_message.message_type == 'human':
            history.add_user_message(HumanMessage(content=chat_message.content))
        elif chat_message.message_type == 'ai':
            content_dict = {'content': chat_message.content}
            history.add_ai_message(AIMessage(content=json.dumps(content_dict)))
    return history