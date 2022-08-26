from blog_app.views import BlogCommentCreate, BlogDetailView, BlogListbyAuthorView, BlogListView, BloggerListView, BlogPostCreate, index

from django.urls import path

urlpatterns = [
    path('', index, name='index'),
    path('blogs/', BlogListView.as_view(), name='blogs'),
    path('blogger/<int:pk>', BlogListbyAuthorView.as_view(), name='blogs-by-author'),
    path('blog/<int:pk>', BlogDetailView.as_view(), name='blog-detail'),
    path('bloggers/', BloggerListView.as_view(), name='bloggers'),
    path('blog/<int:pk>/comment/', BlogCommentCreate.as_view(), name='blog_comment'),
    path('blog/create/', BlogPostCreate.as_view(), name='blog-create')
]