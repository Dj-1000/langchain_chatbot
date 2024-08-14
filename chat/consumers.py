from channels.generic.websocket import AsyncWebsocketConsumer
import json, asyncio
from channels.db import database_sync_to_async
from .models import Room,Messages
from accounts.models import ChatUser
from django.db.models import Q
from .utils import get_user
from chat.openai import get_intent_scores,bot_conversation
import os
import django

django.setup()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chatbot.settings")

class ChatRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        print("In connect :",self.room_name,self.room_group_name)
        self.user = self.scope['user']
        self.room = await database_sync_to_async(Room.objects.get)(id=self.room_name)

        if not self.user.is_authenticated:
            print("User is anonymous")
            return await self.close()
        
        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()




    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get("message","")
    
        message = str(message).strip()

        if message:
            await database_sync_to_async(Messages.objects.create)(
                room = self.room,
                content = message,
                sent_by = self.user,
                is_bot = False
            )

        # Send message to room group
        print("Sending messages to textbox: ", message)
        user = await get_user(email = self.user.email)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "message": message,
                "is_bot": False,
                "sent_by" : self.user.email
            }
        )

    async def chat_message(self, event):
        msg = event["message"]
        print("Chat message called")
        if msg:
            await self.send(text_data=json.dumps({
                "message" : msg,
                "is_bot" : False,
                "sent_by" : self.user.first_name
            }))

        if self.user.email == event['sent_by']:
            intent_score = await bot_conversation(user_query=msg,room_name=self.room_name)
            bot = await get_user()

            print("Response from chatbot :",intent_score)
            # Send message to WebSocket
            
            host_url = self.get_host_address()
            if isinstance(intent_score,dict):
                if intent_score.get("file_url"):
                    file_object = host_url + intent_score.get("file_url")
                else:
                    file_object = None
                file_name = intent_score.get("file_name")
                intent_score = intent_score.get('message')
            else:
                file_object = None
                file_name = None
        
            await database_sync_to_async(Messages.objects.create)(
                    room = self.room,
                    content = intent_score,
                    sent_by = bot,
                    is_bot = True,
                    file_object = file_object,
                    file_name = file_name
            )

            await self.channel_layer.group_send(
                self.room_group_name,
                 {
                    "type": "bot.message",
                    "message": intent_score,
                    "sent_by": "bot@procare.com",
                    "is_bot": True,
                    "file_name": file_name,
                    "file_object": file_object,
                }
            )

    async def bot_message(self, event):
        msg = event["message"]

        print("Chat bot message called", msg)
        if msg:
            await self.send(text_data=json.dumps(
                {
                    "type": "chat.message",
                    "message": event['message'],
                    "file_object": event['file_object'],
                    "sent_by": event["sent_by"],
                    "is_bot": True,
                    "file_name": event['file_name']
                }
            ))
        else:
            return None
        
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    def get_host_address(self):
        for header in self.scope['headers']:
            if header[0] == b'origin':
                return header[1].decode('utf-8')
        return None


