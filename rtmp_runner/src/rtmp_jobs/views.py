from datetime import datetime

from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rtmp_jobs.models import RTMPJob
from rtmp_jobs.serializers import RTMPJobSerializer
from rtmp_jobs.rtmp_process_manager import stop_rtmp_output, start_rtmp_output


class RTMPJobList(APIView):
    def get(self, request, format=None):
        rtmp_jobs = RTMPJob.objects.all()
        serializer = RTMPJobSerializer(rtmp_jobs, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = RTMPJobSerializer(data=request.data)
        if serializer.is_valid():
            destination = request.data['destination']
            new_pid = start_rtmp_output('video', destination)
            serializer.save(pid=new_pid)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RTMPJobDetail(APIView):
    def get_object(self, pk):
        try:
            return RTMPJob.objects.get(pk=pk)
        except RTMPJob.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        rtmp_job = self.get_object(pk)
        serializer = RTMPJobSerializer(rtmp_job)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        rtmp_job = self.get_object(pk)
        serializer = RTMPJobSerializer(rtmp_job, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        rtmp_job = self.get_object(pk)
        rtmp_job_pid = RTMPJobSerializer(rtmp_job).data['pid']
        stop_rtmp_output(rtmp_job_pid)
        # TODO: get from same constants models is using
        rtmp_job.status = 'COMPLETED'
        rtmp_job.completed = datetime.now()
        rtmp_job.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
