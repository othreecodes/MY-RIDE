from django.contrib import admin
from .models import *
# Register your models he
reg = admin.site.register

reg(TextBroadcast)
reg(ImageBroadcast)
reg(DirectionBroadcast)
reg(RideBroadcast)
reg(Comment)
reg(Like)
reg(Broadcast)
