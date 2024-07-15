from django.urls import path
from .views import index,chat_view,room,upload_file,file_list
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',index,name='index'),
    path('file-list/',file_list,name='file-list'),
    path('<int:other_user_id>/',room,name='chatroom'),
    path('chat/<uuid:room_id>/',chat_view,name = 'chat_view'),
    path('upload/', upload_file, name='upload_file'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
