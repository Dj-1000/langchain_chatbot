from django.forms import ModelForm
from .models import File,Folder


class FileForm(ModelForm):
    class Meta:
        model = File
        fields = ['name','file','folder']