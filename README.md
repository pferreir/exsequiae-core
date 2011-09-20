# Introduction

Exsequiæ is a very simple wiki-like personal publishing tool. It is
written in Python and makes heavy use of [Werkzeug](http://werkzeug.pocoo.org/)/[Flask](http://flask.pocoo.org) and [jQuery](http://jquery.com).

---

# Installing

    python setup.py install

# Example config file

Place it at /path/to/environment/exsequiae.cfg

```python
SITE_TITLE = 'My site'
STARTING_YEAR = 2009
DEFAULT_PAGE = 'Start'
ADMIN_USERNAME = 'myusername'
ADMIN_PASSWORD = 'mypass'
SECRET_KEY = 'a VERY random sequence'
STORAGE_TYPE = 'couch'
STORAGE_PARAMS = {'db': 'exsequiae_tests'}
CACHE_TYPE = 'MemcachedCache'
CACHE_PARAMS = {'servers': ['127.0.0.1']}
```

# Executing test server

    python run.py /path/to/environment

# Unit tests

Unit tests can be invoked like this:

    python -m unittest exsequiae.tests
