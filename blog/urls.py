from django.urls import path
from . import views
from .feeds import LatestPostsFeed

app_name = 'blog'

urlpatterns = [
    # Home page - should be first if it's the root
    path('', views.home, name='home'),
    
    # Search - specific pattern before generic ones
    path('search/', views.post_search, name='post_search'),

    
    # Posts by tag
    path('posts/tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
    
    # All posts
    path('posts/', views.post_list, name='post_list'),
    
    # Categories
    path('category/<int:category_id>/', views.category_list, name='category_list'),
    
    # Individual post - very specific pattern
    path('<int:year>/<int:month>/<int:day>/<slug:post>/',
         views.post_detail, name='post_detail'),
    
    # Post interactions
    path('<int:post_id>/share/', views.post_share, name='post_share'),
    path('<int:post_id>/comment/', views.post_comment, name='post_comment'),
    
    # Feed
    path('feed/', LatestPostsFeed(), name='post_feed'),
]