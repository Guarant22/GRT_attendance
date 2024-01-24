from django.shortcuts import render,redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView, View
from rest_framework import generics
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout as auth_logout
from bson import ObjectId
import json
import requests
import os
import datetime


from .models import Student, MeetingTime, AccessToken
from .forms import StudentForm, StudentSearchForm, MeetingTimeForm, MeetingRoomForm
from .serializers import LoginUserSerializer, UserSeriazlizer
from .services import WebexServices, AttendanceServices

class LoginView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        return render(request, 'login.html')
    
    serializer_class = LoginUserSerializer

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        serializer = self.get_serializer(data=data)
        # if not serializer.is_valid():
        #     print(serializer.errors)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        token, created = Token.objects.get_or_create(user=user)
        login(request, user)
        # print("login\n")
        return Response({
                         'ID':user.ID,
                         'token':token.key
                         })
        
class CheckLoginView(generics.GenericAPIView):
    def get(self,request, *args, **kwargs):
        if request.user.is_authenticated:
            print("login")
            # 사용자가 로그인한 경우
            return JsonResponse({'logged_in': True})
        else:
            print("no login")
            # 사용자가 로그인하지 않은 경우
            return JsonResponse({'logged_in': False})

class LogoutView(View):
    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return render(request, 'index.html')

class StudentListView(View):
    def get(self, request, *args, **kwargs):
        form = StudentSearchForm(request.GET or None)
        if form.is_valid() and form.cleaned_data['name']:
            students = Student.objects.filter(name__icontains=form.cleaned_data['name'])
            # for student in students:
            #     print(student.id)
        else:
            students = Student.objects.all()
            # for student in students:
            #     print(ObjectId(student.id))
            #     print(type(student.id))
        return render(request, 'studentlist.html', {'form': form, 'students': students})

class MeetingListView(View):
    def get(self,request, *args, **kwargs):
        student_email = request.GET.get('student_email')
        print(student_email)
        student = Student.objects.get(email=student_email)
        try:
            meetings = MeetingTime.objects.filter(email=student_email)
            print(meetings)
            meetings_with_str_id=[{
                'id_str':str(meeting._id),
                'email':meeting.email,
                'date':meeting.date,
                'start_time':meeting.start_time,
                'end_time':meeting.end_time,
                'pk':meeting.pk
            } for meeting in meetings]
            print(meetings_with_str_id)
        except:
            meetings = None
            meetings_with_str_id = None
        data={
            'student':student,
            'meetings':meetings_with_str_id
        }
        return render(request,'meetinglist.html',data)


class AddStudentView(View):    
    def get(self, request, *args, **kwargs):
        form = StudentForm()
        return render(request, 'addstudent.html', {'form': form})
    
    def post(self, request, *args, **kwargs):
        form = StudentForm(request.POST)
        if form.is_valid():
            student=form.save(commit=False)
            student.save()
            print(student)
            return redirect('addstudent')

    
class AddMeetingView(View):
    def get(self, request, *args, **kwargs):
        student_email = request.GET.get('student_email')
        student = Student.objects.get(email=student_email)
        # print(student.email)
        form = MeetingTimeForm(initial={'email':student_email})
        return render(request,'addmeeting.html',{'form':form,
                                                 'student':student})
    
    def post(self, request, *args, **kwargs):
        form = MeetingTimeForm(request.POST)
        if form.is_valid():
            meeting_time = form.save()
            # print(meeting_time)
            # student_email = request.POST.get('student_email')
            # meeting_time.zoom_id = student_email  # MeetingTime 객체에 student 할당
            # meeting_time.save()
            print("success")
            return redirect('studentlist')
        else:
            print(form.errors)
            return render(request, 'studentlist.html', {'success':"No"})
        
class ExcelUploadView(View):
    template_name='excelmeeting.html'
    def get(self,request):
        return render(request,self.template_name)
    
    def post(self,request):
        if 'excel_file' in request.FILES:
            excel_file=request.FILES['excel_file']
            service=AttendanceServices()
            df=service.read_excel_file(excel_file)
            service.save_excel_mongodb(df)
            return redirect('mainpage')
        
        return HttpResponse('Excel 파일을 업로드하세요.')
class DeleteStudentView(View):
    def post(self, request, *args, **kwargs):
        try:
            data=json.loads(request.body)
            print(data)
            email=data.get('email')
            try:
                student=Student.objects.get(email=email)
                print(student)
                student.delete()
                # meeting_time=MeetingTime.objects.get(id=ObjectId(meeting_id))
                # return meeting_time
            except Exception as e:
                print(e)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        
class DeleteMeetingView(View):
    def post(self, request):
        try:
            data=json.loads(request.body)
            print(data)
            id=data.get('meeting_id_str')
            date=data.get('date')
            email = data.get('email')
            start_time = data.get('start_time')
            end_time = data.get('end_time')
            try:
                meeting=MeetingTime.objects.get(date=date, email=email,start_time=start_time,end_time=end_time)
                print(meeting)
                meeting.delete()
                # meeting_time=MeetingTime.objects.get(id=ObjectId(meeting_id))
                # return meeting_time
            except Exception as e:
                print(e)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        
# class CreateMeetingView(View):
#     def get(self,request,*args, **kwargs):
#         meeting=ZoomServices()
#         meeting.create_meeting()
#         return render(request,'index.html',{'status':"success"})
        
class CheckAttendanceView(View):
    def get(self, request, *args, **kwargs):
        form = MeetingRoomForm(request.GET)
        if form.is_valid() and form.cleaned_data['room']:
            meetingnum=form.cleaned_data['room']
            # meeting=ZoomServices()
            meeting=WebexServices()
            meetingId=meeting.get_meeting_id(meetingnum)
            participants=meeting.get_participants(meetingId)
            # response=meeting.get_participants(meetingId)
            # participants=response.get("participants",[])
            print(participants)
            time=AttendanceServices()
            registrants=time.get_registrants()
            print(registrants)
            # meeting.check_attendance(participants=participants)
            absent=[p for p in registrants if p not in participants]
            print(absent)
            
            # 부재중인 참가자들의 이름 가져오기
            absent_students = list(Student.objects.filter(email__in=absent))
            # .values_list('name', flat=True)
            # absent_names = list(absent_students)
            # print(absent_names)
            return render(request, 'checkattendance.html',{'form': form,
                                                       'absents':absent_students})
        return render(request, 'checkattendance.html',{'form': form})
        
        
class GetParticipantView(View):
    def post(self,request,*args, **kwargs):
        response=json.loads(request.body)
        participant=response['participant']
        print(participant)
        
class RequestPermissionView(View):
    def get(self,request,*args, **kwargs):
        oauth_url=WebexServices().get_permission_url()
        return redirect(oauth_url)
        # return HttpResponseRedirect(oauth_url)
        
class OauthView(View):
    def get(self,request, *args,**kwargs):
        state=request.GET.get('state')
        code=request.GET.get('code')
        if state == 'abcd1234':
            WebexServices().save_access_token(code)
        return render(request,'index.html')
        
class TestView(View):
    def get(self, request, *args, **kwargs):
        token=WebexServices().refresh_access_token()
        if token:
            print(token)
            return render(request,'index.html')
        else:
            return JsonResponse({'success': False})

class MainPageView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'index.html')