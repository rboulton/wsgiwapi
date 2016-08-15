# README

*This project has not been maintained since 2009*


WSGIWAPI is intended to make it extremely easy to make web APIs based on
Python programs.

See docs/introduction.html, or http://wsgiwapi.tartarus.org/, for an
introduction to WSGIWAPI.

You can run the testsuite by running "./runtests.py".

All changes are logged in the ChangeLog.

# Prerequisites

WSGIWAPI should work with python versions 2.5 and 2.6.  Older versions (ie,
2.4 or earlier) are not supported - the main obstacle is that the exception
classes in WSGIWAPI are new-style classes, which are not allowed as
exceptions in python 2.4.

Support for python 3.0 is not yet implemented, but it is not expected to be
difficult.

To use JSON support with python 2.5 (eg, the "jsonreturning" decorator),
you will need the "json" or "simplejson" module.
