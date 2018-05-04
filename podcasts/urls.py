from django.conf import settings
from django.urls import include, path
from . import views

app_name = 'podcasts'


podcasts_patterns = [
    path('', views.podcasts_list, name='podcasts-list'),
    path('discover', views.podcasts_discover, name='podcasts-discover'),
    path('new/', views.podcasts_new, name='podcasts-new'),
    path('<slug:slug>/', include([
        path('', views.podcasts_details, name='podcasts-details'),
        path('refresh/', views.podcasts_refresh_feed, name='podcasts-refresh-feed'),
    ]))
]

urlpatterns = [
    path('', views.index, name='index'),
    path('podcasts/', include(podcasts_patterns)),
]
