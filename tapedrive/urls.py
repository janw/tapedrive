from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.views.generic import TemplateView
from rest_framework import routers

from listeners.serializers import UserViewSet, UserView
from podcasts.api import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"podcasts", views.PodcastViewSet)
router.register(r"episodes", views.EpisodeViewSet)

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="index"),
    path("api/", include(router.urls), name="api-root"),
    path("api/podcastepisodes/<slug:slug>/", views.PodcastEpisodesList.as_view()),
    path("admin/", admin.site.urls),
    path("api/user/", UserView.as_view(), name="user_details"),
    path("api/auth/", include("rest_framework.urls")),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
