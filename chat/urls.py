from django.urls import path
from .views import index,chat_view,upload_file,file_list,create_room, join_room
from accounts.views import dashboard

urlpatterns = [
    path('',dashboard,name='dashboard'),
    path('file-list/',file_list,name='file-list'),
    path('create-room/',create_room,name='create_room'),
    path('join-room/',join_room,name='join_room'),
    path('chat/<uuid:room_id>/',chat_view,name = 'chat_view'),
    path('upload/', upload_file, name='upload_file'),
] 
