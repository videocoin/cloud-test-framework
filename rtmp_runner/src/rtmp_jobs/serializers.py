from rest_framework import serializers
from rtmp_jobs.models import RTMPJob

class RTMPJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = RTMPJob
        fields = ['id', 'pid', 'created', 'creator', 'description', 'source',
        	'loop', 'destination', 'status']
