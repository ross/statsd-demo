from django.db import models


class Employee(models.Model):
    email = models.EmailField(max_length=255, primary_key=True)
    name = models.CharField(max_length=64)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created',)
