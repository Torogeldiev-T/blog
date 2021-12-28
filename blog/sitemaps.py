from django.contrib.sitemaps import Sitemap
from .models import Post


class PostSiteMap(Sitemap):
    priority = 0.9
    changefreq = 'weakly'

    def items(self):
        return Post.published.all()

    def lastmod(self, obj):
        return obj.updated
