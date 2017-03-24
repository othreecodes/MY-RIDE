from django.db import models
from django.conf import *
from django.utils import timezone
from model_utils.managers import InheritanceManager
from django.utils.translation import ugettext_lazy as _

# Create your models here.

class Broadcast(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='%(app_label)s_%(class)s_related')
    date = models.DateField(_('broadcast date'),default=timezone.now)
    time = models.TimeField(_('time'),default=timezone.now)
    send_to_all = models.BooleanField(_('send to all'),default=False)
    bc_from = models.ForeignKey(settings.AUTH_USER_MODEL,blank=True,default=None, null=True,on_delete=models.CASCADE, related_name='bcfrom')
    bc_time = models.TimeField(_('rebc time'),default=timezone.now)
    bc_date = models.DateField(_('rebc date'),default=timezone.now)
    
    objects = InheritanceManager()


    def liked(self):
        num = Like.objects.filter(broadcast_message=self).values_list('liker')

        result = []
        for liker in num:
            print(liker)
            user = liker[0]
            result.append(user)

        return result

    def get_absolute_url(self):
        return '/broadcast/%d/view/' % self.pk


class TextBroadcast(Broadcast):
    message = models.TextField()


class ImageBroadcast(Broadcast):
    image = models.ImageField()
    description = models.TextField()


class RideBroadcast(Broadcast):
    source = models.CharField(_('source'),max_length=256)
    dest = models.CharField(_('destination'),max_length=256)
    date_needed = models.DateField(_('date needed'),default=timezone.now)


class DirectionBroadcast(Broadcast):
    location = models.TextField(_('current Location'))
    destination = models.TextField(_('destination'))
    additional_info = models.TextField(_('additional information'))



class Comment(models.Model):

    commenter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='commenter')
    broadcast_message = models.ForeignKey(Broadcast,on_delete=models.CASCADE,related_name='broadcast_comment')
    comment = models.TextField(_('comment'),blank=False)
    date = models.DateField(_('date'),default=timezone.now)
    time = models.TimeField(_('time'),default=timezone.now)




class Like(models.Model):
    liker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='liker')
    broadcast_message = models.ForeignKey(Broadcast, on_delete=models.CASCADE,related_name='broadcast_like')
    date = models.DateField(_('date'), default=timezone.now)
    time = models.TimeField(_('time'), default=timezone.now)




















