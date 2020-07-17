from rest_framework import serializers 
from tracker.models import User 

class RegistrationSerializer(serializers.ModelSerializer):
    """Serializes registration requests, creates a new user."""

    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True, #makes it so that passwords can't be read by client
    )
    
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User 
        # List all of the fields  that could be included in a request
        # or response 
        fields = ['email', 'password', 'token']
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)