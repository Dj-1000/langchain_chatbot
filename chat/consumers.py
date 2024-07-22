from channels.generic.websocket import AsyncWebsocketConsumer
import json, asyncio
from channels.db import database_sync_to_async
from .models import Room,Messages
from accounts.models import ChatUser
from django.db.models import Q
from .utils import get_bot_user
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
                sent_by = self.user,
                is_bot = False
            )
        # Send message to room group
        print("Sending messages to textbox: ",message)

        # asyncio.run_in_executor()
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "message": message,
                "is_bot": False,
                "sent_by" : self.user.email
            }
        )
        

        intent_score = await bot_conversation(user_query=message,room_name=self.room_name)
        bot = await get_bot_user()
 
        print("Response from chatbot :",intent_score)

        # Send message to WebSocket
        if isinstance(intent_score, dict):
            file_object = intent_score.get("file_url")
            file_name = intent_score.get("file_name")
            intent_score = intent_score.get('message')
        else:
            file_object = None
            file_name = None

        await database_sync_to_async(Messages.objects.create)(
                room = self.room,
                content = intent_score,
                sent_by = bot,
                is_bot = True
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type" : "chat.message",
                "message": intent_score,
                "file_object": file_object,
                "is_bot":True,
                "file_name": file_name
            }
        )


    async def chat_message(self, event):

        msg = event["message"]
        print("",msg)
        if msg:
            await self.send(text_data=json.dumps(event))


        # host_url = self.scope['headers'][0][1].decode()
        # intent_score = await bot_conversation(user_query=msg,room_name=self.room_name)
        # bot = await get_bot_user()
        
                
        # print("Response from chatbot :",intent_score)

        # # Send message to WebSocket
        # if isinstance(intent_score, dict):
        #     file_object = intent_score.get("file_url")
        #     file_name = intent_score.get("file_name")
        #     intent_score = intent_score.get('message')
        # else:
        #     file_object = None
        #     file_name = None

        # await database_sync_to_async(Messages.objects.create)(
        #         room = self.room,
        #         content = intent_score,
        #         sent_by = bot,
        #         is_bot = True
        # )

        # await self.send(text_data=json.dumps({
        #     "message": intent_score,
        #     "file_object": file_object,
        #     "is_bot":True,
        #     "file_name": file_name
        # }))






        