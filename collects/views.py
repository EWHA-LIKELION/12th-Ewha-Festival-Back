from django.shortcuts import render,redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from rest_framework import views
from rest_framework.status import *
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from accounts.models import User
from booths.models import Booth, Day, Menu, Event, EventDay
from django.utils import timezone
from manages.storages import FileUpload, s3_client
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import check_password
from django.contrib import messages, auth
from PIL import Image as pil
import os

def rescale(image, width):
    # 이미지 크기 조절
    img = pil.open(image)
    src_width, src_height = img.size
    src_ratio = float(src_height) / float(src_width)
    dst_height = round(src_ratio * width)

    size=width, dst_height
    img.thumbnail(size, pil.LANCZOS)
    img = img.convert("RGB")
    filename=str(image)
    resultPath="./collects/tempfiles"
    temp_file_path=os.path.join(resultPath, filename)
    img.save(temp_file_path)

    size_kb = os.path.getsize(temp_file_path) / 1024
    print(size_kb)
    while os.path.getsize(temp_file_path) / 1024 > 500:
        width/=2
        dst_height/=2
        size=width, dst_height
        img.thumbnail(size, pil.LANCZOS)
        img = img.convert("RGB")
        img.save(temp_file_path)
        size_kb = os.path.getsize(temp_file_path) / 1024
        print(size_kb)
    return temp_file_path,filename

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request=request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('collects:detail')
        else:
            messages.error(request, '아이디 또는 비밀번호가 올바르지 않습니다.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('collects:login')

def detail_view(request):
    booth=Booth.objects.get(user=request.user)
    menus=Menu.objects.filter(booth=booth.id)
    day1 = booth.days.filter(date=8).first()
    if day1 is None:
        day1=Day(date=None, start_time='', end_time='')
        day1.check=False
    else:
        day1.check=True
    day2 = booth.days.filter(date=9).first()
    if day2 is None:
        day2=Day(date=None, start_time='', end_time='')
        day2.check=False
    else:
        day2.check=True
    day3 = booth.days.filter(date=10).first()
    if day3 is None:
        day3=Day(date=None, start_time='', end_time='')
        day3.check=False
    else:
        day3.check=True
    form = PasswordChangeForm(request.user)
    return render(request, 'detail.html', {'booth': booth, 'day1': day1,'day2': day2,'day3': day3,'form':form,'menus':menus})

def update_view(request,booth_id):
    booth_update=Booth.objects.get(pk=booth_id)
    booth_update.name=request.POST['name']
    booth_update.category=request.POST['category']
    booth_update.updated_at=timezone.now()
    booth_update.description=request.POST['description']
    booth_update.contact=request.POST['contact']
    booth_update.realtime=request.POST['realtime']
    
    file = request.FILES.get('image')
    if file:
        temp_file_path,name = rescale(file,700)
        folder = f"{booth_id}_images"
        
        file_extension = name.split('.')[-1]
        file_url = FileUpload(s3_client).upload(open(temp_file_path, 'rb'), folder, "thumnail."+file_extension)
        booth_update.thumnail = file_url

        os.remove(temp_file_path)

    booth_update.save()

    if 'day1' in request.POST:
        try:
            day = Day.objects.get(booth=booth_id,date=8)
            if day:
                day.start_time=request.POST['start_time_8']
                day.end_time=request.POST['end_time_8']
                day.save()
        except Day.DoesNotExist:
            booth=Booth.objects.get(id=booth_id)
            day = Day(booth=booth,date=8,day="수요일", start_time=request.POST['start_time_8'], end_time=request.POST['end_time_8'])
            day.save()
    else:
        try:
            day = Day.objects.get(booth=booth_id, date=8)
            day.delete()
        except Day.DoesNotExist:
            pass

    if 'day2' in request.POST:
        try:
            day = Day.objects.get(booth=booth_id,date=9)
            if day:
                day.start_time=request.POST['start_time_9']
                day.end_time=request.POST['end_time_9']
                day.save()
        except Day.DoesNotExist:
            booth=Booth.objects.get(id=booth_id)
            day = Day(booth=booth,date=9,day="목요일", start_time=request.POST['start_time_9'], end_time=request.POST['end_time_9'])
            day.save()
    else:
        try:
            day = Day.objects.get(booth=booth_id, date=9)
            day.delete()
        except Day.DoesNotExist:
            pass

    if 'day3' in request.POST:
        try:
            day = Day.objects.get(booth=booth_id,date=10)
            if day:
                day.start_time=request.POST['start_time_10']
                day.end_time=request.POST['end_time_10']
                day.save()
        except Day.DoesNotExist:
            booth=Booth.objects.get(id=booth_id)
            day = Day(booth=booth,date=10,day="금요일", start_time=request.POST['start_time_10'], end_time=request.POST['end_time_10'])
            day.save()
    else:
        try:
            day = Day.objects.get(booth=booth_id, date=10)
            day.delete()
        except Day.DoesNotExist:
            pass
        
    messages.success(request, '수정이 완료되었습니다!')
    return redirect('collects:detail')


def password_change_view(request):
  if request.method == "POST":
    user = request.user
    origin_password = request.POST["current_password"]
    if check_password(origin_password, user.password):
      new_password = request.POST["new_password1"]
      confirm_password = request.POST["new_password2"]
      if new_password == confirm_password:
        user.set_password(new_password)
        user.save()
        auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, '비밀번호가 성공적으로 변경되었습니다.')
        return redirect('collects:detail')
      else:
        messages.error(request, '새로운 비밀번호와 확인용 비밀번호가 일치하지 않습니다.')
    else:
      messages.error(request, '현재 비밀번호가 올바르지 않습니다.')
    return redirect('collects:detail')
  else:
    return redirect('collects:detail')

