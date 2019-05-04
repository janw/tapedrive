from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.i18n import JavaScriptCatalog

password_reset_patterns = [
    path("change/", auth_views.PasswordChangeView.as_view(), name="password_change"),
    path(
        "change/done/",
        auth_views.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    path("reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path(
        "reset/requested/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    re_path(
        r"reset/t/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]

urlpatterns = [
    path("", include("podcasts.urls")),
    path("admin/", admin.site.urls),
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("password/", include(password_reset_patterns)),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
