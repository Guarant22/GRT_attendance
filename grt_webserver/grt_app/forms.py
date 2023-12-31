from django import forms
from .models import Student, MeetingTime

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'email', 'phone_num']

# class MeetingTimeForm(forms.ModelForm):
#     class Meta:
#         model = MeetingTime
#         fields = ['date', 'start_time']
        
class StudentSearchForm(forms.Form):
    name = forms.CharField(required=False, label='학생 이름')
    
class MeetingTimeForm(forms.ModelForm):
    class Meta:
        model = MeetingTime
        fields = ['email', 'date', 'start_time', 'end_time']  # 필요한 필드를 여기에 추가합니다.
        
class MeetingRoomForm(forms.Form):
    room = forms.CharField(required=True, label='meeting_num')
    
    def clean_room(self):
        data=self.cleaned_data['room']
        room_num=data.replace(" ","")
        return room_num
        