def update_menu_view(request,menu_id):
    if request.method == "POST":
        menu_update = Menu.objects.get(id=menu_id)
        booth_id=menu_update.booth.id
        menu_update.menu = request.POST['menu']
        menu_update.price = request.POST['price']
        menu_update.vegan = request.POST['vegan']
        file = request.FILES.get('menuimg')
        if file:
            temp_file_path,name = rescale(file,700)
            folder = f"{booth_id}_images"
            file_extension = name.split('.')[-1]
            
            file_url = FileUpload(s3_client).upload(open(temp_file_path, 'rb'), folder, "menu"+str(menu_id)+"."+file_extension)
            menu_update.img = file_url

            os.remove(temp_file_path)


        menu_update.save()
        return redirect('collects:detail')
    

def delete_menu_view(request,menu_id):
    if request.method == "POST":
        menu_update = Menu.objects.get(pk=menu_id)
        menu_update.delete()
        return redirect('collects:detail')
    
def create_menu_view(request,booth_id):
    if request.method == "POST":
        booth=Booth.objects.get(pk=booth_id)
        menu = Menu(
            booth=booth,
            menu = request.POST['menu'],
            price = request.POST['price'],
            vegan = request.POST['vegan']
        )
        menu.save()
        file = request.FILES.get('menuimg')
        if file:
            temp_file_path,name = rescale(file,700)
            folder = f"{booth_id}_images"
            file_extension = name.split('.')[-1]
            
            file_url = FileUpload(s3_client).upload(open(temp_file_path, 'rb'), folder, "menu"+str(menu.id)+"."+file_extension)
            menu.img=file_url 

            os.remove(temp_file_path)
            menu.save()

        
        return redirect('collects:detail')
    
def event_list_view(request):
    events=Event.objects.all()
    return render(request, 'eventlist.html',{'events': events})

def event_detail_view(request,event_id):
    event=Event.objects.get(id=event_id)
    day1 = event.days.filter(date=8).first()
    if day1 is None:
        day1=Day(date=None, start_time='', end_time='')
        day1.check=False
    else:
        day1.check=True
    day2 = event.days.filter(date=9).first()
    if day2 is None:
        day2=Day(date=None, start_time='', end_time='')
        day2.check=False
    else:
        day2.check=True
    day3 = event.days.filter(date=10).first()
    if day3 is None:
        day3=Day(date=None, start_time='', end_time='')
        day3.check=False
    else:
        day3.check=True
    return render(request, 'eventdetail.html',{'event': event, 'day1': day1,'day2': day2,'day3': day3,})


