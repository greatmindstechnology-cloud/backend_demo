from rest_framework import serializers
from .models import LoginDetails, Role, StudentInformation, VendorData, TrainerData

class LoginDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginDetails
        fields = '__all__'

class StudentSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentInformation
        fields = '__all__'

class VendorSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorData
        fields = '__all__'

class TrainerSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainerData
        fields = '__all__'

class EmailOnlySerializer(serializers.Serializer):
    email = serializers.EmailField()
 