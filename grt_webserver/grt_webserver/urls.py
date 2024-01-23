"""
URL configuration for grt_webserver project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from grt_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('grt_app/',include('grt_app.urls')),
    path('', views.MainPageView.as_view(),name='mainpage'),
    path('grt/login/',views.LoginView.as_view(), name='loginpage'),
    path('grt/auth/login/', views.LoginView.as_view(), name = 'login'),
    path('grt/auth/check_login/', views.CheckLoginView.as_view(), name = 'check_login'),
    path('grt/auth/logout/',views.LogoutView.as_view(), name='logoutpage'),
    path('grt/auth/getoauth/',views.LogoutView.as_view(), name='logoutpage'),
    path('grt/students/', views.StudentListView.as_view(), name='studentlist'),
    path('grt/meetings/', views.MeetingListView.as_view(), name='meetinglist'),
    path('grt/addstudent/', views.AddStudentView.as_view(), name = 'addstudent'),
    path('grt/addmeeting/', views.AddMeetingView.as_view(), name='addmeeting'),
    path('grt/excelmeeting/', views.ExcelUploadView.as_view(), name='excelmeeting'),
    # path('grt/createmeeting/', views.CreateMeetingView.as_view(), name='createmeeting'),
    path('grt/checkattendance/', views.CheckAttendanceView.as_view(), name='checkattendance'),
    path('grt/getparticipant/', views.GetParticipantView.as_view(), name='getparticipant'),
    path('grt/gettest/', views.TestView.as_view(), name='gettest'),
    path('grt/requestpermission/', views.RequestPermissionView.as_view(), name='requestpermission'),
    path('grt/oauth/', views.OauthView.as_view(), name='oauth'),
    path('grt/deletemeeting/', views.DeleteMeetingView.as_view(), name='deletemeeting'),
    path('grt/deletestudent/', views.DeleteStudentView.as_view(), name='deletestudent'),
]
