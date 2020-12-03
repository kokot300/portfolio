from uuid import uuid1

from django.contrib.auth.models import User
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver


# Create your models here.

@receiver(pre_delete, sender=User)
def delete_user(sender, instance, **kwargs):
    su = User.objects.filter(is_superuser=True)
    if len(su) < 2:
        raise PermissionDenied


class UserActivation(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    activation = models.TextField(default=uuid1(), blank=True, null=True)


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
        return Institution.TYPE_CHOICES[int(self.type) - 1][1]


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
    is_taken = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.quantity} {self.categories} od {self.user}'
