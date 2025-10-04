
from rest_framework import serializers
from .models import CourseFeedback, Project,Project_submit,TaskTable,TaskSubmit,StudentCourse,CourseTable

class CourseFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseFeedback
        fields = [
            'id', 'course', 'overall_rating', 'content_quality_rating',
            'trainer_rating', 'platform_rating', 'course_difficulty',
            'what_do_you_like_most', 'what_do_you_like_least',
            'suggestions', 'submitted_at'
        ]
        read_only_fields = ['id', 'submitted_at']

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

class Project_submit_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Project_submit
        fields = '__all__'



class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskTable
        fields = "__all__"


class TaskSubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskSubmit
        fields = "__all__"



class StudentCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCourse
        fields = "__all__"


class CourseTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseTable
        fields = "__all__"
