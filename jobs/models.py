from django.db import models

class Job(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    industry = models.CharField(max_length=50)  # Ngành nghề (VD: lập trình, kinh doanh,...)

    def __str__(self):
        return self.title
