from django.shortcuts import render,redirect
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .models import Room
from django.db.models import Q
from .models import File,Folder,Messages, ChatMessage
from .forms import FileForm,RoomForm
from django.contrib.auth.decorators import login_required


User = get_user_model()


def index(request):
    return render(request,'index.html')


@login_required
def create_room(request):
    form = RoomForm(data=request.POST)
    if request.method=='POST':
        try:
            if form.is_valid():
                name = request.POST.get('name')
                user = request.user
                room = Room()
                room.name = name
                room.owner = user
                room.save() ## to add member
                room.member.add(user)
                room.save()
                return redirect(reverse('chat_view', kwargs={'room_id': room.id}))
        except Exception as e:    
            alert = e
            return render(request,'create_room.html',{'alert':alert})

    return render(request,'create_room.html',{'form':form})


@login_required
def join_room(request):
    if request.method == 'POST':
        user = request.user
        room_id = request.POST.get('room_id')
        room = Room.objects.filter(id = room_id).first()
        if room:
            room.join(user)
            return redirect(reverse('chat_view', kwargs={'room_id': room_id}))

    return render(request, "join_room.html")


@login_required
def chat_view(request,room_id):
    room = Room.objects.filter(id = room_id).first()
    prev_messages = Messages.objects.filter(room__id = room_id)

    context = {
        'room_id': room_id,
        'prev_messages' : prev_messages,
        'room_name': room.name
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