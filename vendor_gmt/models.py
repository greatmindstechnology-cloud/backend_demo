from django.db import models
from signup_gmt.models import VendorData 
from django.utils import timezone

class VendorInternship(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    vendor = models.ForeignKey(VendorData, on_delete=models.CASCADE, related_name='internships')

    title = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    mode = models.CharField(max_length=20)  # No choices
    duration = models.CharField(max_length=50)
    start_date = models.DateField()
    stipend = models.CharField(max_length=50)
    skills_required = models.JSONField(default=list, blank=True)
    eligibility_criteria = models.TextField()
    application_deadline = models.DateField()
    number_of_openings = models.PositiveIntegerField()
    contact_info = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    application_process = models.TextField()

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


class VendorEvent(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    vendor = models.ForeignKey(VendorData, on_delete=models.CASCADE, related_name='events')

    event_title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    event_date_time = models.DateTimeField()
    duration = models.CharField(max_length=50)
    event_type = models.CharField(max_length=255)
    target_audience = models.CharField(max_length=255)
    capacity = models.PositiveIntegerField()
    registration_deadline = models.DateField()
    registration_fee = models.CharField(max_length=50)
    contact_information = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=255)
    event_link = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




class CSREvent(models.Model):
    EVENT_TYPES = [
        ("Blood Donation", "blood donation"),
        ("Green Based Events", "green based events"),
        ("Motivational Talk", "motivational talk"),
        ("Awarness", "awarness"),
        ("other", "Other"),
    ]

    vendor = models.ForeignKey(VendorData, on_delete=models.CASCADE, related_name="csrevents")
    
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    event_name = models.CharField(max_length=200)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    agenda_file = models.FileField(upload_to="csr_events/agenda/", null=True, blank=True)
    video = models.FileField(upload_to="csr_events/videos/", null=True, blank=True)
    no_of_slots = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.event_name} ({self.event_type})"


from django.db import models

class BloodNeed(models.Model):
    BLOOD_GROUPS = [
        ("A+", "A+"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B-", "B-"),
        ("O+", "O+"),
        ("O-", "O-"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
    ]

    REQUEST_STATUS = [
        ("open", "Open"),
        ("Closed", "closed"),
    ]

    request_id = models.CharField(max_length=50, unique=False)
    role_name = models.CharField(max_length=50, default="requester")

    location = models.CharField(max_length=200)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    request_status = models.CharField(max_length=20, choices=REQUEST_STATUS)
    blood_unit = models.IntegerField()  
    contact_no = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.request_id}] {self.role_name} requested {self.blood_unit} units of {self.blood_group} at {self.location}"
