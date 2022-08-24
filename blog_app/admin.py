from django.contrib import admin
from .models import BlogComment, BlogPost

admin.site.register(BlogPost)

admin.site.register(BlogComment)
