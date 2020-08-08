from django.urls import path, include

from tracker.views import (RegistrationAPIView, LoginAPIView,
    UserRetrieveUpdateAPIView, HomePageView, SpaceListView,
    ChoreListView, MemberListView)

app_name = 'tracker'

api_urlpatterns = [
    path('user/register/', RegistrationAPIView.as_view()),
    path('user/login/', LoginAPIView.as_view()),
    path('user/', UserRetrieveUpdateAPIView.as_view()),
    
    path('space/', SpaceListView.as_view()),
    path('space/<int:parent>/subspaces', SpaceListView.as_view()),
    
    path('space/<int:space>/members', MemberListView.as_view()),
    
    path('chore/', ChoreListView.as_view()),
    path('space/<int:parent_space>/chores', ChoreListView.as_view())
]


urlpatterns = [
    path('api/', include(api_urlpatterns)),
    path('', HomePageView.as_view()),
]
