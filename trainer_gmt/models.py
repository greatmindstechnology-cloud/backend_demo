from django.db import models
from signup_gmt.models import TrainerData, StudentInformation,LoginDetails
from django.contrib.auth.models import User as AuthUser
from course_gmt.models import CourseTable


class Topic(models.Model):
    trainer = models.ForeignKey(TrainerData, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    duration = models.IntegerField(help_text="Duration in minutes")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class QuizQuestion(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField()
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    correct_option = models.IntegerField(choices=[(1, 'Option 1'), (2, 'Option 2'), (3, 'Option 3'), (4, 'Option 4')])
    explanation = models.TextField(blank=True, null=True)
    marks = models.IntegerField(default=1)
    difficulty = models.CharField(
        max_length=10,
        choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')],
        default='medium'
    )

    def __str__(self):
        return self.question


class StudentResponse(models.Model):
    student = models.ForeignKey(StudentInformation, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    
    selected_option = models.IntegerField(choices=[(1, 'Option 1'), (2, 'Option 2'), (3, 'Option 3'), (4, 'Option 4')])
    is_correct = models.BooleanField()
    marks_obtained = models.IntegerField(default=0)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'question')  # Prevent multiple submissions

    def __str__(self):
        return f"{self.student.username} - Q{self.question.id}"

class StudentResult(models.Model):
    student = models.ForeignKey(StudentInformation, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)

    total_score = models.IntegerField()
    grade = models.CharField(max_length=5)
    completed_at = models.DateTimeField(auto_now_add=True)
    total_possible_marks = models.FloatField(default=0)
    percentage = models.FloatField(default=0)

    class Meta:
        unique_together = ('student', 'topic')  # One result per student per quiz

    def __str__(self):
        return f"{self.student.username} - {self.topic.title} - {self.grade}"
    
class Assignment(models.Model):
    trainer = models.ForeignKey(TrainerData, on_delete=models.CASCADE)
    course = models.ForeignKey(CourseTable, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateField()
    max_marks = models.IntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class StudentAssignmentSubmission(models.Model):
    student = models.ForeignKey(StudentInformation, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    
    answer_text = models.TextField(blank=True, null=True)
    uploaded_file = models.FileField(upload_to='assignment_submissions/', blank=True, null=True)
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('student', 'assignment')  # Prevent resubmission

    def __str__(self):
        return f"{self.student.login.username} - {self.assignment.title}"

class AssignmentResult(models.Model):
    student = models.ForeignKey(StudentInformation, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    
    marks_obtained = models.FloatField()
    # max_marks = models.IntegerField(default=100)
    total_possible_marks = models.FloatField(default=0)
    percentage = models.FloatField()
    grade = models.CharField(max_length=5)
    evaluated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'assignment')

    def __str__(self):
        return f"{self.student.login.username} - {self.assignment.title} - {self.grade}"





class CounselorApplication(models.Model):
    trainer = models.ForeignKey(TrainerData, on_delete=models.CASCADE)  # For trainers; add vendor FK if separate model exists
    domains = models.JSONField()  # List of strings, e.g., ["Technical", "HR"]
    why_interested = models.TextField()
    availability = models.JSONField()  # Dict, e.g., {"monday": ["10:00-12:00", "14:00-16:00"]}
    uploaded_docs = models.JSONField(default=list)  # List of file paths/URLs
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')],
        default='Pending'
    )
    admin_comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Application {self.id} by {self.trainer}"
    
class Counselor(models.Model):
    user = models.ForeignKey(LoginDetails, on_delete=models.CASCADE)
    approved_domains = models.JSONField()
    rating = models.FloatField(default=0.0)
    total_sessions = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Counselor {self.user.username}"   # if LoginDetails has username field




# trainer_gmt/models.py

from django.db import models
from signup_gmt.models import TrainerData, StudentInformation
from django.contrib.auth.models import User as AuthUser
from course_gmt.models import CourseTable

# tra# trainer_gmt/models.py
from django.db import models
from signup_gmt.models import StudentInformation
from .models import Counselor

class CounselingRequest(models.Model):
    student = models.ForeignKey(StudentInformation, on_delete=models.CASCADE)
    counselor = models.ForeignKey(Counselor, on_delete=models.SET_NULL, null=True, blank=True)
    domain = models.CharField(max_length=100)
    description = models.TextField()
    preferred_times = models.JSONField()
    resume = models.FileField(upload_to='counseling_resumes/', null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Assigned', 'Assigned'), ('Accepted', 'Accepted'), ('Rejected', 'Rejected'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')],
        default='Pending'
    )
    session_time = models.DateTimeField(null=True, blank=True)
    meeting_id = models.CharField(max_length=100, blank=True, null=True)  # Renamed from google_calendar_event_id
    meet_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Request {self.id} by {self.student.login.username} for {self.domain}"

class CounselingFeedback(models.Model):
    request = models.ForeignKey(CounselingRequest, on_delete=models.CASCADE, related_name='feedback')
    rating = models.FloatField()
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)







from django.db import models
from django.db.models import JSONField
from signup_gmt.models import LoginDetails, TrainerData

class Interviewer(models.Model):
    user = models.ForeignKey(LoginDetails, on_delete=models.CASCADE)
    approved_domains = JSONField(default=list)
    rating = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Interviewer: {self.user.username}"

class InterviewerApplication(models.Model):
    trainer = models.ForeignKey(TrainerData, on_delete=models.CASCADE)
    domains = JSONField(default=list)
    why_interested = models.TextField(null=True, blank=True)
    availability = JSONField()
    docs = models.FileField(upload_to='interviewer_docs/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending')
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Application by {self.trainer.first_name} for {self.domains}"

class InterviewRequest(models.Model):
    student_id = models.IntegerField()
    interviewer = models.ForeignKey('Interviewer', on_delete=models.SET_NULL, null=True, blank=True)
    domain = models.CharField(max_length=100)
    description = models.TextField()
    preferred_times = JSONField()
    resume = models.FileField(upload_to='interview_resumes/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Assigned', 'Assigned'), ('Accepted', 'Accepted'), ('Rejected', 'Rejected'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], default='Pending')
    session_time = models.DateTimeField(null=True, blank=True)
    meeting_id = models.CharField(max_length=100, blank=True, null=True)
    meet_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Request {self.id} for {self.domain} by student_id {self.student_id}"

class InterviewFeedback(models.Model):
    request = models.ForeignKey(InterviewRequest, on_delete=models.CASCADE)
    rating = models.FloatField()
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for Request {self.request.id}"