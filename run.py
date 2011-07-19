#!/usr/bin/env python

"""
Run script - suitable for both standalone WSGI server, or inclusion from others.
"""

from exsequiae import app

if __name__ == "__main__":
    app.run(debug=True)
