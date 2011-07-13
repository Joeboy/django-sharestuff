==========
Going Spare
==========
-----------------------------------------
Peer to Peer Sharing for physical objects
-----------------------------------------

What's this thing for?
======================

The grand plan
--------------
The grand plan is to establish an open platform for sharing unneeded goods.
Think of it like Freecycle for Web 2.0, or The Pirate Bay for physical objects.

The short term plan
-------------------
The immediate plan is to create a quick and dirty Django app that:

 * Enables people to enter information about items they wish to give away
 * Serves up that information to the web
 * Allows people to easily share that information on freecycle, freegle etc

Longer term plans
-----------------
 * Enable users to save searches, and create rss feeds of them
 * More work on privacy options, which aren't really respected a the moment
 * Think about integrating feeds from other systems. The main barrier being,
   getting permission to do so
 * Think about integrating it into users' social graphs (ie. f***book)
 * Wanted listings
 * Use hListing or similar markup to allow easy scraping by other apps
 * An API

Status
======

It's possible for users to register and enter offer details, share offers on
freecycle/freegle, and search for offers.

Getting it working
==================

The project is written in the Django framework. To get it working you'll need
to:
 * Check out the project
 * install the dependencies from the requirements.txt file
 * copy localsettings.py.dist to localsettings.py, and edit localsettings.py to
   your tastes
 * Grab the mindmap geoip data by running the script `geoip/get_db.sh`
 * If you did everything right, you should be able to syncdb and runserver.
