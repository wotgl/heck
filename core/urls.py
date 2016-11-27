from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^set_access_token/$', views.set_access_token),
    url(r'^get_comments/$', views.get_comments),
    url(r'^redirect/$', views.redirect),
    url(r'^get_comments_admin/$', views.get_comments_admin),
    url(r'^ban_user/$', views.ban_user),
    url(r'^fetch_result/$', views.fetch_result),
]