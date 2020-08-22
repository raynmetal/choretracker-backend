from django.urls import path, include

from tracker.views import (RegistrationAPIView, LoginAPIView,
    UserRetrieveUpdateAPIView, HomePageView, SpaceListView,
    ChoreListView, MemberListView, RequestView, AcceptRequestView)

app_name = 'tracker'

api_urlpatterns = [
    path('user/register/', RegistrationAPIView.as_view(), name='register'),
    path('user/login/', LoginAPIView.as_view(), name='login'),
    path('user/', UserRetrieveUpdateAPIView.as_view(), name='user'),
    
    path('space/', SpaceListView.as_view(), name='rootspaces'),
    path('space/<int:parent>/subspaces/', SpaceListView.as_view(), name='spaces'),
    
    path('space/<int:space>/members/', MemberListView.as_view(), name='members'),
    
    path('requests/', RequestView.as_view(), name='requests'),
    path('space/<int:space_id>/request/create/', RequestView.as_view(), name='createrequest'),
    path('requests/accept/', AcceptRequestView.as_view(), name='acceptrequest'),

    path('chore/', ChoreListView.as_view(), name='userchores'),
    path('space/<int:parent_space>/chores', ChoreListView.as_view(), name='spacechores'),
]


urlpatterns = [
    path('api/', include(api_urlpatterns)),
    path('', HomePageView.as_view()),
]
