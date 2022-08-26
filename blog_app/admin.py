from django.contrib import admin
from .models import BlogAuthor, BlogComment, BlogPost

admin.site.register(BlogAuthor)

admin.site.register(BlogComment)

admin.site.register(BlogPost)
