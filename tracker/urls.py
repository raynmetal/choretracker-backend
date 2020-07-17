from django.urls import path 

from tracker.views import (RegistrationAPIView, LoginAPIView)

app_name = 'tracker'
urlpatterns = [
    path('users/register/', RegistrationAPIView.as_view()),
    path('users/login/', LoginAPIView.as_view())
]