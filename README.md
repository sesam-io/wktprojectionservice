WKT projection service
======================

A web server that receives triples by POST and projects WKT polygons and multipolygin coordinates from
one coordinate system to another. The result is posted to a SDShare Push Receiver endpoint, typically the push
receiver endpoint of a sink in a sdshare client.

The predicates to look for and to output, the graph to post to, push receiver endpoint etc can be
specified in a config file in yaml format. See config/test.yaml for an example configuration.

Installation
------------

This package requires python 3.4 to be installed

In a virtualenv as a normal user so you don't "pollute" your site-packages:
    
    * virtualenv venv
    * source venv/bin/activate
    * python setup.py install

Or as root/superuser: `python setup.py install`

To run
------

`wktprojectionservice`

The server is running at the port 6543 by default. You can modify the port by command line options.
Run it with --help to see all options.

You can do manual tests by posting NTriples using the form found at: http://localhost:6543/form
