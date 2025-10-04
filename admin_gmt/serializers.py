# serializers.py

from rest_framework import serializers
from .models import InstitutionData

class InstitutionDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionData
        fields = '__all__'
