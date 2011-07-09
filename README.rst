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

 * Enables users to enter information about items they wish to give away
 * Serves up that information to the web, marked up using open formats
   such as hListing

Longer term plans
-----------------
 * Enable users to aggregate and search other users' listings
 * Allow users to specify privacy settings for searches
 * Geographical searches
 * Think about integrating it into users' social graphs (ie. f***book)
 * Think further about how users will contact each other once one of them has
   identified something they want
 * Wanted listings

Status
======

Still lots to do before it's actually useful. So far it's possible for users to
register and enter offer details, but searching those listings is still TODO.

Getting it working
==================

It's a pretty standard Django project, so I won't provide detailed instructions.
Check it out, install the dependencies (which I will list at some point...), 
copy localsettings.py.dist to localsettings.py, edit localsettings.py, then you
should be able to do the syncdb and runserver shizzle.
