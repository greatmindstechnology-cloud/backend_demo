from rest_framework import serializers
from trainer_gmt.models import Topic,QuizQuestion

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = '__all__'


class QuizQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQuestion
        fields = '__all__'

# serializers.py
from rest_framework import serializers
from .models import StudentBooking

class StudentBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentBooking
        fields = '__all__'
        read_only_fields = ['student_name', 'email', 'booking_id']
