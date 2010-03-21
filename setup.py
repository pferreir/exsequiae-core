from setuptools import setup, find_packages

setup(
    name = "exsequiae",
    author = "Pedro Ferreira",
    author_email = "ilzogoiby@gmail.com",
    version = "0.1",
    packages = find_packages(),
    package_data = {
    '': ['*.html']
    })
