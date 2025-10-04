
from rest_framework import serializers
from .models import CSREvent,BloodNeed

class CSREventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CSREvent
        fields = "__all__"

class BloodNeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodNeed
        fields = "__all__"
