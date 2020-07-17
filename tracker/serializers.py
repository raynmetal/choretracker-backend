from tracker.models import User 
from rest_framework import serializers

class RegisterUserSerializer(serializers.ModelSerializer):
    """Serializes registration requests and creates a new user."""
    
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True # client cannot read password 
    )

    # read_only=True prevents client from sending us tokens 
    token = serializers.CharField(max_length=255, read_only=True) 

    class Meta:
        model = User 
        fields = ['email', 'password', 'token']
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

