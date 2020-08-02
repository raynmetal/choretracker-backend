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


# Serializes root spaces 
class RootSpaceSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50, required=True)
    id = serializers.IntegerField(allow_null=True, read_only=True)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        return instance
    def create(self, validated_data):
        name = validated_data.get('name')
        creator = validated_data.get('creator')

        space = Space.objects.create(name=name)
        space.members.add(creator)
        
        return space


# Serializes child spaces
class SpaceSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50, required=True)
    full_name = serializers.CharField(max_length=600, read_only=True)
    id = serializers.IntegerField(allow_null=True, read_only=True)
    parent_id = serializers.IntegerField(allow_null=True)

    def update(self, instance, validated_data):
        parent_id = validated_data.get('parent_id', instance.parent.pk)

        instance.name = validated_data.get('name', instance.name)

        # Change this space's parent(eg., when changing this space's
        # position on the tree)
        instance.parent = Space.objects.get(pk=parent_id)
        return instance
    
    def create(self, validated_data):
        parent_id = validated_data.get('parent_id', None)

        name = validated_data.get('name', None)
        parent = Space.objects.get(pk=parent_id)

        if not parent:
            #TODO: add method to handle failure to retrieve space's parent
            pass
        space = Space.objects.create(name=name, parent=parent)
        space.initialize_members_from_parent_space()       
        return space

