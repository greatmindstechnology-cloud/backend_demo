from django.db import models

from django.db import models
from signup_gmt.models import LoginDetails

class AdminData(models.Model):
    login = models.OneToOneField(LoginDetails, on_delete=models.CASCADE)

    first_name = models.CharField(max_length=100, blank=True, default='')
    last_name = models.CharField(max_length=100, blank=True, default='')
    email = models.EmailField(unique=True, blank=True, default='')
    phone_number = models.CharField(max_length=15, blank=True, default='')
    gender = models.CharField(max_length=10, blank=True, default='')
    profile_picture = models.ImageField(upload_to='admin/', blank=True, null=True)
    role = models.CharField(default='admin', max_length=20)

    created_at = models.DateTimeField(auto_now_add=True)