def event_update_view(request,event_id):
    if request.method == "POST":
        event=Event.objects.get(pk=event_id)
        event.name=request.POST['name']
        event.place=request.POST['place']
        event.type=request.POST['type']
        event.updated_at=timezone.now()
        event.description=request.POST['description']
        event.contact=request.POST['contact']
        event.realtime=request.POST['realtime']
        
        file = request.FILES.get('image')
        if file:
            temp_file_path,name = rescale(file,700)
            folder = f"event_images"  
            file_extension = name.split('.')[-1]
            
            file_url = FileUpload(s3_client).upload(open(temp_file_path, 'rb'), folder, "thumnail"+str(event_id)+"."+file_extension)
            event.thumnail=file_url

            os.remove(temp_file_path)

        event.save()
        if 'day1' in request.POST:
            try:
                day = EventDay.objects.get(event=event_id,date=8)
                if day:
                    day.start_time=request.POST['start_time_8']
                    day.end_time=request.POST['end_time_8']
                    day.save()
            except EventDay.DoesNotExist:
                event=Event.objects.get(id=event_id)
                day = EventDay(event=event,date=8,day="수요일", start_time=request.POST['start_time_8'], end_time=request.POST['end_time_8'])
                day.save()
        else:
            try:
                day = EventDay.objects.get(event=event_id, date=8)
                day.delete()
            except EventDay.DoesNotExist:
                pass

        if 'day2' in request.POST:
            try:
                day = EventDay.objects.get(event=event_id,date=9)
                if day:
                    day.start_time=request.POST['start_time_9']
                    day.end_time=request.POST['end_time_9']
                    day.save()
            except EventDay.DoesNotExist:
                event=Event.objects.get(id=event_id)
                day = EventDay(event=event,date=9,day="목요일", start_time=request.POST['start_time_9'], end_time=request.POST['end_time_9'])
                day.save()
        else:
            try:
                day = EventDay.objects.get(event=event_id, date=9)
                day.delete()
            except EventDay.DoesNotExist:
                pass

        if 'day3' in request.POST:
            try:
                day = EventDay.objects.get(event=event_id,date=10)
                if day:
                    day.start_time=request.POST['start_time_10']
                    day.end_time=request.POST['end_time_10']
                    day.save()
            except EventDay.DoesNotExist:
                event=Event.objects.get(id=event_id)
                day = EventDay(event=event,date=10,day="금요일", start_time=request.POST['start_time_10'], end_time=request.POST['end_time_10'])
                day.save()
        else:
            try:
                day = EventDay.objects.get(event=event_id, date=10)
                day.delete()
            except EventDay.DoesNotExist:
                pass
            
        messages.success(request, '수정이 완료되었습니다!')
        return redirect('collects:event_detail',event_id=event.id)

def event_delete_view(request,event_id):
    if request.method == "POST":
        event = Event.objects.get(pk=event_id)
        event.delete()
        return redirect('collects:event_list')

def event_add_page_view(request):
    return render(request, 'eventadd.html')


def event_add_view(request):
    if request.method == "POST":
        event=Event(
            name=request.POST['name'],
            place=request.POST['place'],
            type=request.POST['type'],
            updated_at=timezone.now(),
            description=request.POST['description'],
            contact=request.POST['contact'],
            realtime=request.POST['realtime'],
            user=User.objects.get(id=1)
        )
        event.save()
        event_id=event.id
        file = request.FILES.get('image')
        if file:
            temp_file_path,name = rescale(file,700)
            folder = f"event_images"  
            file_extension = name.split('.')[-1]

            file_url = FileUpload(s3_client).upload(open(temp_file_path, 'rb'), folder, "thumnail"+str(event_id)+"."+file_extension)
            
            event.thumnail=file_url

            os.remove(temp_file_path)
            event.save()
        if 'day1' in request.POST:
            try:
                day = EventDay.objects.get(event=event_id,date=8)
                if day:
                    day.start_time=request.POST['start_time_8']
                    day.end_time=request.POST['end_time_8']
                    day.save()
            except EventDay.DoesNotExist:
                event=Event.objects.get(id=event_id)
                day = EventDay(event=event,date=8,day="수요일", start_time=request.POST['start_time_8'], end_time=request.POST['end_time_8'])
                day.save()
        else:
            try:
                day = EventDay.objects.get(event=event_id, date=8)
                day.delete()
            except EventDay.DoesNotExist:
                pass

        if 'day2' in request.POST:
            try:
                day = EventDay.objects.get(event=event_id,date=9)
                if day:
                    day.start_time=request.POST['start_time_9']
                    day.end_time=request.POST['end_time_9']
                    day.save()
            except EventDay.DoesNotExist:
                event=Event.objects.get(id=event_id)
                day = EventDay(event=event,date=9,day="목요일", start_time=request.POST['start_time_9'], end_time=request.POST['end_time_9'])
                day.save()
        else:
            try:
                day = EventDay.objects.get(event=event_id, date=9)
                day.delete()
            except EventDay.DoesNotExist:
                pass

        if 'day3' in request.POST:
            try:
                day = EventDay.objects.get(event=event_id,date=10)
                if day:
                    day.start_time=request.POST['start_time_10']
                    day.end_time=request.POST['end_time_10']
                    day.save()
            except EventDay.DoesNotExist:
                event=Event.objects.get(id=event_id)
                day = EventDay(event=event,date=10,day="금요일", start_time=request.POST['start_time_10'], end_time=request.POST['end_time_10'])
                day.save()
        else:
            try:
                day = EventDay.objects.get(event=event_id, date=10)
                day.delete()
            except EventDay.DoesNotExist:
                pass
            
        messages.success(request, '등록이 완료되었습니다!')

        return redirect('collects:event_list')
