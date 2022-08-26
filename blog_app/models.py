from django.conf import settings
from django.db import models
from django.utils import timezone
from django.urls import reverse #Used to generate URLs by reversing the URL patterns
from django.contrib.auth.models import User #Blog author or commenter


class BlogAuthor(models.Model): #to fix the bug with User instance
    """
    Model representing a blogger.
    """
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    bio = models.TextField(max_length=400, help_text="Enter your bio details here.")

    class Meta:
        ordering = ["user", "bio"]

    def get_absolute_url(self):
        """
        Returns the url to access a particular blog-author instance.
        """
        return reverse('blogs-by-author', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.user.username


class BlogPost(models.Model):
    """
    Model representing a blog post.
    """
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    short_text = models.CharField(max_length=200)
    full_text = models.TextField()
    image = models.ImageField(upload_to='blog/images/', default='image.png')
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    is_published = models.BooleanField

    class Meta:
        ordering = ["-created_date"]

    def get_absolute_url(self):
        """
        Returns the url to access a particular blog instance.
        """
        return reverse('blog-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.title


class BlogComment(models.Model):
    """
    Model representing a comment against a blog post.
    """
    commenter = models.CharField(max_length=200)
    comment_text = models.TextField(max_length=1000, help_text="Enter comment about blog here.")
    comment_date = models.DateTimeField(auto_now_add=True)
    commented_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
    is_published = models.BooleanField

    class Meta:
        ordering = ["-comment_date"]

    def __str__(self):
        """
        String for representing the Model object.
        """
        len_title = 75
        if len(self.comment_text) > len_title:
            titlestring = self.comment_text[:len_title] + '...'
        else:
            titlestring = self.comment_text
        return titlestring
