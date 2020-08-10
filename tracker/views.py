import jwt
from django.shortcuts import render
from django.views.generic import TemplateView

from rest_framework import status 
from rest_framework.permissions import AllowAny, IsAuthenticated, DjangoModelPermissions
from rest_framework.response import Response 
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView, ListCreateAPIView
from rest_framework.renderers import JSONRenderer 


from tracker.serializers import (
    RegistrationSerializer, LoginSerializer, UserSerializer,
    RootSpaceSerializer, SpaceSerializer, ChoreListSerializer,
    MemberSerializer, RequestSerializer)
from tracker.renderers import UserJSONRenderer
from tracker.models import Chore, Space, User, Request

class HomePageView(TemplateView):
    template_name = "index.html"


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer 

    def retrieve(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class RegistrationAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer 

    def post(self, request):
        user = request.data.get('user', {})

        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save() 

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})

        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status = status.HTTP_200_OK)


class SpaceListView(APIView):
    """
    List spaces user is a member of/list subspaces under 
    a space the user is a member of
    """
    #TODO: make access to space list contingent on authentication 
    #     and membership
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None, parent=None):
        user = request.user

        if not parent:
            spaces = Space.objects.filter(parent=None).filter(members=user)
            serializer = RootSpaceSerializer(spaces, many=True)
            return Response(serializer.data)
        
        space = Space.objects.get(pk=parent)
        # User must be a member of a space to get subspaces
        if not space.members.filter(pk=request.user.pk).count():
            return Response(None, status=status.HTTP_400_BAD_REQUEST)

        spaces = space.child.all()
        serializer = SpaceSerializer(spaces, many=True)
        return Response(serializer.data)

    def post(self, request, format=None, parent=None):
        new_space = request.data 

        # If no parent, create a root space
        if not parent:
            serializer = RootSpaceSerializer(data=new_space)
            if(serializer.is_valid()):
                serializer.save(creator=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Otherwise create space with parent parent_id
        # Parent in request data takes precedence over parent in url
        space = Space.objects.get(pk=parent)
        # User must be a member of a space to add a subspace
        if not space.members.filter(pk=request.user.pk).count():
            return Response(None, status=status.HTTP_400_BAD_REQUEST)
        
        new_space['parent_id'] = parent
        serializer = SpaceSerializer(data=new_space)
        if(serializer.is_valid()):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MemberListView(APIView):
    """
    List members of a space
    """

    permission_classes = (IsAuthenticated,)
    def get(self, request, space, format=None):
        user = request.user 
        space = Space.objects.get(pk=space)

        members = space.members.all()

        # user must be a member of this space to view other members
        if not members.filter(pk=request.user.pk).count():
            return Response(None, status=status.HTTP_400_BAD_REQUEST)
        serializer = MemberSerializer(members, many=True)
        return Response(serializer.data)


class ChoreListView(APIView):
    """
    List chores belonging to a space or a user 
    """

    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None, parent_space=None):
        user = request.user 

        if not parent_space:
            chores = Chore.objects.filter(users=user)
            serializer = ChoreListSerializer(chores, many=True)
            return Response(serializer.data)
    
        space = Space.objects.get(pk=parent_space)
        # User must be a member of a space to get chores
        if not space.members.filter(pk=request.user.pk).count():
            return Response(None, status=status.HTTP_400_BAD_REQUEST)

        chores = space.chores.all()
        serializer = ChoreListSerializer(chores, many=True)
        return Response(serializer.data)

    def post(self, request, parent_space, format=None):
        user = request.user
        new_chore = request.data 

        space = Space.objects.get(pk=parent_space)
        # User must be a member of a space to get chores
        if not space.members.filter(pk=request.user.pk).count():
            return Response(None, status=status.HTTP_400_BAD_REQUEST)
        
        new_chore['parent_space_id'] = parent_space 
        serializer = ChoreListSerializer(data=new_chore)
        if(serializer.is_valid()):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RequestView(APIView):
    """
    List chores received by a user, or create requests 
    """

    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):
        user = request.user 

        serializer = RequestSerializer(user.received_requests, many=True)
        return Response(serializer.data)
    
    def post(self, request, space_id, format=None):
        from_user = {'email': request.user.email}
        new_request = request.data
        new_request["space_id"] = space_id
        new_request["from_user"] = from_user
        print(new_request)
        
        serializer = RequestSerializer(data=new_request)
  
        if(serializer.is_valid()):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AcceptRequestView(APIView):
    """
    Adds user to the space associated with the request
    """

    permission_classes = (IsAuthenticated,)
    def post(self, request, format=None):
        user = request.user
        request_id = request.data.get('request_id')
        request_instance = Request.objects.get(pk=request_id)

        if(request_instance.to_user != user):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        request_instance.space.add_member(user)
        request_instance.space.assign_member_to_chores(user)

        request_instance.delete()

        return Response()


class UserCalendarView(APIView):
    # TODO: define calendar view
    pass


