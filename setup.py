from setuptools import setup, find_packages

setup(
    name = "exsequiae",
    author = "Pedro Ferreira",
    author_email = "ilzogoiby@gmail.com",
    description = "A personal publishing system, based on markdown and web.py",
    version = "0.1",
    install_requires = ['markdown2', 'flask', 'babel', 'flask-babel'],
    packages = find_packages(),
    package_data = {
    'exsequiae': ['templates/*.html', 
                  'static/*.js', 'static/*.css', 'static/images/*.png',
                  'static/smoothness/*.css', 'static/smoothness/images/*.png']
    },
    zip_safe=False)

