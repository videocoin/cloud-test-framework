from rest_framework import serializers

from jobs.models import Job


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            'id', 'status'
        ]


class RTMPJobRequestSerializer(serializers.Serializer):
    destination = serializers.CharField(min_length=1, max_length=4096, required=True)

    class Meta:
        fields = [
            'destination'
        ]
