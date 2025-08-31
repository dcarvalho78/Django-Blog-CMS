# blog/context_processors.py
from .models import Category
from taggit.models import Tag

def categories(request):
    return {
        "categories": Category.objects.all(),
        "tags": Tag.objects.all()[:50],  # limit to 50 to keep the menu snappy
    }
