from django.urls import path 

from tracker.views import (RegistrationAPIView, LoginAPIView,
    UserRetrieveUpdateAPIView,)

app_name = 'tracker'
urlpatterns = [
    path('users/register/', RegistrationAPIView.as_view()),
    path('users/login/', LoginAPIView.as_view()),
    path('user/', UserRetrieveUpdateAPIView.as_view()),
]