from __future__ import unicode_literals
import re

from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin,
                                        UserManager)
from django.core.mail import send_mail
from django.core import validators
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    A custom user class that basically mirrors Django's `AbstractUser` class
    and doesn't force `first_name` or `last_name` with sensibilities for
    international names.

    http://www.w3.org/International/questions/qa-personal-names
    """
    username = models.CharField(_('username'), max_length=30, unique=True,
                                help_text=_('Required. 30 characters or fewer. Letters, numbers and '
                                            '@/./+/-/_ characters'),
                                validators=[
                                    validators.RegexValidator(re.compile(
                                        '^[\w.@+-]+$'), _('Enter a valid username.'), 'invalid')
                                ])
    full_name = models.CharField(_('full name'), max_length=254, blank=False)
    short_name = models.CharField(_('short name'), max_length=30, blank=True)
    choices = (('Male','Male'),('Female','Female'))
    sex = models.CharField(_('sex'), max_length=30, blank=False, choices=choices)
    email = models.EmailField(_('email address'), max_length=254, unique=True)
    phone_number = models.CharField(_('phone number'), max_length=20, validators=[
                                    validators.RegexValidator(re.compile(
                                        '^[0-9]+$'), _('Only numbers are allowed.'), 'invalid')

                                ])
    user_choices = (('Driver', 'Driver'), ('Passenger', 'Passenger'))
    user_type = models.CharField(_('user type'), max_length=30, blank=False, choices=user_choices)
    address = models.TextField(_('address'),max_length=400,blank=False)

    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin '
                                               'site.'))
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __unicode__(self):
        return self.username

    def get_absolute_url(self):
        return "/app/user/%d/" % self.pk

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = self.full_name
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.short_name.strip()

    def get_sex(self):
        return self.sex

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])


class Vehicle(models.Model):

    year = models.IntegerField(_('year of purchase'), max_length=254, blank=False)
    make = models.CharField(_('vehicle make'), max_length=254, blank=False)
    model = models.CharField(_('vehicle model'), max_length=254, blank=False)
    seats = models.IntegerField(_('no of seats'), max_length=254, blank=True)
    user_choices = (('private', 'private'), ('hired', 'hired'))
    type = models.CharField(_('vehicle type'), max_length=30, blank=False, choices=user_choices)
    user_choices = (('Car', 'Car'), ('Bus', 'Bus'),  ('Coaster', 'Coaster'),  ('Truck', 'Truck'))
    category = models.CharField(_('vehicle category'), max_length=30, blank=False, choices=user_choices)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return "/app/ride/%d/view" % self.pk

    def __str__(self):
        return self.make+" "+self.model +" belonging to "+self.user.username


class VehicleSharing(models.Model):
    start = models.CharField(_('starting point'), max_length=256, blank=False,)
    dest = models.CharField(_('destination'), max_length=256, blank=False)
    cost = models.IntegerField(_('cost'), max_length=256, blank=False)
    date = models.DateField(_('date'), default=timezone.now)
    start_time = models.TimeField(_('start time'), max_length=256, blank=False)
    arrival_time = models.TimeField(_('starting point'), max_length=256, blank=False)
    no_pass = models.IntegerField(_('no of passengers'), max_length=256, blank=False)
    choices = (('Male', 'Male'), ('Female', 'Female'), ('Both', 'Both'))
    sex = models.CharField(_('gender preference'), max_length=30, blank=False, choices=choices)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)

    def __str__(self):
        return self.start+" to "+self.dest

    def get_user(self):
        return self.user

    def get_absolute_url(self):
        return "/app/sharing/%d/view" % self.pk


class Request(models.Model):
    pick = models.CharField(_('pick up point'), max_length=256, blank=False,)
    dest = models.CharField(_('destination'), max_length=256, blank=False)
    reg_date = models.DateTimeField(_('registration date'), default=timezone.now)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    bearable = models.IntegerField(_('bearable cost'), max_length=256, blank=False)
    status = models.CharField(_('status'), max_length=256, blank=False, default='pending')
    ride = models.ForeignKey(VehicleSharing, on_delete=models.CASCADE)

    def __str__(self):
        return "request from "+self.user.get_full_name()+" on "+self.reg_date.isoformat(' ')[0:16]

    def get_absolute_url(self):
        return "/app/request/%d/view" % self.pk












