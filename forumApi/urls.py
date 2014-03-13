from django.conf.urls import patterns, url

from forumApi import views

urlpatterns = patterns('',
    # url(r'^$', views.new_questions, name='index')
    url(r'^$', views.index),
)