from rest_framework import serializers
from course_gmt.models import CourseTable, Section, Lecture
from .models import Assignment,StudentAssignmentSubmission,AssignmentResult,CounselorApplication, Counselor,CounselingRequest, CounselingFeedback

from signup_gmt.models import TrainerData, StudentInformation



# class LectureSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Lecture
#         fields = ['title','duration','active','video_file']
        # read_only_fields = ['order', 'completed', 'active']

class SectionSerializer(serializers.ModelSerializer):
    # lectures = LectureSerializer(many=True, read_only=True)
    
    class Meta:
        model = Section
        fields = [ 'section_title'] 
         
        # read_only_fields = ['order']

class TrainerCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseTable
        fields = [
            'course_title', 'course_price', 'course_description', 'course_rating',
            'about_course', 'course_specification',
            'preknowledge', 'why_this_course', 'course_image','author_name','created_date'
        ]
        # read_only_fields = ['total_students_enrolled', 'status']




class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'



class StudentAssignmentSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.login.username', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)

    class Meta:
        model = StudentAssignmentSubmission
        fields = '__all__'  # or list fields explicitly if you prefer


class AssignmentResultSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.login.username', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)

    class Meta:
        model = AssignmentResult
        fields = '__all__'


class CounselorApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CounselorApplication
        fields = '__all__'


class CounselorApplicationSerializer(serializers.ModelSerializer):
    trainer_name = serializers.CharField(source='trainer.first_name', read_only=True)
    trainer_email = serializers.CharField(source='trainer.login.email', read_only=True)

    class Meta:
        model = CounselorApplication
        fields = ['id', 'trainer', 'trainer_name', 'trainer_email', 'domains', 'why_interested', 'availability', 'uploaded_docs', 'status', 'admin_comments', 'created_at', 'updated_at']



# trainer_gmt/serializers.py



class CounselorSerializer(serializers.ModelSerializer):
    availability = serializers.SerializerMethodField()

    class Meta:
        model = Counselor
        fields = ['id', 'user', 'approved_domains', 'availability', 'rating', 'total_sessions', 'created_at']

    def get_availability(self, obj):
        latest_application = CounselorApplication.objects.filter(
            trainer__login=obj.user, status='Approved'
        ).order_by('-updated_at').first()
        return latest_application.availability if latest_application else {}

class CounselingRequestSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.login.username', read_only=True)
    counselor_name = serializers.CharField(source='counselor.user.username', read_only=True)
    resume_url = serializers.SerializerMethodField()

    class Meta:
        model = CounselingRequest
        fields = [
            'id', 'student', 'student_name', 'counselor', 'counselor_name',
            'domain', 'description', 'preferred_times', 'resume_url',
            'status', 'created_at', 'updated_at', 'session_time',
            'meet_link', 'meeting_id'
        ]

    def get_resume_url(self, obj):
        return obj.resume.url if obj.resume else None

    
      
class CounselingFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = CounselingFeedback
        fields = ['id', 'request', 'rating', 'comments', 'created_at']
        read_only_fields = ['created_at']



from rest_framework import serializers
from .models import InterviewerApplication, InterviewRequest, InterviewFeedback
from signup_gmt.models import StudentInformation

class InterviewerApplicationSerializer(serializers.ModelSerializer):
    trainer_name = serializers.CharField(source='trainer.first_name', read_only=True)
    class Meta:
        model = InterviewerApplication
        fields = ['id', 'trainer', 'trainer_name', 'domains', 'why_interested', 'availability', 'docs', 'status', 'comments', 'created_at', 'updated_at']
        read_only_fields = ['id', 'trainer_name', 'created_at', 'updated_at']

class InterviewRequestSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    interviewer_name = serializers.CharField(source='interviewer.user.username', read_only=True, allow_null=True)
    resume_url = serializers.SerializerMethodField()

    class Meta:
        model = InterviewRequest
        fields = ['id', 'student_id', 'student_name', 'interviewer', 'interviewer_name', 'domain', 'description', 'preferred_times', 'resume_url', 'status', 'session_time', 'meet_link', 'meeting_id', 'created_at', 'updated_at']
        read_only_fields = ['id', 'student_name', 'interviewer_name', 'resume_url', 'status', 'session_time', 'meet_link', 'meeting_id', 'created_at', 'updated_at']

    def get_student_name(self, obj):
        try:
            student = StudentInformation.objects.get(id=obj.student_id)
            return student.login.username
        except StudentInformation.DoesNotExist:
            return None

    def get_resume_url(self, obj):
        return obj.resume.url if obj.resume and obj.resume.name else None

class InterviewFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewFeedback
        fields = ['id', 'request', 'rating', 'comments', 'created_at']