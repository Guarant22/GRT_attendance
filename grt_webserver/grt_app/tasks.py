from celery import shared_task
from .models import AccessToken
from .services import WebexServices
import datetime

@shared_task
def check_token_expire():
    webex=WebexServices()
    token=webex.get_access_token()
    today=datetime.date.today()
    if token.expire_time.date()==today:
        webex.refresh_access_token()