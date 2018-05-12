from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

password_reset_patterns = [
    path('', auth_views.password_reset, name='password_reset'),
    path('requested/', auth_views.password_reset_done, name='password_reset_done'),
    re_path(r't/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            auth_views.password_reset_confirm, name='password_reset_confirm'),
    path('done/', auth_views.password_reset_complete, name='password_reset_complete'),
]

urlpatterns = [
    path('', include('podcasts.urls')),

    path('admin/', admin.site.urls),

    path('login/', auth_views.login, name='login'),
    path('logout/', auth_views.logout, name='logout'),

    path('password-reset/', include(password_reset_patterns)),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
        # re_path(r'^silk/', include('silk.urls', namespace='silk')),
    ] + urlpatterns
