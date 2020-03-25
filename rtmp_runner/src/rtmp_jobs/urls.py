from django.urls import path

from rest_framework.urlpatterns import format_suffix_patterns

from rtmp_jobs import views


urlpatterns = [
    path(r'rtmpjobs', views.RTMPJobList.as_view()),
    path(r'rtmpjobs/<int:pk>', views.RTMPJobDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
