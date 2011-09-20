#!/usr/bin/env python

"""
Run script - suitable for both standalone WSGI server, or inclusion from others.
"""

import argparse
from exsequiae import create_app

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('instance_path', help='path for the desired instance')

    args = parser.parse_args()

    create_app(args.instance_path).run(debug=True)
