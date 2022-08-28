from django.contrib import admin
from .models import BlogAuthor, BlogComment, BlogPost


class BlogPostInlineModelAdmin(admin.TabularInline):
    model = BlogPost


@admin.register(BlogAuthor)
class BlogAuthorAdmin(admin.ModelAdmin):
    list_display = ["user", "bio"]
    inlines = [BlogPostInlineModelAdmin]


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ["is_published", "commenter", "comment_text"]
    list_filter = ["is_published"]
    actions = ["change_status_to_published"]

    def get_queryset(self, request):
        return super(BlogCommentAdmin, self).get_queryset(request)

    def change_status_to_published(self, request, queryset):
        queryset.update(is_published=True)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ["is_published", "author", "title", "short_text", "full_text", "created_date", "published_date", "image"]
    list_filter = ["is_published"]
    actions = ["change_status_to_published"]

    def get_queryset(self, request):
        return super(BlogPostAdmin, self).get_queryset(request)

    def change_status_to_published(self, request, queryset):
        queryset.update(is_published=True)

