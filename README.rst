Project faro
======

Project faro is a service that allows users to collaboratively plan events and then
will handle the organization of participants during the lifetime of the event.

Alpha 2
=======
Alpha 2 is a raw flask RESTful api not using flask-restless. It aims to be more
powerful and configurable than Alpha 1. It will be running on port 5002 on the
same host and its availability is random at best, zero and worst.

Alpha 1
=======

Alpha 1 is an extremely simple version of the Faro API. It has support for the
following resources:

* Users at /api/users
* Events at /api/events
* Choices at /api/choices

To use Alpha 1
--------------

Using Alpha 1 isn't meant to be simple or nice, but it is meant to teach you
the basic pattern of things.

On a linux type machine with git perform the following steps::

  $ git clone https://github.com/micha/resty.git
  $ source resty/resty
  $ resty http://jibely.com:5001 -H "Content-type:application/json"
  $ GET /api/users
  $ GET /api/events
  $ GET /api/choices
  $ POST /api/users -d '{"name":"<some username>"}'
  $ GET /api/users/<some user uuid>
  $ DELETE /api/users/<some user uuid>
  $ POST /api/events -d '{"name":"<some event name>", "owner_id": "<user uuid>"}'
  $ DELETE /api/events/<some event uuid>

Just a summary of what is happening above:

- The resty client is first cloned (downloaded) from github.com
- By 'sourcing' the file it dumps the resty code into your shell, so you can use
  the application
- resty <url> -H "..." will set the global resty URL target, and -H are headers
  passed to the underlying HTTP system, curl
- At this point normal HTTP methods are available in all caps: GET, POST, etc
  at passed resource relative to the global resty URL target
- Data is passed to curl using -d, and jibely.com is expecting json

Expected and known issues:

- There is no attempt to maintain foreign key (FK) constraints
- Sometimes errors are not returned in a proper format (all of them should be
  json)
- The service is currently running on a tmux session and is subject to the
  whims of the tmux owner

Service Features
================

* Simple creation of events with multiple components
* Collaborative decision making for all participants in the event
* Component selection based on selected component (if a certain component is
  selected then other components become available or unavailable)
* A component that provides suggestions (like a suggestion box) which are then
  available to be voted on 

Project Components
==================

* a RESTful service
* a web front-end
* multiple mobile apps

RESTful Service
===============

* OAuth Support

