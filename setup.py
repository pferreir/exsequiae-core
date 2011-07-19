from setuptools import setup, find_packages

setup(
    name = "exsequiae",
    author = "Pedro Ferreira",
    author_email = "ilzogoiby@gmail.com",
    description = "A personal publishing system, based on markdown and web.py",
    version = "0.1",
    install_requires = ['markdown2', 'flask', 'babel'],
    packages = find_packages(),
    package_data = {
    '': ['*.html']
    })

