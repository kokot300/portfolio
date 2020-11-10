from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=127)

    def __str__(self):
        return self.name


class Institution(models.Model):
    TYPE_CHOICES = [
        (1, 'Fundacja'),
        (2, 'Organizacja pozarządowa'),
        (3, 'Zbiórka lokalna'),
    ]

    name = models.CharField(max_length=127)
    description = models.TextField()
    type = models.CharField(choices=TYPE_CHOICES, default=1, max_length=63)
    categories = models.ManyToManyField(to='Category')

    def __str__(self):
        return self.name

    def type_verbose(self):
        return Institution.TYPE_CHOICES[int(self.type)][1]


class Donation(models.Model):
    quantity = models.IntegerField()
    categories = models.ManyToManyField(to='Category')
    institution = models.ForeignKey(to=Institution, on_delete=models.CASCADE)
    address = models.TextField()
    phone_number = models.IntegerField()
    city = models.CharField(max_length=127)
    zip_code = models.IntegerField()
    pick_up_date = models.DateField()
    pick_up_time = models.TimeField()
    pick_up_comment = models.TextField()
    user = models.ForeignKey(to=User, null=True, default=None, on_delete=models.CASCADE)
