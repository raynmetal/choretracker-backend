from django.urls import path 

from tracker.views import RegistrationAPIView 

app_name = 'tracker'
urlpatterns = [
    path('users/', RegistrationAPIView.as_view())
]