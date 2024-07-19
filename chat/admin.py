from django.contrib import admin
from .models import *

admin.site.register(Room)


class FileAdmin(admin.ModelAdmin):  # Display the name and parent in the list view
    ordering = ['folder','name'] 
admin.site.register(File,FileAdmin)

class FolderAdmin(admin.ModelAdmin):  # Display the name and parent in the list view
    ordering = ['parent','name'] 

admin.site.register(Folder,FolderAdmin)