import os
import requests
import pytz
import datetime
import logging
from django.http import JsonResponse
from .models import MeetingTime, AccessToken, RefreshToken
from urllib.parse import urlencode
from django.db.models import Q

# Cisco Webex
class WebexServices:
    def __init__(self):
        self.client_id      ='C03c4cc4241b670127061c64ffaa4d51983adb429256e00f581e155a4bba3b6cf'
        self.client_secret  ='75a811db4175b51eda367464a91679c1a40c1b7e9f9684186952ce8d4834db0b'
        self.redirect_base_uri   ='https://limhyeongseok.pythonanywhere.com/'
        self.permission_url      ='https://webexapis.com/v1/authorize?'
        self.access_token   = self.get_access_token()
        self.api_base_url   = "https://webexapis.com/v1"
        self.headers        ={
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        
    def get_access_token(self):
        latest_token=AccessToken.objects.latest('expire_time')
        return latest_token.access_token
    
    def get_refresh_token(self):
        latest_refresh_token=RefreshToken.objects.latest('refresh_expire_time')
        return latest_refresh_token

    def get_permission_url(self):
        params={
            "response_type":"code",
            "client_id":self.client_id,
            "redirect_uri":f"{self.redirect_base_uri}grt/oauth/",
            "scope":'spark:kms meeting:schedules_read meeting:participants_read meeting:controls_read meeting:admin_participants_read meeting:participants_write meeting:schedules_write',
            'state': 'abcd1234',
        }
        oauth_url=self.permission_url+urlencode(params)
        print(oauth_url)
        return oauth_url

    def save_access_token(self,code):
        headers={
            "accept":"application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        params={
            "grant_type":"authorization_code",
            "client_id":self.client_id,
            "client_secret":self.client_secret,
            "code":code,
            "redirect_uri":"https://limhyeongseok.pythonanywhere.com/grt/oauth",
        }
        resp=requests.post(f"{self.api_base_url}/access_token",
                           headers=headers,data=params)
        data=resp.json()
        logging.info(f"Access token response: {data}")
        access_token = data.get("access_token")
        expires_in = data.get("expires_in")
        refresh_token = data.get("refresh_token")
        refresh_expires_in = data.get("refresh_token_expires_in")
        current_time = datetime.datetime.now()
        expire_time = current_time + datetime.timedelta(seconds=expires_in)
        refresh_expire_time = current_time + datetime.timedelta(seconds=refresh_expires_in)

        token_obj=AccessToken(
            access_token=access_token,
            expire_time=expire_time
        )
        # print(access_token)
        token_obj.save()

        token_obj=RefreshToken(
            refresh_token=refresh_token,
            refresh_expire_time=refresh_expire_time
        )
        token_obj.save()

        return access_token
    
    def refresh_access_token(self):
        latest_access_token=self.get_access_token()
        today=datetime.date.today()
        if latest_access_token.expire_time.date()==today:
            latest_refresh_token=self.get_refresh_token()
            params={
                'grant_type':'refresh_token',
                'client_id':self.client_id,
                'client_secret':self.client_secret,
                'refresh_token':latest_refresh_token
            }
            resp=requests.post(f"{self.api_base_url}/access_token",data=params)
            data=resp.json()
        
            access_token = data.get("access_token")
            expires_in = data.get("expires_in")
            refresh_token = data.get("refresh_token")
            refresh_expires_in = data.get("refresh_token_expires_in")
            current_time = datetime.datetime.now()
            expire_time = current_time + datetime.timedelta(seconds=expires_in)
            refresh_expire_time = current_time + datetime.timedelta(seconds=refresh_expires_in)

            token_obj=AccessToken(
                access_token=access_token,
                expire_time=expire_time
            )
            # print(access_token)
            token_obj.save()

            token_obj=RefreshToken(
                refresh_token=refresh_token,
                refresh_expire_time=refresh_expire_time
            )
            token_obj.save()
        
            return access_token

    def create_meeting(self):
        start_time="2023-12-26T00:00"
        end_time="2023-12-26T23:00"

    def get_meeting_id(self, meetingnum):
        print("meetingNUM: "+meetingnum)
        params={"meetingNumber":meetingnum}
        print(self.access_token)
        resp=requests.get(f"{self.api_base_url}/meetings",
                          headers=self.headers,params=params)
        if resp.status_code!=200:
            print(resp.status_code)
            return JsonResponse({"error":"Got error"},status=resp.status_code)
        data=resp.json()
        print(resp)
        meetingIds=[item['id'] for item in data['items']]
        meetingId=meetingIds[0]

        return meetingId


    def get_participants(self,meetingId):
        print("meetingID: "+str(meetingId))
        params={"max":100,
                "meetingId":meetingId}
        resp = requests.get(f"{self.api_base_url}/meetingParticipants",
                             headers=self.headers,params=params)
        data=resp.json()

        print(data)
        if resp.status_code==200:
            participants=[item['email'] for item in data['items']]
            print(type(participants))
            print("Service:")
            print(participants)
            return participants
            # return JsonResponse({"participants":participants})
        else:
            error_code=resp.status_code
            print("Failed to get participants.")
            print(resp.status_code)
            return JsonResponse({"error":"Got error"},status=error_code)

    def check_attendance(self, participants):
        # time_now=AttendanceServices.get_time()

        return participants


class AttendanceServices:
    def __init__(self):
        self.current_time=self.get_time()
        self.current_hour=self.current_time.strftime("%H:%M")
        self.current_date=self.current_time.strftime("%m/%d")
        self.formatted_date=self.current_time.strftime("%y/%m/%d")

    def get_time(self):
        # UTC 현재 시간
        utc_now = datetime.datetime.utcnow()

        # UTC 시간을 한국 시간대(KST, UTC+9)로 변환
        kst_timezone = pytz.timezone('Asia/Seoul')
        kst_now = utc_now.replace(tzinfo=pytz.utc).astimezone(kst_timezone)

        # print("UTC 시간:", utc_now)
        # print("한국 시간:", kst_now)

        return kst_now

    def get_registrants(self):
        register_meetings=MeetingTime.objects.filter(
            Q(date=self.current_date)|Q(date=self.formatted_date),
            start_time__lte=self.current_hour,
            end_time__gte=self.current_hour
            )
        registrants=list(register_meetings.values_list('email',flat=True))
        # print(registrants)
        return registrants



# zoom
# class ZoomServices:
#     def __init__(self):
#         # replace with your client ID
#         self.client_id = os.environ.get('CLIENT_ID')

#         # replace with your account ID
#         self.account_id = os.environ.get('ACCOUNT_ID')

#         # replace with your client secret
#         self.client_secret = os.environ.get('CLIENT_SECRET')

#         self.auth_token_url = "https://zoom.us/oauth/token"
#         self.api_base_url = "https://api.zoom.us/v2"

#         self.access_token=self.get_access_token()

#         self.headers = {
#             "Authorization": f"Bearer {self.access_token}",
#             "Content-Type": "application/json"
#         }


#     def get_access_token(self):
#         data={
#             "grant_type": "account_credentials",
#             "account_id": self.account_id,
#             "client_secret": self.client_secret
#         }
#         response = requests.post(self.auth_token_url,auth=(self.client_id,self.client_secret),data=data)

#         if response.status_code!=200:
#                 print("Unable to get access token")
#         else:
#             print("Success")
#         response_data = response.json()
#         access_token = response_data["access_token"]
#         return access_token

#     def create_meeting(self):
#         print(self.client_id)
#         print(self.account_id)
#         print(self.client_secret)

#         start_date="2023-12-28"
#         start_time="17:43"
#         payload = {
#             "topic": "test",
#             "duration": "60",
#             'start_time': f'{start_date}T10:{start_time}',
#             "type": 2
#         }

#         resp = requests.post(f"{self.api_base_url}/users/me/meetings",
#                              headers=self.headers,
#                              json=payload)

#         if resp.status_code!=201:
#             print("Unable to generate meeting link")
#         response_data = resp.json()

#         content = {
#             "meeting_url": response_data["join_url"],
#             "password": response_data["password"],
#             "meetingTime": response_data["start_time"],
#             "purpose": response_data["topic"],
#             "duration": response_data["duration"],
#             "message": "Success",
#             "status":1
#         }
#         print(content)

#     def get_registrants(self,meetingId):
#         print("meetingID: "+meetingId)
#         # params={"type":"live"}
#         resp = requests.get(f"{self.api_base_url}/meetings/{meetingId}/registrants",
#                              headers=self.headers)
#         response_data=resp.json()
#         print(response_data)
#         if resp.status_code==200:
#             participants=resp.json().get("participants",[])
#             print(participants)
#             return JsonResponse({"participants":participants})
#         else:
#             error_code=resp.status_code
#             print("Failed to get participants.")
#             print(resp.status_code)
#             return JsonResponse({"error":"Got error"},status=error_code)

#     def get_participants(self,meetingId):

#         print("meetingID: "+meetingId)
#         # params={"type":"live"}
#         resp = requests.get(f"{self.api_base_url}/metrics/meetings/{meetingId}/participants",
#                              headers=self.headers)
#         response_data=resp.json()
#         print(response_data)
#         if resp.status_code==200:
#             participants=resp.json().get("participants",[])
#             print(participants)
#             return JsonResponse({"participants":participants})
#         else:
#             error_code=resp.status_code
#             print("Failed to get participants.")
#             print(resp.status_code)
#             return JsonResponse({"error":"Got error"},status=error_code)
