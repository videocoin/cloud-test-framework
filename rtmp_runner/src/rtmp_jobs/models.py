from django.db import models
# from datetime import datetime
SOURCE_CHOICES = [
	('FILE', 'File'), ('SCREEN', 'Screen')]

STATUS_CHOICES = [
	('RUNNING', 'Running'), ('PAUSED', 'paused'), 
	('COMPLETED', 'Completed'), ('ERROR', 'Error')]


class RTMPJob(models.Model):	
    pid = models.IntegerField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    creator = models.CharField(max_length=100, blank=True, default='')
    description = models.TextField(blank=True)
    source = models.CharField(max_length=100, choices=SOURCE_CHOICES, default=SOURCE_CHOICES[0][0])
    loop = models.BooleanField(default=True) 
    destination = models.CharField(max_length=100)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    completed = models.DateTimeField(null=True)

    class Meta:
        ordering = ['created']
