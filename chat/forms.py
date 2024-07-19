from django.forms import ModelForm
from .models import File,Folder,Room


class FileForm(ModelForm):
    class Meta:
        model = File
        fields = ['name','file','folder']


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = ['name']

