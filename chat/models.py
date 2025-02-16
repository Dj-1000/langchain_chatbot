from django.db import models
from django.contrib.auth import get_user_model
import uuid
import django

User = get_user_model()


class Folder(models.Model):
    name = models.CharField(max_length=2000)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subfolders')
    description = models.CharField(max_length=2000,blank=True)

    def __str__(self) -> str:
        if self.parent:
            return self.name + ' / ' + self.parent.name
        else:
            return self.name
        

class Room(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    name = models.CharField(max_length=2000,default=None)
    member = models.ManyToManyField(User, related_name="rooms")
    category = models.ForeignKey(to=Folder, on_delete=models.CASCADE, related_name='sessions', null=True, default=None)
    is_matched = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True,null = True)
    owner = models.ForeignKey(User, related_name='owner_of',on_delete=models.CASCADE,null = True,default = None)
    
    def __str__(self) -> str:
        return str(self.id)

    def get_online_count(self):
        return self.member.count()


    def join(self, user):
        self.member.add(user)
        self.save()

    def leave(self, user):
        self.member.remove(user)
        self.save()


class Messages(models.Model):
    room = models.ForeignKey(Room, related_name='messages',on_delete=models.CASCADE,null=True)
    content = models.TextField()
    is_bot = models.BooleanField(default=False)
    sent_by = models.ForeignKey(User, related_name="messages_sent", on_delete=models.DO_NOTHING)
    file_object = models.URLField(default = None, null=True)
    file_name = models.CharField(max_length=200,default = None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'messages'
    def __str__(self) -> str:
        return self.content


class File(models.Model):
    name = models.CharField(max_length=2000)
    description = models.CharField(max_length=2000,blank=True)
    folder = models.ForeignKey(Folder, related_name='files', on_delete=models.CASCADE,null=True,blank=True)
    file = models.FileField(upload_to='uploads/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.folder:
            return self.name + ' / ' + self.folder.name
        else:
            return self.name
        

class ChatMessage(models.Model):
    MESSAGE_TYPE_CHOICES = (
        ('human', 'Human'),
        ('ai', 'AI'),
    )
    room = models.ForeignKey(Room, related_name='chat_messages',on_delete=models.CASCADE,null=True)
    message_type = models.CharField(max_length=5, choices=MESSAGE_TYPE_CHOICES,default = MESSAGE_TYPE_CHOICES[0])
    content = models.TextField(default = None)
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.content}"
    