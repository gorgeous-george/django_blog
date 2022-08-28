import datetime

from blog_app.tasks import send_email_task as celery_send_mail
from blog_app.tasks import send_email_to_author_task as celery_send_mail_to_author

from blog_app.forms import ContactFrom, RegisterForm
from blog_app.models import BlogAuthor, BlogPost, BlogComment

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect, render
from django.urls import path, reverse, reverse_lazy
from django.views import generic
from django.views.decorators.cache import cache_page


@cache_page(20)
def index(request):
    """View function for home page of site."""
    b_count = BlogPost.objects.filter(is_published=True).annotate(blogposts_count=Count('author'))
    count = b_count.count()
    paginator = Paginator(b_count, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        context={
            'page_obj': page_obj,
            'count': count,
        }
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

    def get_queryset(self):
        """
        Return list of Blog objects having "is_published = True"
        """
        queryset = BlogPost.objects.filter(is_published=True)
        return queryset


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
        author = get_object_or_404(BlogAuthor, pk=id)
        queryset = BlogPost.objects.filter(author=author, is_published=True)
        return queryset

    def get_context_data(self, **kwargs):
        """
        Add BlogAuthor to context, so they can be displayed in the template
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
    paginate_using = BlogComment
    paginate_by = 5

    def get_context_data(self, **kwargs):
        object_list = BlogComment.objects.filter(is_published=True, commented_post=self.get_object())  # TODO: fix comment pagination and is_published
        context = super(BlogDetailView, self).get_context_data(object_list=object_list, **kwargs)
        return context


class BloggerListView(generic.ListView):
    """
    Generic class-based view for a list of bloggers.
    """
    model = BlogAuthor
    paginate_by = 5


class BlogCommentCreate(generic.CreateView):
    """
    Form for adding a blog comment. Requires login.
    """
    model = BlogComment
    fields = ['commenter', 'comment_text']

    def get_context_data(self, **kwargs):
        """
        Add associated blog to form template so can display its title in HTML.
        """
        # Call the base implementation first to get a context
        context = super(BlogCommentCreate, self).get_context_data(**kwargs)
        # Get the blog from id and add it to the context
        context['blogpost'] = get_object_or_404(BlogPost, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        """
        Add associated blog to form data before setting it as valid (so it is saved to model)
        """
        # Associate comment with blog based on passed id
        post = get_object_or_404(BlogPost, pk=self.kwargs['pk'])
        form.instance.commented_post = post

        # Sending email to helpdesk
        subject = 'new comment has been added'
        from_email = 'noreply@my_blog.com'
        message_text = post.title+' received a new comment: "'+form.cleaned_data['comment_text']+'"'
        celery_send_mail.delay(subject, message_text, from_email)

        # Sending email to author
        url = reverse('blog-detail', kwargs={'pk': self.kwargs['pk'], })
        link = path(url, BlogDetailView.as_view())
        subject = 'new comment has been added to your post'
        author_email = [post.author.user.email]
        message_text = post.title+' received a new comment: "'+form.cleaned_data['comment_text']+'" '+f"{link}" # TODO: fix
        celery_send_mail_to_author.delay(subject, message_text, author_email)

        # Call super-class form validation behaviour
        return super(BlogCommentCreate, self).form_valid(form)

    def get_success_url(self):
        """
        After posting comment return to associated blog.
        """
        return reverse('blog-detail', kwargs={'pk': self.kwargs['pk'], })


class BlogPostCreate(LoginRequiredMixin, generic.CreateView):
    model = BlogPost
    fields = ['title', 'short_text', 'full_text', 'created_date', 'published_date', 'image', 'is_published']
    initial = {
        'published_date': datetime.datetime.now(),
    }

    def form_valid(self, form):
        author = BlogAuthor.objects.get(user_id=self.request.user.id)
        form.instance.author = author
        subject = 'new post has been created'
        from_email = 'noreply@my_blog.com'
        message_text = author.user.username+' created new post "'+form.cleaned_data['title']+'"'
        celery_send_mail.delay(subject, message_text, from_email)
        return super(BlogPostCreate, self).form_valid(form)


class BlogPostUpdate(LoginRequiredMixin, SuccessMessageMixin, generic.UpdateView):
    model = BlogPost
    fields = ['title', 'short_text', 'full_text', 'created_date', 'published_date', 'image', 'is_published']
    initial = {
        'published_date': datetime.datetime.now(),
    }
    template_name = 'blog_app/blogpost_update.html'
    success_message = "Blog post was updated"

    def get_success_url(self):
        """
        After posting comment return to associated blog.
        """
        return reverse('blog-detail', kwargs={'pk': self.kwargs['pk'], })
