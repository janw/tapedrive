from django.conf import settings
from django.urls import include, path
from . import views

app_name = 'podcasts'
urlpatterns = [
    path('', views.index, name='index'),
    path('podcasts', views.podcasts_list, name='podcasts-list'),

]
