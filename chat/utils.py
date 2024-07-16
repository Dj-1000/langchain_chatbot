from .models import Folder, File, Room
from asgiref.sync import sync_to_async
import json

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
    return obj

