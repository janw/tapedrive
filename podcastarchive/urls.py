from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from rest_framework import routers

from podcastarchive.users.serializers import UserViewSet, UserView
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
    path("api/", include(router.urls), name="api-root"),
    path("api/auth/", include("rest_framework.urls")),
    path("admin/", admin.site.urls),
    path("api/user/", UserView.as_view(), name="user_details"),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
