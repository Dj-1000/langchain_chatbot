from django.forms import ModelForm
from .models import File,Folder,Room
from django import forms

class FileForm(ModelForm):
    class Meta:
        model = File
        fields = ['name','file','folder']


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = ['name']
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Room.objects.filter(name=name).exists():
            raise forms.ValidationError('Room with this name already exists.')
        return name

