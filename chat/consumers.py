from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from .models import Room,Messages
from django.db.models import Q

from .openai import get_intent_scores
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
        # self.other_user = await self.get_other_user(room=self.room)

        # if self.other_user:
        #     print(f"User 1 :{self.user} Other User : {self.other_user}")

        if not self.user.is_authenticated:
            print("User is anonymous")
            return await self.close()
        
        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get("message","")
    
        message = str(message).strip()

        if message:
            await database_sync_to_async(Messages.objects.create)(
                room = self.room,
                content = message,
                sent_by = self.user
            )
        # Send message to room group
        print("Sending messages to textbox: ",message)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "is_bot": False
            })
    

    # Receive message from room group
    async def chat_message(self, event):
        msg = event["message"]
        print("Recieved input message :",msg)
        host_url = self.scope['headers'][0][1].decode()
    
        if msg:
            await self.send(text_data=json.dumps({
                "message": msg,
                "is_bot": False
            }))

            intent_score = await get_intent_scores(msg,room_name=self.room_name, host_url=host_url)

            
            print("Response from chatbot :",intent_score)
            
        # Send message to WebSocket
        if isinstance(intent_score, dict):
            file_object = intent_score.get("file_url")
            intent_score = intent_score.get('message')
        else:
            file_object = None

        await self.send(text_data=json.dumps({
            "message": intent_score,
            "file_object": file_object,
            "is_bot":True
        }))



    # @database_sync_to_async
    # def get_other_user(self,room):
    #     return list(room.member.all().exclude(id = self.user.id))[0]
        