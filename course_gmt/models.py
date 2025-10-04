from django.db import models
from datetime import timedelta
from signup_gmt.models import TrainerData,StudentInformation


class CourseTable(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    status = models.CharField(max_length=10,choices=STATUS_CHOICES,default='waiting')
    course_id = models.AutoField(primary_key=True)
    course_title = models.CharField(max_length=255)
    course_price = models.DecimalField(max_digits=10, decimal_places=2)
    course_description = models.TextField()
    course_rating = models.FloatField()
    about_course = models.TextField()
    total_students_enrolled = models.IntegerField(default=0,blank=True,null=True)
    course_specification = models.TextField()
    preknowledge = models.TextField(default=True)
    why_this_course = models.TextField(default=True)
    course_image = models.ImageField(upload_to='course_images/',blank=True, null=True)
    trainer = models.ForeignKey('signup_gmt.TrainerData', on_delete=models.SET_NULL, null=True)
    author_name= models.CharField(max_length=255,blank=True, null=True)
    created_date = models.DateField(blank=True, null=True)
    def __str__(self):
        return self.course_title




class Section(models.Model):
    course = models.ForeignKey('CourseTable', on_delete=models.CASCADE)
    section_title = models.CharField(max_length=255)
    order = models.IntegerField()

    def save(self, *args, **kwargs):
        if not self.pk:
            last_order = Section.objects.filter(course=self.course).aggregate(
                models.Max('order')
            )['order__max']
            self.order = (last_order or 0) + 1
        super().save(*args, **kwargs)


class Lecture(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    duration = models.DurationField()
    completed = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    order = models.IntegerField()
    video_file = models.FileField(upload_to='course_videos/', blank=True, null=True)
    pdf=models.FileField(upload_to='course_pdf/',blank=True,null=True)
    ppt=models.FileField(upload_to='course_ppt/',blank=True,null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            last_order = Lecture.objects.filter(section=self.section).aggregate(
                models.Max('order')
            )['order__max']
            self.order = (last_order or 0) + 1
        super().save(*args, **kwargs)

class CourseFeedback(models.Model):
    course = models.ForeignKey('CourseTable', on_delete=models.CASCADE, related_name='feedbacks')

    overall_rating = models.IntegerField()
    content_quality_rating = models.IntegerField()
    trainer_rating = models.IntegerField()
    platform_rating = models.IntegerField()
    course_difficulty = models.CharField(max_length=100)

    what_do_you_like_most = models.TextField(blank=True, null=True)
    what_do_you_like_least = models.TextField(blank=True, null=True)
    suggestions = models.TextField(blank=True, null=True)

    submitted_at = models.DateTimeField(auto_now_add=True)



class ProjectTable(models.Model):
    project_id = models.AutoField(primary_key=True)
    description = models.TextField()
    domain = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    pdf = models.FileField(upload_to='project_pdfs/', blank=True, null=True)
    most_usage = models.CharField(max_length=100)
    
    # Foreign Keys
    course = models.ForeignKey(CourseTable, on_delete=models.CASCADE, related_name='projects')
    trainer = models.ForeignKey(TrainerData, on_delete=models.CASCADE, related_name='projects')

    def __str__(self):
        return f"{self.project_id} - {self.domain}"



class Project(models.Model):
    course = models.ForeignKey(CourseTable,on_delete=models.CASCADE,related_name="assignments") 
    title = models.CharField(max_length=255)
    description = models.TextField()
    tags = models.JSONField(default=list, blank=True)  # stores list of tags
    pdf = models.FileField(upload_to="assignments_pdfs/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.course.course_title})"

class Project_submit(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="student_projects")
    student = models.ForeignKey(StudentInformation, on_delete=models.CASCADE, related_name="student_projects")
    project_file = models.FileField(upload_to='student_projects/files/')
    project_document = models.FileField(upload_to='student_projects/documents/')
    submitted_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)      

    class Meta:
        unique_together = ('project', 'student')  

    def __str__(self):
        return f"{self.student.firstname} - {self.project.project_id}"

class TaskTable(models.Model):
    task_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(CourseTable, on_delete=models.CASCADE, related_name="tasks")
    task_title = models.CharField(max_length=255)
    task_description = models.TextField()
    task_pdf = models.FileField(upload_to='course_tasks/')
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)      

    def __str__(self):
        return f"{self.task_title} ({self.course.course_title})"

class TaskSubmit(models.Model):
    id = models.AutoField(primary_key=True)
    task = models.ForeignKey(TaskTable, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(StudentInformation, on_delete=models.CASCADE, related_name="task_submissions")
    document = models.FileField(upload_to='task_submissions/')
    comments = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('task', 'student')

    def __str__(self):
        return f"{self.student.firstname} - {self.task.task_title}"

class StudentCourse(models.Model):
    student = models.ForeignKey(StudentInformation, on_delete=models.CASCADE)
    course = models.ForeignKey(CourseTable, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "course")  # prevent duplicate entries

    def __str__(self):
        return f"{self.student.id} - {self.course.course_title}"
