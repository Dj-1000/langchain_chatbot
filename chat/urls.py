from django.urls import path
from .views import index,chat_view,upload_file,file_list,create_room
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',index,name='index'),
    path('file-list/',file_list,name='file-list'),
    path('create-room/',create_room,name='create_room'),
    path('chat/<uuid:room_id>/',chat_view,name = 'chat_view'),
    path('upload/', upload_file, name='upload_file'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
