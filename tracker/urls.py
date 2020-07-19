from django.urls import path 

from tracker.views import (RegistrationAPIView, LoginAPIView,
    UserRetrieveUpdateAPIView, ChoreListAPIView)

app_name = 'tracker'
urlpatterns = [
    path('users/register/', RegistrationAPIView.as_view()),
    path('users/login/', LoginAPIView.as_view()),
    path('user/', UserRetrieveUpdateAPIView.as_view()),
    path('spaces/<int:space_pk>/chores/', ChoreListAPIView.as_view()),
    path('user/chores/', ChoreListAPIView.as_view()),
]