from django.urls import path, include

urlpatterns = [
    path('', include('rtmp_jobs.urls'))
]
