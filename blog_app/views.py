import datetime
import time

from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction

from blog_app.forms import ContactFrom, RegisterForm
from blog_app.models import BlogAuthor, BlogPost, BlogComment

from celery import Celery

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User #Blog author or commenter
from django.core.mail import BadHeaderError, send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import generic


from .tasks import send_email_task as celery_send_mail


def index(request):
    """View function for home page of site."""
    return render(
        request,
        'index.html',
    )

def contact_form(request):
    if request.method == "POST":
        form = ContactFrom(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            from_email = form.cleaned_data['from_email']
            message_text = form.cleaned_data['message']
            celery_send_mail.delay(subject, message_text, from_email)
            messages.add_message(request, messages.SUCCESS, 'Message sent')
            return redirect('contact')
    else:
        form = ContactFrom()
    return render(
        request,
        "blog_app/contact.html",
        context={
            "form": form,
        }
    )


class RegisterFormView(SuccessMessageMixin, generic.FormView):
    template_name = 'registration/register.html'
    form_class = RegisterForm
    success_message = "Profile has been registered"
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        user = form.save()
        password = form.cleaned_data.get("password1")
        user = authenticate(username=user.username, password=password)
        login(self.request, user)
        return super(RegisterFormView, self).form_valid(form)


class UpdateProfile(LoginRequiredMixin, SuccessMessageMixin, generic.UpdateView):
    model = User
    fields = ["username", "email"]
    template_name = 'registration/update_profile.html'
    success_url = reverse_lazy("index")
    success_message = "Profile updated"

    def get_object(self, queryset=None):
        user = self.request.user
        return user


class UserProfile(LoginRequiredMixin, generic.DetailView):
    model = User
    template_name = "registration/profile.html"

    def get_object(self, queryset=None):
        user = self.request.user
        return user

    def get_context_data(self, **kwargs):
        context = super(UserProfile, self).get_context_data(**kwargs)
        return context


class BlogListView(generic.ListView):
    """
    Generic class-based view for a list of all blogs.
    """
    model = BlogPost
    paginate_by = 5


from django.shortcuts import get_object_or_404


class BlogListbyAuthorView(generic.ListView):
    """
    Generic class-based view for a list of blogs posted by a particular BlogAuthor.
    """
    model = BlogPost
    paginate_by = 5
    template_name = 'blog_app/blog_list_by_author.html'

    def get_queryset(self):
        """
        Return list of Blog objects created by BlogAuthor (author id specified in URL)
        """
        id = self.kwargs['pk']
        target_author = get_object_or_404(BlogAuthor, pk=id)
        return BlogPost.objects.filter(author=target_author) #TODO: to fix the bug

    def get_context_data(self, **kwargs):
        """
        Add BlogAuthor to context so they can be displayed in the template
        """
        # Call the base implementation first to get a context
        context = super(BlogListbyAuthorView, self).get_context_data(**kwargs)
        # Get the blogger object from the "pk" URL parameter and add it to the context
        context['blogger'] = get_object_or_404(BlogAuthor, pk=self.kwargs['pk'])
        return context


class BlogDetailView(generic.DetailView):
    """
    Generic class-based detail view for a blog.
    """
    model = BlogPost


class BloggerListView(generic.ListView):
    """
    Generic class-based view for a list of bloggers.
    """
    model = BlogAuthor
    paginate_by = 5


from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.urls import reverse


class BlogCommentCreate(CreateView):
    """
    Form for adding a blog comment.
    """
    model = BlogComment
    fields = ['description', ]

    def get_context_data(self, **kwargs):
        """
        Add associated blog to form template so can display its title in HTML.
        """
        # Call the base implementation first to get a context
        context = super(BlogCommentCreate, self).get_context_data(**kwargs) #TODO: to fix the bug
        # Get the blog from id and add it to the context
        context['blog'] = get_object_or_404(BlogPost, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        """
        Add author and associated blog to form data before setting it as valid (so it is saved to model)
        """
        # Add logged-in user as author of comment
        form.instance.author = self.request.user
        # Associate comment with blog based on passed id
        form.instance.blog = get_object_or_404(BlogPost, pk=self.kwargs['pk'])
        # Call super-class form validation behaviour
        return super(BlogCommentCreate, self).form_valid(form)

    def get_success_url(self):
        """
        After posting comment return to associated blog.
        """
        return reverse('blog-detail', kwargs={'pk': self.kwargs['pk'], })

class BlogPostCreate(LoginRequiredMixin,generic.CreateView):
    model = BlogPost
    fields = ['title', 'short_text', 'full_text', 'created_date', 'published_date', 'image']
    initial = {
        'published_date': datetime.datetime.now(),
    }
