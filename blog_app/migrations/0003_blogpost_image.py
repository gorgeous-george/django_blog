# Generated by Django 4.1 on 2022-08-25 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog_app', '0002_blogauthor'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpost',
            name='image',
            field=models.ImageField(default='image.png', upload_to='blog/images/'),
        ),
    ]
