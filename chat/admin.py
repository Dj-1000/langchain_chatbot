from django.contrib import admin
from .models import *

admin.site.register(Room)


class FileAdmin(admin.ModelAdmin):  # Display the name and parent in the list view
    ordering = ['folder','name'] 

class FolderAdmin(admin.ModelAdmin):  # Display the name and parent in the list view
    ordering = ['parent','name'] 

class MessageAdmin(admin.ModelAdmin):
    list_display = ('room', 'content', 'is_bot', 'sent_by', 'created_at')


admin.site.register(Folder,FolderAdmin)
admin.site.register(File,FileAdmin)
admin.site.register(Messages,MessageAdmin)
admin.site.register(ChatMessage)