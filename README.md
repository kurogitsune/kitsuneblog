# Kitsuneblog

This is a python template for a blog that updates live 1 symbol per a given time interval. It is lazily ported to heroku and uses web-sockets, flask, gevent, redis and gunicorn.

This is a fork of [heroku websocket example](https://github.com/heroku-examples/python-websockets-chat) at [kennethreitz](https://github.com/kennethreitz)kennethreitz. It is therefore not intended to be fully optimized and is likely prone to attacks. Consider it an example as well, and try to use SSL when possible.

Check out the [demo](http://www.mensurazoili.com) at my blog or fork.

## Installation:
Clone and follow the setup instructions on the main page, set up origin time, delay and check out the static text file format (there has to be an enclosing div).

Text will slowly fade in for every user, whenever they come, at the same pace.

Supports unicode and most of HTML layout. Support for input controls and images coming soon.

## Known issues: 
Problem with spaces near tags - use non breakable spaces when spaces are missing.

No non-paired tags. Img support coming soon.



![Kitsune](/static/favicons/favicon-16x16.png) kokudagitsune