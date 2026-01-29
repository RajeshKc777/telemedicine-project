from django.db import models

class Hospital(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    contact_email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    website = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
