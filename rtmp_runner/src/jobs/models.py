from django.db import models


TYPE_CHOICES = [
    ('RTMP', 'RTMP'),
    ('RTC', 'RTC')
]

STATUS_CHOICES = [
    ('RUNNING', 'Running'),
    ('PAUSED', 'paused'),
    ('COMPLETED', 'Completed'),
    ('ERROR', 'Error')
]


class Job(models.Model):
    pid = models.IntegerField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_CHOICES[0][0])
    destination = models.CharField(max_length=100)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    completed = models.DateTimeField(null=True)

    class Meta:
        ordering = ['-created']
