from django.contrib.auth import authenticate 

from rest_framework import serializers 

from tracker.models import (User, Space, Chore, Request,
                            UserSpace, UserChore)

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

class UserEmailSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['email']
        model = User


# Serializes login requests
class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True, max_length=255)
    password = serializers.CharField(required=True, max_length=128, write_only=True)
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

class UserSpaceSerializer(serializers.ModelSerializer):
    user = UserEmailSerializer(read_only=True)
    class Meta:
        model = UserSpace
        fields = ['available', 'user']

class RootSpaceSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=50, required=True)
    id = serializers.IntegerField(allow_null=True, read_only=True)
    userspaces = UserSpaceSerializer(many=True)

    class Meta:
        fields = ['name', 'id', 'userspaces']
        model = Space
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
class SpaceSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=50, required=True)
    full_name = serializers.CharField(max_length=600, read_only=True)
    id = serializers.IntegerField(allow_null=True, read_only=True)
    parent_id = serializers.IntegerField(allow_null=True)
    
    userspaces = UserSpaceSerializer(many=True)

    class Meta:
        fields = ['name', 'id', 'userspaces']
        model = Space

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

# Serializes list of chores
class ChoreListSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50, required=True)
    parent_space_id = serializers.IntegerField(required=True)
    interval = serializers.IntegerField(required=False)
    id = serializers.IntegerField(read_only=True)

    next_date = serializers.DateField(read_only=True)
    last_date = serializers.DateField(read_only=True)

    next_user = UserEmailSerializer(read_only=True)
    last_user = UserEmailSerializer(read_only=True)

    def update(self, instance, validated_data):
        parent_space_id = validated_data.get('parent_id', instance.parent_space.pk)
        instance.name = validated_data.get('name', instance.name)
        instance.interval = validated_data.get('interval', instance.interval)
        instance.parent = Space.objects.get(pk=parent_space_id)
        
        instance.get_next_user()

        instance.refresh_from_db()
        return instance

    def create(self, validated_data):
        parent_space_id = validated_data.get('parent_space_id')
        name = validated_data.get('name')
        interval = validated_data.get('interval')
        parent_space = Space.objects.get(pk=parent_space_id)
        
        instance = None
        if(interval): instance = Chore.objects.create(name=name, interval=interval, parent_space=parent_space)
        else: instance = Chore.objects.create(name=name, parent_space=parent_space)
        instance._initialize_users()
        instance.get_next_user()

        instance.refresh_from_db()
        return instance

class RequestSerializer(serializers.Serializer):
    from_user = UserEmailSerializer(required=True)
    to_user = UserEmailSerializer(required=True)
    space_id = serializers.IntegerField(required=True)
    id = serializers.IntegerField(read_only=True) 

    created_date = serializers.DateField(read_only=True)

    def create(self, validated_data):
        space_id = validated_data.get('space_id')
        from_user = validated_data.get('from_user')
        to_user = validated_data.get('to_user')

        from_user = User.objects.get(email=from_user["email"])
        to_user = User.objects.get(email=to_user["email"])
        space = Space.objects.get(pk=space_id)

        return Request.objects.create(from_user=from_user, to_user=to_user, space=space)

class UserCalendarSerializer(serializers.Serializer):
    #TODO: define calendar serializer
    pass

class UserChoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserChore 
        fields = ['user', 'vwork', '']