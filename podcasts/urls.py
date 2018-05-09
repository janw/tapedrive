from django.conf import settings
from django.urls import include, path
from . import views
from . import api

app_name = 'podcasts'

episodes_patterns = [
    path('<uuid:id>/', include([
        # path('position/<int:position>', views.podcasts_refresh_feed, name='podcasts-refresh-feed'),
        path('played/', api.episodes_mark_played, name='episodes-mark-played'),
        # path('unplayed/', views.episodes_mark_unplayed, name='episodes-mark-unplayed'),
    ]))
]

api_patterns = [
    path('refresh-feed/<slug:slug>/', api.podcasts_refresh_feed, name='api-refresh-feed'),
    path('episodes/', include(episodes_patterns)),
]


podcasts_patterns = [
    path('', views.podcasts_list, name='podcasts-list'),
    path('discover/', views.podcasts_discover, name='podcasts-discover'),
    path('new/', views.podcasts_new, name='podcasts-new'),
    path('<slug:slug>/', include([
        path('', views.podcasts_details, name='podcasts-details'),
        path('refresh/', views.podcasts_refresh_feed, name='podcasts-refresh-feed'),
    ]))
]

urlpatterns = [
    path('', views.index, name='index'),
    path('api/', include(api_patterns)),
    path('podcasts/', include(podcasts_patterns)),
    path('settings/', views.user_settings, name='podcasts-user-settings'),
]
