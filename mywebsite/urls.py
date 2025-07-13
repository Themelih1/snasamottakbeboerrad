from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('snasa/', admin.site.urls),
    path('tinymce/', include('tinymce.urls')),
]

urlpatterns += i18n_patterns(
    path('', include('core.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
