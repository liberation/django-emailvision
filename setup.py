#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
django-emailvision
------------------

django-emailvision is a python library that communicate with the REST (PI Syntax)
API of emailvision.

Links
`````

* `website <https://github.com/liberation/django-emailvision>`_
* `emailvision <http://www.emailvision.fr/>`_
"""
from setuptools import setup


setup(
    name='django-emailvision',
    version='0.1',
    url='http://packages.python.org/django-emailvision/',
    license='WTF',
    author='Djaz Team',
    author_email='devweb@liberation.fr',
    description='Access emailvision API with Python',
    long_description=__doc__,
    packages=['emailvision'],
    namespace_packages=['emailvision'],
    zip_safe=False,
    platforms='any',
#    tests_require=['nose', 'mock_http'],
#    test_suite="nose.collector",
    install_requires=['lxml'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
