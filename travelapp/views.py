import re
from django.core import mail
from django.shortcuts import redirect, render
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import authenticate,logout, login as auth_login

from django.contrib.auth.models import User
from .models import Profile
import uuid
from website.settings import *
from django.contrib.auth.decorators import login_required

import speech_recognition as sr
from csv import writer
from geopy import distance,Point
from geopy.geocoders import Nominatim
import pandas as pd

r = sr.Recognizer()
li=[]


# Create your views here.
@login_required(login_url= LOGIN_REDIRECT_URL)
def index(request):
    return render(request, 'index.html')


def signUp(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            if User.objects.filter(username=username).first():
                messages.warning(request, 'Username already taken!')
                return redirect('/signup')
            if User.objects.filter(email=email).first():
                messages.warning(request, 'Email already taken!')
                return redirect('/signup')
            
            user_obj = User.objects.create_user(username=username, email=email, password=password)

            # you can use at time of forgot password.
            # user_obj.set_password('newpassword)
            auth_token=str(uuid.uuid4())
            profile_obj = Profile.objects.create(user=user_obj, auth_token=auth_token)
        
            # send_mail
            msg = send_mail(
                subject = 'Activate your account',
                message = f'Here is the message click on the link to activate http://127.0.0.1:8000/verify/{auth_token}',
                from_email = EMAIL_HOST_USER,
                recipient_list = [email],
                fail_silently=False,
            )

            user_obj.save()
            profile_obj.save()

            print('Mail sent successfully')
            messages.success(request, "Account created successfully")
            return redirect('/token')

        except Exception as e:
            print(e)
            return redirect('/error')

        
    return render(request, 'signUp.html')


def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user_obj = User.objects.filter(username = username).first()

        if user_obj is None:
            messages.warning(request, "User not found")
            return redirect("/login")     

        profile_obj = Profile.objects.filter(user = user_obj).first()

        if not profile_obj.verified:
            messages.warning(request, "Profile not verified, check your mail.")
            return redirect("/login")

        user = authenticate(username=username, password=password)
        if user is None:
            messages.warning(request, "Invalid Credentials")
            return redirect("/login")

        auth_login(request, user)
        return redirect("/")
    return render(request, 'login.html')


def send_token(request):
    return render(request, 'send_token.html')


def verify(request, slug):
    try:
        profile_obj = Profile.objects.filter(auth_token = slug).first()
        if profile_obj:
            if profile_obj.verified:
                messages.success(request, 'Account already verified')
                return redirect('/login')

            profile_obj.verified = True
            profile_obj.save()
            messages.success(request, 'Your account is now verified')
            return redirect('/login')
        else:
            return redirect('/error')
        
    except Exception as e:
        print(e)
        return redirect('/error')


def error(request):
    return render(request, "error.html")

def errorvc(request):
    return render(request, "")
    
def logoutUser(requests):
    logout(requests)
    messages.success(requests, 'Logged out successfully')
    return redirect('/login')

def forgetPassword(request):
    if request.method == "POST":
        email = request.POST.get('email')
    
        try:
            userObj = User.objects.filter(email=email).first()
            if userObj is None:
                messages.warning(request, "User not found")
                return redirect("/login")

            profileObj = Profile.objects.filter(user = userObj).first()
            if profileObj is None:
                messages.warning(request, "Internal Error")
                return redirect('/error')

            token = profileObj.auth_token
            msg = send_mail(
                subject = 'Reset your Password',
                message = f'Follow this link to reset your password http://127.0.0.1:8000/reset/{token}',
                from_email = EMAIL_HOST_USER,
                recipient_list = [email],
                fail_silently=False,
            )

            if msg==1:
                return render(request, "mail_forgetPass.html")
            else:
                messages.warning(request, "Something went wrong! Try again later.")
                return redirect('/error')

        except Exception as e:
            print(e)
            return redirect('/error')

    return render(request, "forgetPass.html")


def reset(request, token):
    try:
        if request.method == "POST":
            new_password = request.POST.get('password1')
            confirm_password = request.POST.get('password2')

            if new_password == confirm_password:
                # print(confirm_password)

                profile_obj = Profile.objects.filter(auth_token = token).first()
                
                if profile_obj is None:
                    messages.warning(request, "Something went wrong!")
                    return redirect("/error") 

                user_id = profile_obj.user.id

                if user_id is None:
                    messages.warning(request, "User not found :(")
                    return redirect("/login")

                user_obj = User.objects.get(id = user_id)
                user_obj.set_password(new_password)
                user_obj.save()

                messages.success(request, "Password updated successfully :)")
                return redirect("/login")

            else:
                messages.warning(request, "Passwords doesn't match, enter again")


        # if user_obj:
            # print(user_obj.username)
        #     if profile_obj.verified:
        #         messages.success(request, 'Account already verified')
        #         return redirect('/login')

        #     profile_obj.verified = True
        #     profile_obj.save()
        #     messages.success(request, 'Your account is now verified')
        #     return redirect('/login')
        # else:
        #     return redirect('/error')
        
    except Exception as e:
        print(e)
        # return redirect('/error')

    return render(request, 'PassInput.html')

def voiceinput(request):
    li=[]
    try:
        try:
            with sr.Microphone() as source1:
                print("Silence please, calibrating background noise")
                r.adjust_for_ambient_noise(source1,duration=2)
                print("Calibrated, now speak")
                print("From: ")
                From=r.listen(source1,phrase_time_limit=3)
                text=r.recognize_google(From)
                text=text.lower()
                print("You said: ",text)
                li.append(text)
        
                print("To: ")
                To=r.listen(source1,phrase_time_limit=3)
                text1=r.recognize_google(To)
                text1=text1.lower()
                print("You said: ",text1)
                li.append(text1)
        except:
            print("Error in microphone")

        print(li)
        with open('journey.csv', 'a+',newline='') as f_object:
            writer_object = writer(f_object)
            writer_object.writerow(li)
            f_object.close()
        print("\nSaved in File------!!!!!!")
        
        return render(request,'index.html')
    except:
        return render(request,'errorvc.html')
    
    
def distancecost(request):
    try:
        geolocator=Nominatim(user_agent="travelapp")
        df=pd.read_csv('journey.csv')
        lat = []
        long = []
        for row in df['source']:
            addr = geolocator.geocode(row, timeout=10)
            if addr is None:
                lat.append(None)
                long.append(None)
            else:
                latitude = addr.latitude
                longitude = addr.longitude    
            lat.append(latitude)
            long.append(longitude)
        df['latitude1'] = lat
        df['longitude1'] = long
        # Another Iteration
        lat = []
        long = []
        for row in df['destination']:
            addr = geolocator.geocode(row, timeout=10)
            if addr is None:
                lat.append(None)
                long.append(None)
            else:
                latitude = addr.latitude
                longitude = addr.longitude  
            lat.append(latitude)
            long.append(longitude)
        df['latitude2'] = lat
        df['longitude2'] = long
        df['point1'] = df.apply(lambda row: Point(latitude=row['latitude1'], longitude=row['longitude1']), axis=1)
        df['point2'] = df.apply(lambda row: Point(latitude=row['latitude2'], longitude=row['longitude2']), axis=1)
        df['distance_km'] = df.apply(lambda row: distance.distance(row['point1'], row['point2']).km if row['point2'] is not None else float('nan'), axis=1)
        df.to_csv('result.csv', index=False)
        df.to_excel('result.xlsx', index=False)
        dis=df.distance_km.sum()
        cost_per_km=8
        x=dis*cost_per_km
        ta = round(x)
        print("your current TA is: ",ta," Rs")
        return render(request, "travel/cost-travel.html",context = {'ta' : ta})
    
    except:
        return render(request,'errorvc.html')