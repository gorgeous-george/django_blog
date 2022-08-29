# Django DIY Blog

## Basic blog site written in Django 

This web application creates a very basic blog site using Django. 
The site allows blog authors to create/update blogs, and any user to add comments via a form. 
Any user can list all bloggers, all blogs, and detail for bloggers and blogs.

## Quick Start

To get this project up and running locally on your computer:

- Set up the Python development environment. We recommend using a Python virtual environment.
- Assuming you have Python setup, run the following commands (if you're on Windows you may use py or py -3 instead of python3 to start Python):

> pip3 install -r requirements.txt
> python3 manage.py makemigrations
> python3 manage.py migrate
> python3 manage.py createsuperuser # Create a superuser
> python3 manage.py fill_db # to fill the database with lorem ipsum data
> python3 manage.py runserver

- Open a browser to http://127.0.0.1:8000/admin/ to open the admin site
- Create a few test objects of each type.
- Open tab to http://127.0.0.1:8000 to see the main site, with your new objects.

- for celery tasks and cache you need to install appropriate libraries and appropriately update settings.py

## Features:
- User can register + login/logout
- User can create posts (login required)
- The user can publish posts or put them into drafts
- The users can modify their posts
- Anonymous users can post comments
- Comments are moderated before publication 
- The administrator receives an email notification about a new post or comment (console)
- The user is notified of a new comment below the post (console) 
- There is a page with a list of all posts
- There is a page with a list of user posts
- There is a post page
- There is a public profile page
- There is a profile in which you can change your data
- Pagination of posts and comments
- The post has a title, a short description, a picture, and a full description
- The comment has a username and text
- Fixture loremipsum
- Admin panel with functionality
- Feedback form with the admin
- Templates with styling
- Different settings for development and production
- Database query optimization
- Caching
- Celery