from django.urls import path, include
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from blog.sitemaps import PostSitemap

sitemaps = {
    'posts': PostSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls', namespace='blog')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
    # Redirect root to blog home
    path('', RedirectView.as_view(url='blog/', permanent=True)),
    path('tinymce/', include('tinymce.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)