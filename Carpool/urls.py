from django.conf.urls import include, url
from django.contrib import admin
import app
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^app/', include('app.urls')),
    url(r'^$', app.views.IndexView.as_view()),
]

