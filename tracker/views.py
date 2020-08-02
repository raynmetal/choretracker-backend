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
    RootSpaceSerializer, SpaceSerializer
    )
from tracker.renderers import UserJSONRenderer
from tracker.models import Chore, Space, User

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
    def get(self, request, format=None, parent=None):
        user = request.user
        if not parent:
            spaces = Space.objects.filter(parent=None)
            serializer = RootSpaceSerializer(spaces, many=True)
            return Response(serializer.data)
        spaces = Space.objects.filter(parent=parent)
        serializer = SpaceSerializer(spaces, many=True)
        return Response(serializer.data)

    def post(self, request, format=None, parent=None):
        new_space = request.data 

        if not parent:
            serializer = RootSpaceSerializer(data=new_space)
            if(serializer.is_valid()):
                serializer.save(creator=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        new_space['parent_id'] = parent
        serializer = SpaceSerializer(data=new_space)
        if(serializer.is_valid()):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
