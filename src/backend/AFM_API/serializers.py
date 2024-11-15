from rest_framework import serializers
from .models import WaterLevel, Account


class WaterLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterLevel
        fields = ['location_id', 'value_at_time', 'unit', 'created_at']

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'username', 'email', 'created_at']
