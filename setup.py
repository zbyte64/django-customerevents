# -*- coding: utf-8 -*-
from setuptools import setup

DESCRIPTION = ''
try:
    LONG_DESCRIPTION = open('README.rst').read()
else:
    LONG_DESCRIPTION = DESCRIPTION

setup(
    name='django-customerevents',
    version='0.0.1',
    author='Jason Kraus',
    author_email='zbyte64@gmail.com',
    packages=['customerevents'],
    url='https://github.com/zbyte64/django-post_office',
    license='MIT',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    zip_safe=False,
    include_package_data=True,
    #package_data={'': ['README.rst']},
    install_requires=['django-jsonfield'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
