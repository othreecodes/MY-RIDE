from django.conf.urls import include, url
from broadcast import views

app_name = 'broadcast'
urlpatterns = [
    url(r'^upload/text/$', views.upload_text, name='upload_text'),
    url(r'^upload/image/$', views.upload_image, name='upload_image'),
    url(r'^upload/ride/$', views.upload_ride, name='upload_ride'),
    url(r'^upload/direction/$', views.upload_direction, name='upload_direction'),
    url(r'^$',views.index,name='index'),
    url(r'^like/(?P<broadcast_id>[0-9]+)/$', views.like_broadcast, name='like_broadcast'),
    url(r'^rebc/(?P<bc_id>[0-9]+)/$', views.rebc, name='rebc'),
    url(r'^(?P<bc_id>[0-9]+)/view/$', views.broadcast_view, name='view'),
    url(r'^comment/(?P<broadcast_id>[0-9]+)/$', views.comment, name='comment'),

]