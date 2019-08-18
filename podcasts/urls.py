from podcasts.api import views

from rest_framework import routers


router = routers.DefaultRouter()
router.register(r"podcasts", views.PodcastViewSet)
router.register(r"episodes", views.EpisodeViewSet)

app_name = "podcasts"
urlpatterns = router.urls


# urlpatterns = [
#     path("", views.index, name="index"),
#     path("api/", include(global_api_patterns)),
#     path("podcasts/", include(podcasts_patterns)),
#     path("episodes/", include(episodes_patterns)),
#     path("activity/", views.activity_list, name="activity-list"),
#     path("settings/", views.settings, name="settings"),
# ]
# episodes_patterns = [
#     path(
#         "<int:id>/",
#         include(
#             [
#                 path(
#                     "download/",
#                     api.episode_queue_download,
#                     name="api-episode-queue-download",
#                 ),
#                 path(
#                     "details/",
#                     api.EpisodeDetailsView.as_view(),
#                     name="api-episode-details",
#                 ),
#                 path("played/", api.episodes_mark_played, name="episodes-mark-played"),
#             ]
#         ),
#     )
# ]

# podcasts_api_patterns = [
#     path("download/", api.podcast_queue_download, name="api-podcast-queue-download"),
#     path("refresh-feed/", api.podcast_refresh_feed, name="api-refresh-feed"),
#     path("subscribe/", api.podcast_subscribe, name="api-subscribe"),
#     path("unsubscribe/", api.podcast_unsubscribe, name="api-unsubscribe"),
# ]

# global_api_patterns = [
#     path("add/", api.AddPodcast.as_view(), name="api-podcast-add"),
#     path("topcharts/", api.apple_podcasts_topcharts, name="api-topcharts"),
#     path("search/", api.ApplePodcastsSearch.as_view(), name="api-search"),
#     path("lookup/<int:id>", api.apple_podcasts_feed_from_id, name="api-lookup"),
# ]

# podcasts_patterns = [
#     path("", views.PodcastsList.as_view(), name="podcasts-list"),
#     path("new/", views.PodcastNew.as_view(), name="podcasts-new"),
#     path(
#         "<slug:slug>/",
#         include(
#             [
#                 path("", views.PodcastDetails.as_view(), name="podcasts-details"),
#                 path("api/", include(podcasts_api_patterns)),
#                 path(
#                     "refresh/",
#                     views.podcasts_refresh_feed,
#                     name="podcasts-refresh-feed",
#                 ),
#                 path("delete/", views.PodcastDeleteView.as_view(), name="delete"),
#             ]
#         ),
#     ),
# ]

