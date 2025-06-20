from django.urls import path
from django.views.generic import TemplateView
from .sitemaps import BlogSitemap, ServiceSitemap
from . import views
from .views import tinymce_upload_image
from django.contrib.sitemaps.views import sitemap


# Import your sitemap classes here, for example:
# from .sitemaps import BlogSitemap, ServiceSitemap

# Define the sitemaps dictionary
sitemaps = {
    'blog': BlogSitemap,
    'services': ServiceSitemap,
}

app_name = 'core'


urlpatterns = [
    path('', views.home, name='home'),
    path('hizmetler/', views.services, name='services'),
    path('hizmetler/<slug:slug>/', views.service_detail, name='service_detail'),
    path('ekibimiz/', views.team, name='team'),
    path('ekibimiz/<slug:slug>/', views.team_detail, name='team_detail'),
    path('blog/', views.blog, name='blog'),
    path('blog/<slug:slug>/yorum/', views.add_comment, name='add_comment'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('iletisim/', views.contact, name='contact'),
    path('tinymce/upload_image/', views.tinymce_upload_image, name='tinymce_upload_image'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),

]

