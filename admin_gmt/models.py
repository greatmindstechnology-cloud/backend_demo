from django.db import models


class InstitutionData(models.Model):
    name = models.CharField(max_length=255)
    type_of_institution = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    street = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)
    contact_email = models.EmailField()

    def __str__(self):
        return self.name
  
