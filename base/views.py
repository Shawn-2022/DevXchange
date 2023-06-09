from django.shortcuts import render ,redirect
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .models import Room,Topic,Message,User
from .forms import RoomForm,UserForm,MyUserRegistrationForm

def login_register_Page(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request,'User does not exist !')
            
        user = authenticate(request,email=email,password=password)
        
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,"username OR password does not exist")
    context ={'page':page}
    return render (request,'base/login_register.html',context) 
   
def logoutUser(request):
    logout(request)
    return redirect('home')

def registerUser(request):
    form = MyUserRegistrationForm()
    
    if request.method == 'POST':
        form = MyUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower() # use lower() to convert to lowercase
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Registration Failed!!!')
            
    return render(request, 'base/login_register.html', {'form':form})


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q) 
        # Q(host__icontains=q)
        
        )
    Topics =Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {'rooms':rooms,'Topics':Topics,'room_count':room_count,'room_messages':room_messages}
    return render (request, 'base/home.html',context)


def room(request,id):
    room = Room.objects.get(id=id)
    room_messages = room.message_set.all()
    participants = room.participants.all()
    if request.method =='POST':
        message = Message.objects.create(
            user = request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room',id=room.id)
    
    context = {'room':room,'room_messages':room_messages,'participants':participants}
    return render (request, 'base/room.html',context)

def userProfile(request,id):
    user = User.objects.get(id=id)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    Topics = Topic.objects.all()
    context ={'user':user,'rooms':rooms,'room_messages':room_messages,'Topics':Topics}
    return render(request,'base/profile.html',context)

@login_required(login_url='/login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic,created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            )
        return redirect('home')
    
    context = {'form':form,'topics':topics}
    return render (request,'base/room_form.html',context)

@login_required(login_url='/login')
def updateRoom(request,id):
    room = Room.objects.get(id=id)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse("You can't make changes here !")
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic,created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
    context ={'form':form,'topics':topics,'room':room}
    return render(request,'base/room_form.html',context)

@login_required(login_url='/login')
def updateMessage(request,id):
    message = Message.objects.get(id=id)
    if request.user != message.user:
        return HttpResponse("You can't make changes here !")
    if request.method == 'POST':
        message.body = request.POST['body']
        message.save()
        return redirect ('home')
    return render(request, 'base/update_message.html', {'message': message})

@login_required(login_url='/login')
def deleteRoom(request,id):
    room = Room.objects.get(id=id)
    if request.user != room.host:
        return HttpResponse("You can't delete this room!")
    if request.method == 'POST':
        room.delete()
        return redirect ('home')
    return render(request,'base/delete.html',{'obj':room})

@login_required(login_url='/login')
def deleteMessage(request,id):
    message =Message.objects.get(id=id)
    if request.user != message.user:
        return HttpResponse("You can't delete this message!")
    if request.method == 'POST':
        message.delete()
        return redirect ('home')
    return render(request,'base/delete.html',{'obj':message})

@login_required(login_url='/login')
def updateUser(request):
    user =request.user
    form = UserForm(instance=user)
    
    if request.method == 'POST':
        form = UserForm(request.POST,request.FILES,instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile',id=user.id)
    return render(request,'base/update-user.html',{'form':form})

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    
    topics =Topic.objects.filter(name__icontains=q)
    return render(request,'base/topics.html',{'topics':topics})

def activityPage(request):
    
    room_messages = Message.objects.all()
    return render(request,'base/activity.html',{'room_messages':room_messages})