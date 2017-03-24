from django.conf.urls import include, url
from django.contrib import admin
import app
from django.conf import settings
from django.conf.urls.static import static
import notifications.urls
from os import path

urlpatterns = [
    url(r'^admin/', include('smuggler.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^app/', include('app.urls')),
    url(r'^api/', include('api.urls')),
    url(r'^broadcast/', include('broadcast.urls')),
    url(r'^$', app.views.IndexView.as_view()),
    url('^inbox/notifications/', include(notifications.urls, namespace='notifications')),
    url('', include('app.urls')),

]


urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)


