from django.shortcuts import render,redirect
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .models import Room
from django.db.models import Q
from .models import Messages,File,Folder
from .forms import FileForm


User = get_user_model()


def index(request):
    return render(request,'index.html')


@login_required
def room(request,other_user_id):
    user_id = request.user.id
    other_user_id = other_user_id

    user = User.objects.filter(id = user_id).first()
    other_user = User.objects.filter(id = other_user_id).first()

    if user and other_user:
        rooms_with_user = Room.objects.filter(member=user).filter(member=other_user).first()
        if rooms_with_user:
            return redirect(reverse('chat_view',kwargs={"room_id" : rooms_with_user.id}))
            
         
        else:
            room = Room()
            room.save()
            room.member.add(user,other_user)
            return redirect(reverse('chat_view',kwargs={"room_id" : room.id}))

def chat_view(request,room_id):
    prev_messages = Messages.objects.filter(room__id = room_id).order_by('-created_at')
    context = {
        'room_id': room_id,
        'prev_messages' : prev_messages
    }
    return render(request,'chatbot.html',context=context)



def file_list(request):
    files = File.objects.all()
    return render(request, 'file_list.html', {'files': files})

def upload_file(request):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():

            form.save()
            alert = "File uploaded successfully"
            return render(request, 'upload_file.html', {'alert': alert})
        else:
            alert = "Error uploading file"
            return render(request, 'upload_file.html', {'alert': alert})  # Redirect to a success page or another view
    else:
        form = FileForm()
    return render(request, 'upload_file.html', {'form': form})
    

