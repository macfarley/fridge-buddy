from django.db import models
from django.urls import reverse

class Food(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    date_bought = models.DateField
    expiration = models.DateField
    spoiled = models.BooleanField

    

    def __str__(self):
        return self.name
        # Define a method to get the URL for this particular food instance
    def get_absolute_url(self):
        # Use the 'reverse' function to dynamically find the URL for viewing this food's details
        return reverse('cat-detail', kwargs={'food_id': self.id})
