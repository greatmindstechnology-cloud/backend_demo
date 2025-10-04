from django.db import models
import datetime
from django.utils import timezone


class Role(models.Model):
    role_name = models.CharField(max_length=50)

class LoginDetails(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)

class StudentInformation(models.Model):
    login = models.OneToOneField(LoginDetails, on_delete=models.CASCADE)
    role = models.CharField(default='student', max_length=20)

    profile_picture = models.ImageField(upload_to='student/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    firstname = models.CharField(max_length=100, blank=True, default='')
    lastname = models.CharField(max_length=100, blank=True, default='')
    email = models.EmailField(unique=True, blank=True, default='')
    contact_number = models.CharField(max_length=15, blank=True, default='')
    alt_contact = models.CharField(max_length=15, blank=True, default='')
    father_name = models.CharField(max_length=100, blank=True, default='')
    mother_name = models.CharField(max_length=100, blank=True, default='')
    pincode = models.CharField(max_length=10, blank=True, default='')
    description = models.TextField(blank=True, default='')
    designation = models.CharField(max_length=100, blank=True, default='')
    gender = models.CharField(max_length=10, blank=True, default='')
    skills = models.JSONField(blank=True, default=list, null=True)

    account_holder_name = models.CharField(max_length=100, blank=True, default='')
    account_number = models.CharField(max_length=50, blank=True, default='')
    bank_location = models.CharField(max_length=100, blank=True, default='')
    bank_name = models.CharField(max_length=100, blank=True, default='')
    branch_name = models.CharField(max_length=100, blank=True, default='')
    ifsc_code = models.CharField(max_length=20, blank=True, default='')

    institution_name = models.CharField(max_length=100, blank=True, default='')
    location = models.CharField(max_length=100, blank=True, default='')
    major_subject = models.CharField(max_length=100, blank=True, default='')
    qualification = models.CharField(max_length=100, blank=True, default='')

    cgpa = models.FloatField(blank=True, null=True)
    passedout = models.IntegerField(blank=True, null=True)
    door_number = models.CharField(max_length=100, blank=True, default='')
    street_name = models.CharField(max_length=100, blank=True, default='')
    landmark = models.CharField(max_length=100, blank=True, default='')
    country = models.CharField(max_length=100, blank=True, default='')
    state = models.CharField(max_length=100, blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    


class TrainerData(models.Model):
    login = models.OneToOneField(LoginDetails, on_delete=models.CASCADE)

    STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting')
    role = models.CharField(default='trainer', max_length=20)


    first_name = models.CharField(max_length=100, blank=True, default='')
    last_name = models.CharField(max_length=100, blank=True, default='')
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, default='')
    email = models.EmailField(unique=True, blank=True, default='')
    phone_number = models.CharField(max_length=15, blank=True, default='')
    pincode = models.CharField(max_length=10, blank=True, default='')

    highest_qualification = models.CharField(max_length=100, blank=True, default='')
    specialization = models.CharField(max_length=100, blank=True, default='')
    total_experience_years = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    current_organization = models.CharField(max_length=100, blank=True, default='')
    previous_teaching_experience = models.TextField(blank=True, default='')
    certifications = models.CharField(max_length=255, blank=True, default='')

    account_holder_name = models.CharField(max_length=100, blank=True, default='')
    bank_name = models.CharField(max_length=100, blank=True, default='')
    branch_name = models.CharField(max_length=100, blank=True, default='')
    account_number = models.CharField(max_length=30, blank=True, default='')
    bank_location = models.CharField(max_length=100, blank=True, default='')
    ifsc_code = models.CharField(max_length=20, blank=True, default='')

    resume = models.FileField(upload_to='trainer/', blank=True, null=True)
    id_proof = models.FileField(upload_to='trainers/', blank=True, null=True)
    educational_certificates = models.FileField(upload_to='trainer/', blank=True, null=True)
    profile_picture = models.ImageField(upload_to='trainer/', blank=True, null=True)

    available_days = models.JSONField(blank=True, null=True, default=list)
    available_mode = models.CharField(max_length=50, blank=True, default='')
    preferred_time_slots = models.CharField(max_length=100, blank=True, default='')
    door_number = models.CharField(max_length=100, blank=True, default='')
    street_name = models.CharField(max_length=100, blank=True, default='')
    landmark = models.CharField(max_length=100, blank=True, default='')
    country = models.CharField(max_length=100, blank=True, default='')
    state = models.CharField(max_length=100, blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')

class VendorData(models.Model):
    login = models.OneToOneField(LoginDetails, on_delete=models.CASCADE)
    STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting')
    role = models.CharField(default='vendor', max_length=20)
    firstname = models.CharField(max_length=100, blank=True, default='')
    lastname = models.CharField(max_length=100, blank=True, default='')
    business_name = models.CharField(max_length=200, blank=True, default='')
    business_type = models.CharField(max_length=100, blank=True, default='')
    gst_number = models.CharField(max_length=50, blank=True, default='')
    registration_number = models.CharField(max_length=100, blank=True, default='')
    year_of_establishment = models.IntegerField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, default='')
    contact_phone = models.CharField(max_length=15, blank=True, default='')
    alternate_contact = models.CharField(max_length=15, blank=True, default='')
    pincode = models.CharField(max_length=10, blank=True, default='')
    country = models.CharField(max_length=100, blank=True, default='')

    account_holder_name = models.CharField(max_length=100, blank=True, default='')
    account_number = models.CharField(max_length=30, blank=True, default='')
    ifsc_code = models.CharField(max_length=20, blank=True, default='')   
    bank_location = models.CharField(max_length=100, blank=True, default='')
    bank_name = models.CharField(max_length=100, blank=True, default='')
    branch_name = models.CharField(max_length=100, blank=True, default='')
    

    gst_certificate = models.FileField(upload_to='vendor/', blank=True, null=True)
    business_license = models.FileField(upload_to='vendor/', blank=True, null=True)
    pan_card = models.FileField(upload_to='vendor/', blank=True, null=True)
    profile_picture = models.ImageField(upload_to='vendor/', blank=True, null=True)

    events_type = models.TextField(blank=True, default='')
    event_history = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    door_number = models.CharField(max_length=100, blank=True, default='')
    street_name = models.CharField(max_length=100, blank=True, default='')
    landmark = models.CharField(max_length=100, blank=True, default='')
    country = models.CharField(max_length=100, blank=True, default='')
    state = models.CharField(max_length=100, blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
