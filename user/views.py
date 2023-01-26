from django.shortcuts import render, redirect
from django.contrib.auth.models import User,Group
from django.http import HttpResponse
from django.contrib import auth
from django import forms
from django.core.exceptions import ObjectDoesNotExist

default_group = 'ChangeYourGroup'

def register(request):
      if request.method == "GET":
        return render(request, 'register.html')
      elif request.method == "POST":
        username = request.POST.get('username',None)
        #email = request.POST.get('email',None)
        #group = request.POST.get('group',None)
        password = request.POST.get('password1',None)
        re_password = request.POST.get('password2',None)
        res_data_register = {}
        if not (username and password and re_password) :
            res_data_register['message'] = "모든 값을 입력해야 합니다."
        elif User.objects.filter(username=username).exists():
            res_data_register['message'] = "아이디가 이미 존재합니다."
        #elif User.objects.filter(email=email).exists():
            #res_data_register['message'] = "메일이 이미 존재합니다"
        elif password != re_password :
            # return HttpResponse('비밀번호가 다릅니다.')
            res_data_register['message'] = "비밀번호가 다릅니다."
        else :
            user = User.objects.create_user(username=request.POST["username"], password=request.POST["password1"])
            try:
                g = Group.objects.get(name=default_group)
            except Group.DoesNotExist:
                create_group=Group.objects.create(name=default_group)
                g = Group.objects.get(name=default_group)
                pass
            user.groups.add(g)
            res_data_register['message'] = "회원가입이 완료되었습니다."
        return render(request, 'register.html', res_data_register) #register를 요청받으면

def group(request):
    res_data_group = {}
    res_data_group['group_list']=Group.objects.exclude(name=default_group)
    if request.method =="POST":
        old_group = request.user.groups.all()[0]
        g=Group.objects.get(name=old_group)
        g.user_set.remove(request.user)
        new_group = request.POST.get('group',None)
        g=Group.objects.get(name=new_group)
        request.user.groups.add(g)
        
        res_data_group['message']="그룹 변경이 완료되었습니다."


    return render(request, 'group.html',res_data_group)


def login(request):
    if request.method == "GET":
        return render(request, 'login.html')
    elif request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        res_data_login = {}
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
           res_data_login['error'] = "아이디, 비밀번호가 일치하지 않습니다."
           return render(request, 'login.html', res_data_login)
    else:
       # res_data_login['error'] = "아이디, 비밀번호를 입력해주세요."
        return render(request, 'login.html',res_data_login)

def logout(request):
     auth.logout(request)
     return redirect('/')



