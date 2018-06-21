# SSDP Chapter Activity Tracker
## v3.0.0 - Flask Rebuild
```
├── admin.py
├── auth.py
├── blog.py
├── chapters.py
├── db.py
├── __init__.py
├── __pycache__
│   ├── admin.cpython-36.pyc
│   ├── auth.cpython-36.pyc
│   ├── blog.cpython-36.pyc
│   ├── chapters.cpython-36.pyc
│   ├── db.cpython-36.pyc
│   └── __init__.cpython-36.pyc
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

## admin.py
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

## auth.py
This class controls logging in and logging out. It's almost a direct duplicate of the Flaskr tutorial login system.

I pretty much didn't change anything from the tutorial [here](http://flask.pocoo.org/docs/1.0/tutorial/) - so not much to say about it. If you want to dig in to how things are working, check out the tutorial and feel free to make changes there. Login systems are beyond my abilities at the moment, so I won't make many changes here. 
