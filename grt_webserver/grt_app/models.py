from djongo import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
# Create your models here.

class SingleUserManager(BaseUserManager):
    def create_user(self, ID, password=None, **extra_fields):
        if not ID:
            raise ValueError('Users must have an ID')
        user = self.model(ID=ID, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, ID, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')


class SingleUser(AbstractBaseUser, PermissionsMixin):
    ID          = models.CharField(max_length=100, unique=True, primary_key=True)
    
    USERNAME_FIELD  = "ID"
    REQUIRED_FIELDS = []
    
    objects = SingleUserManager()
    
    class Meta:
        db_table = 'User'
        
    # def save(self, *args, **kwargs):
    #     # 데이터베이스에 이미 사용자가 존재하면 새 사용자 생성 방지
    #     if not self.pk and SingleUser.objects.exists():
    #         raise Exception("Cannot create more than one user.")
    #     super(SingleUser, self).save(*args, **kwargs)


class Student(models.Model):
    name        = models.CharField(max_length=100)
    email       = models.CharField(max_length=100)
    phone_num   = models.CharField(max_length=15)
    
    class Meta:
        db_table = 'Student'
    
class MeetingTime(models.Model):
    student_id  = models.ObjectIdField()
    date        = models.DateField()
    start_time  = models.TimeField()
    end_time    = models.TimeField()
    
    class Meta:
        db_table = 'MeetingTime'