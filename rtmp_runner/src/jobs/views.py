from datetime import datetime

from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from jobs.models import Job
from jobs.serializers import JobSerializer, RTMPJobRequestSerializer
from jobs.rtmp_process_manager import stop_rtmp_output, start_rtmp_output


class RTMPJobView(APIView):
    def post(self, request, format=None):
        serializer = RTMPJobRequestSerializer(data=request.data)
        if serializer.is_valid():
            destination = request.data['destination']
            new_pid = start_rtmp_output('video', destination)
            job = Job.objects.create(pid=new_pid)
            response_serializer = JobSerializer(job)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JobsView(APIView):
    def get_object(self, pk):
        try:
            return Job.objects.get(pk=pk)
        except Job.DoesNotExist:
            raise Http404

    def delete(self, request, pk, format=None):
        job = self.get_object(pk)
        stop_rtmp_output(pk)
        # TODO: get from same constants models is using
        job.status = 'COMPLETED'
        job.completed = datetime.now()
        job.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
