import datetime

import lorem
import random

from blog_app.models import BlogAuthor, BlogPost, BlogComment

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'fill db using lorem ipsum'

    def handle(self, *args, **options):
        # it is expected that superuser is already created
        # so this command creates just a dummy_user, and adding both admin and dummy_user as authors
        dummy_user = User.objects.create_user(
            username='user', password='user', email='user@user.com', is_superuser='False', is_staff='False')
        dummy_user.save()

        BlogAuthor.objects.create(
            user=User.objects.get(username='admin'),
            bio='Admin has written hundreds of articles about all things to match any occasion.'
        )

        BlogAuthor.objects.create(
            user=User.objects.get(username='user'),
            bio='User is learning to write posts about some things'
        )

        authors_id_list = [_.id for _ in BlogAuthor.objects.all()]

        for _ in range(15):
            BlogPost.objects.create(
                title=lorem.sentence(range=10),
                short_text=lorem.sentence(range=20),
                full_text=lorem.text(range=50),
                created_date=datetime.datetime.now(),
                published_date=datetime.datetime.now(),
                image='blog/FB_IMG_1550259829926.jpg',
                is_published='False',
                author_id=random.choice(authors_id_list),
            )

        for _ in range(15):
            BlogComment.objects.create(
                commenter=lorem.sentence(range=10),
                comment_text=lorem.sentence(range=20),
                comment_date=datetime.datetime.now(),
                commented_post_id=_,
                is_published=random.randint(0, 1),
            )
