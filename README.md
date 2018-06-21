# SSDP Chapter Activity Tracker
## v3.0.0 - Flask Rebuild
Add note about backups directory and database stuff.
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

###
