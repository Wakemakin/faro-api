faro-api
======

The faro-api is the service node that provides access to the models of the faro
platform.

Alpha 3
=======

Alpha 3 is the current version of the RESTful faro-api. It is running on port
5001 and has replaced alpha 1.

It has support for the following resources:

* Users at /api/users
* Events at /api/events

Deploying Alpha 3
-----------------

On a linux type machine with git and virtualenv perform the following
steps::

  $ git clone https://github.com/Wakemakin/faro-api.git
  $ cd faro-api
  $ virtualenv --prompt="(faro-api)" --distribute --no-site-packages .venv
  $ source .venv/bin/activate
  $ pip install -r pip-requirements.txt
  $ python run.py

Args that can be passed to python run.py:

* --database: will recreate and initialize the faro-api.database
* --public: will run the service on an forward listening interface

Testing Alpha 3
---------------

Within the virtual environment (you get in with: source .venv/bin/activate) you
will need to run the following to test the code::

  $ pip install tox
  $ tox

This will run the unit tests on the API and will also run some code-standards
checks based on:

* PEP8
* OpenStack standards

These tests should autmatically run on the CI when pushed if things are working
correctly. :)

To use Alpha 3
--------------

Using Alpha 3 isn't meant to be simple or nice, but it is meant to teach you
the basic pattern of things.

On a linux type machine with git and **curl**,perform the following steps::

  $ git clone https://github.com/micha/resty.git
  $ source resty/resty
  $ resty http://jibely.com:5001 -H "Content-type:application/json"
  $ GET /api/users
  $ GET /api/events
  $ POST /api/users -d '{"username":"<some username>"}'
  $ GET /api/users/<some user uuid>
  $ DELETE /api/users/<some user uuid>
  $ POST /api/events -d '{"name":"<some event name>", "owner_id": "<user uuid>"}'
  $ DELETE /api/events/<some event uuid>

Just a summary of what is happening above:

- The resty client is first cloned (downloaded) from github.com
- By 'sourcing' the file it dumps the resty code into your shell, so you can
  use the application
- resty <url> -H "..." will set the global resty URL target, and -H are headers
  passed to the underlying HTTP system, curl
- At this point normal HTTP methods are available in all caps: GET, POST, etc
  at passed resource relative to the global resty URL target
- Data is passed to curl using -d, and jibely.com is expecting json

Knowing What to Pass in POSTs
-----------------------------

You can find the columns that are needed for proper posting in the following
directory::

  faro_api/models

All of the models within there can be posted to except the Base model. Anything
that has a sa.Column is a thing that can be posted to. For example (this may
be an outdated version of user.py, but the example is fine)::

  class User(db.model()):
      id = sa.Column(sa.Unicode, primary_key=True)
      username = sa.Column(sa.Unicode, unique=True)
      first_name = sa.Column(sa.Unicode)
      last_name = sa.Column(sa.Unicode)
  
      def __init__(self, **kwargs):
          super(User, self).__init__(**kwargs)
          self.id = unicode(utils.make_uuid())
  
      @staticmethod
      def read_only_columns():
          return ['username']
  
      @staticmethod
      def query_columns():
          return ['first_name',
                  'last_name',
                  'date_created'] 

Defines a couple things:

  - There are four columns available to post to: id, username, first_name, and
    last_name
  - One of the columns needs to be unique (username)
  - One column is readonly (username)
  - You can query off 3 columns (first_name, last_name, date_created)
  - btw, everything has a date_created column (from the Base)

Using resty you can create a user like this::

  $ POST /api/users -d '{"username": "bobbeh", "first_name": "bob"}'

Expected and known issues
-------------------------

- Sometimes errors are not returned in a proper format (all of them should be
  json)
- The service is currently running on a tmux session and is subject to the
  whims of the tmux owner

Supported features as of tag:alpha3
----------------------------------

- CRUD support for /api/users
- CRUD support for /api/events (requires valid user)
- Username substitution for User UUID on all queries
- Event association between events and users
- Access of user events through /api/users/id/events
- Access of event owner through /api/events/id/owner
- Creation of event under user POST to /api/users/id/events
