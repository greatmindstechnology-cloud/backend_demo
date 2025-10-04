from django.db import models
from signup_gmt.models import StudentInformation
from django.utils.crypto import get_random_string

class StudentBooking(models.Model):
    student = models.ForeignKey(StudentInformation, on_delete=models.CASCADE, related_name='bookings')
    student_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    additional_notes = models.TextField(blank=True, null=True)
    booking_id = models.CharField(max_length=20, unique=True, editable=False)
    pdf = models.FileField(upload_to='student_booking_pdfs/', blank=True, null=True)
    type = models.CharField(max_length=50, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Auto-fill student_name and email if not provided
        if self.student and not self.student_name:
            self.student_name = f"{self.student.firstname} {self.student.lastname}".strip()
        if self.student and not self.email:
            self.email = self.student.email

        # Generate a unique booking_id if not already set
        if not self.booking_id:
            self.booking_id = self.generate_unique_booking_id()

        super().save(*args, **kwargs)

    def generate_unique_booking_id(self):
        while True:
            new_id = f"BOOK-{get_random_string(8).upper()}"
            if not StudentBooking.objects.filter(booking_id=new_id).exists():
                return new_id

    def __str__(self):
        return f"{self.student_name} - {self.booking_id}"

