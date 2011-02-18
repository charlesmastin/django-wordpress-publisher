#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='django-wordpress-publisher',
    version='0.2.2',
    description='Remotely publish to your Wordpress blog via the XML-RPC from your Django website',
    author='Charles Mastin',
    author_email='charles@bricksf.com',
    url='https://github.com/charlesmastin/django-wordpress-publisher/',
    license='New BSD License',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
    ],
    packages=find_packages(),
    zip_safe=False,
)
