from django.urls import path

from rest_framework.urlpatterns import format_suffix_patterns

from jobs import views


urlpatterns = [
    path(r'rtmp', views.RTMPJobView.as_view()),
    path(r'jobs/<int:pk>/', views.JobsView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
