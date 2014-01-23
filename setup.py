# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

DESCRIPTION = ''
try:
    LONG_DESCRIPTION = open('README.rst').read()
except:
    LONG_DESCRIPTION = DESCRIPTION

setup(
    name='django-customerevents',
    version='0.0.4',
    author='Jason Kraus',
    author_email='zbyte64@gmail.com',
    packages=find_packages(exclude=['tests']),
    url='https://github.com/zbyte64/django-customerevents',
    license='BSD',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    zip_safe=False,
    include_package_data=True,
    #package_data={'': ['README.rst']},
    #install_requires=['django-jsonfield'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
