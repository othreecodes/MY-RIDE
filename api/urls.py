from django.conf.urls import include, url
from . import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [


    url(r'^users/$',views.UserList.as_view(), name='users'),

    url(r'^login/$',views.process_login, name='api_login'),

    url(r'^broadcasts/$',views.BroadcastList.as_view(), name='broadcasts'),
    url(r'^messages/$',views.MessageList.as_view(), name='messages'),
    url(r'^get_user/$',views.UserDetail.as_view(), name='user'),
    url(r'^getdashboard/$',views.DashStuff.as_view(), name='dashstuff'),
    url(r'^addride/$',views.addride, name='addride'),
    url(r'^userrides/$',views.UserVehicles.as_view(), name='userride'),
    url(r'^usershared/$',views.UserSharedVehicles.as_view(), name='usershared'),
    url(r'^requests/$',views.Requests.as_view(), name='requests'),



    # url(r'^upload/$',views.upload_file,name='upload'),
]

urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls'))
]

urlpatterns = format_suffix_patterns(urlpatterns)
