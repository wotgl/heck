from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^set_access_token/$', views.set_access_token),
    url(r'^get_comments/$', views.get_comments),
]