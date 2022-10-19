from travelapp import views
from os import name
from django.urls import path
from travelapp.views import *

urlpatterns = [
    path('', views.index, name='Home'),
    path('signup', views.signUp, name='SignUp'),
    path('login', views.login, name='Login'),
    path('token', views.send_token, name='Token'),
    path('error', views.error, name='Error'),
    path('logout', views.logoutUser, name='Logout'),
    path('verify/<slug>', views.verify, name='Token'),
    path('forgetpass', views.forgetPassword, name='ForgetPassword'),
    path('reset/<token>', views.reset, name='ResetPass'),
    path('voiceinput',views.voiceinput, name = 'voiceinput'),
    path('distancecost',views.distancecost, name = 'distancecost'),
    path('errorvc',views.errorvc,name='errorvc')
]