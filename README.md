# SSDP Chapter Activity Tracker
## v3.0.0 - Flask Rebuild

> A web application to track activity in the Students For Sensible Drug Policy network
> [ssdp.org](https://ssdp.org)

## Setup
We haven't actually pushed this to production yet, so no setup information is avaiable.

## Development
You'll want to set up a Flask development environment to work on this. You can learn more about the steps to do so in the [Flask Documentation](http://flask.pocoo.org/docs/1.0/installation/#installation).

The Flask CAT was built with Flask v1.0 and Python 3.
```
├── admin.py
├── auth.py
├── blog.py
├── chapters.py
├── db.py
├── __init__.py
├── schema.sql
├── static
│   ├── bootstrap.css
│   ├── bootstrap.min.js
│   ├── custom.css
│   ├── logo-transparent.png
│   └── SSDP20-logo-transparent.png
└── templates
    ├── admin
    │   ├── activities.html
    │   ├── categories.html
    │   ├── index.html
    │   ├── spending.html
    │   ├── stats.html
    │   ├── user-edit.html
    │   ├── user-list.html
    │   └── users.html
    ├── auth
    │   ├── login.html
    │   └── register.html
    ├── base.html
    ├── blog
    │   ├── available-activities.html
    │   ├── create.html
    │   ├── faq.html
    │   ├── index.html
    │   ├── leaderboard.html
    │   ├── store.html
    │   └── update.html
    └── chapters
        ├── chapter.html
        └── index.html
```
## Python Classes

### admin.py
This is where all the administrative functions and pages live. The index, at /admin, is a landing page for all those pages and functions. It should just be a column of buttons that include links and fuctions for users to control their CAT experience.

Users with the permissions 'Admin' can see all of the controls. 'Staffer' gets fewer. 'Chapter' gets the least.

This class controls:
- Creating unique URLs for user pages with `makeURL()`
- Generating the stats page with `stats()`
- Adding users with `users()`
- Adding point categories with `categories()`
- Logging points with `activities()`
- Spending points with `spending()`
- One-off commands with `command()`
  - `RESET` will reset the stats in the user table
  - `BACKUP` will create a backup of the database. There's notes in the documentation in this class, but for good measure: you need to have a folder called `/backups` in your root directory for this to work. Otherwise it won't. Planning some funcationality to hook into a Google Drive or DropBox or something
- Editing user information through the `userList()` and `userEdit()` methods

### auth.py
This class controls logging in and logging out. It's almost a direct duplicate of the Flaskr tutorial login system.

I pretty much didn't change anything from the tutorial [here](http://flask.pocoo.org/docs/1.0/tutorial/) - so not much to say about it. If you want to dig in to how things are working, check out the tutorial and feel free to make changes there. Login systems are beyond my abilities at the moment, so I won't make many changes here.

### blog.py
This class came from the [Flaskr tutorial](http://flask.pocoo.org/docs/1.0/tutorial/) as well.

The tutorial gave me a few things like creating 'blog posts' and editing them, so I kept the bulk of that to use with actions.

I never changed it from `blog` because I didn't want to create any weird bugs. Maybe later on down the road we'll clean it up in refactoring. For now, here's what we do:

- Control the homepage for the entire site with `index()`
- Control the creation of action with `create()`
  - This is **not** how we're creating actions. We could, but we're doing it better in admin.activities(). Leaving this in for now, but will come back and remove it during refactoring and cleanup
- Retrieve actions through `get_action()`
- Update actions with `update()`
- Delete actions with `delete()`
- Render a leaderboard with `leaderboard()`
- Render the available activities page through `availableActivities()`
- Render the FAQ with `faq()`
- Render the store with `store()`
  - This may need to get merged or changed with the spending function in the admin class

Lots of these methods are good boilerplates for manipulating the database in other ways, so I've kept a lot of it pretty close to the tutorial.

### chapters.py
This class provides methods to work with chapter data. It's a bit more front facing.

Here's what this class does:

- Displays all of the chapters in a page with `index()`
- Return a chapter from the database with `get_chapter()`
- Displays a chapter page with `chapter()`

### db.py
This class was also provided by the [Flaskr tutorial](http://flask.pocoo.org/docs/1.0/tutorial/). In the same fashion, I really didn't make any changes here.

The biggest thing to note is that I was having trouble getting click to work and couldn't make new CLI commands. That was a hassle during development, so I just overrode the one CLI command that did work.

There are some comments in `init_db()` that go over those overrides and how I used them.

### init.py
Another class that came from the [Flaskr tutorial](http://flask.pocoo.org/docs/1.0/tutorial/). My understanding is this class initializes the Flask app and registers blueprints and URL rules. I've only added here what I needed for Blueprints and URLs.

## SQL files
### schema.sql
This is the SQL schema for the SQLite database. It's the first database I've ever designed from the ground up, so could be refined. I'm somewhat hopeful I built it in such a way that it's at least easy to extend.

## Static assets
We've got the bootstrap CSS and JS, along with a custom CSS file here and other assets. Pretty straightforward. Any other required assets should live in this directory.

## Templates
Flask uses the Jinja2 templating language for HTML templates.

### base.html
This template provides the `<head>`, `<header>`, and `<html>` tags, along with the nav bar.

In the future, we might pull out some of those components for better structure.

### admin/activities.html
This template is where we log activities.

### admin/categories.html
This page allows us to create new types of actions

### admin/index.html
Landing page for the control panel for all types of users.

### admin/spending.html
This template allows us to create new spending.

### admin/stats.html
Renders a stats page. Most of the interesting work is done on the Python side for this one, and the HTML just renders the values.

### admin/user-edit.html
Allows us to edit some values for each user.

### admin/user-list.html
Renders a list of users and their user-edit links. In the future this will include a search function. For now, ctrl+f will have to do.

### admin/users.html
Allows us to add new users.

### auth/login.html
Login page - provided by Flask tutorial

### auth/register.html
Register page - disabled in our app for now. Will likely need to remove or consider enabling this in the future.

### blog/available-activities.html
Lists the available activities

### blog/create.html
Used to create blog posts/actions. Disabled in our app, and should consider re-enabling it or removing it in a refactor.

### blog/faq.html
Displays the FAQ page. 


## TODO:
- PEP8 standards
- WCAG standards
- Email notifications for staffers, chapters, etc.
- Twitter integration for activity feed
- Mozilla Observatory changes
- Automate points to Master List and/or NationBuilder
- Consistent login reqs across pages
