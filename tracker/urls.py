from django.urls import path
from tracker import views 
from rest_framework.urlpatterns import format_suffix_patterns

# Add url patterns to the list below 
app_name = 'tracker'
urlpatterns = [
    path('api/users/', views.RegistrationAPIView.as_view()),
    path('', views.index),
]

urlpatterns = format_suffix_patterns(urlpatterns)

