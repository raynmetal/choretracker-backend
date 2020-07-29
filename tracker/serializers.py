from django.contrib.auth import authenticate 

from rest_framework import serializers 

from tracker.models import User, Space, Chore

# Serializes User
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta:
        model = User
        fields = ('email', 'password', 'token')

        read_only_fields = ('token',)
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for (key, value) in validated_data.items():
            setattr(instance, key, value)
        
        if password is not None:
            instance.set_password(password)
    
        instance.save()

        return instance


# Serializes login requests
class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        """
        Make sure that current instance is valid by matching 
        provided email and password with the one present in our
        database
        """
        email = data.get('email', None)
        password = data.get('password', None)

        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in'
            )
        
        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )
        
        # Pass email as username field for same reason we set 
        # USERNAME_FIELD to 'email'
        user = authenticate(username=email, password=password)

        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password was not found'
            )
        
        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )
        

        # 'validate' method should return a dictionary of valid data
        return {
            'email': user.email,
            'token': user.token
        }


# Serializes registration requests
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
