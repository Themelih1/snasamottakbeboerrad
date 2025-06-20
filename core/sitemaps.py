from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import BlogPost, Service

class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return BlogPost.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at
class ServiceSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        # Yalnızca yayınlanmış servisleri dahil et
        return Service.objects.filter(is_published=True)
    
    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('core:service_detail', args=[obj.slug])