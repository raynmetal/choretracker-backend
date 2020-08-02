from django.urls import path, include

from tracker.views import (RegistrationAPIView, LoginAPIView,
    UserRetrieveUpdateAPIView, HomePageView, SpaceListView)

app_name = 'tracker'

api_urlpatterns = [
    path('users/register/', RegistrationAPIView.as_view()),
    path('users/login/', LoginAPIView.as_view()),
    path('user/', UserRetrieveUpdateAPIView.as_view()),
    
    path('space/', SpaceListView.as_view()),
    path('space/<int:parent>/', SpaceListView.as_view())
]


urlpatterns = [
    path('api/', include(api_urlpatterns)),
    path('', HomePageView.as_view()),
]
