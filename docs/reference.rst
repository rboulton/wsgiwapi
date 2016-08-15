===========================
WSGIWebAPI Reference Manual
===========================

.. Warning:: This manual is not in any way complete - don't trust it for information yet!

Design Philosophy
=================

WSGIWebAPI tries hard not to get in your way.  The intention is that it should
be possible to use only those bits of WSGIWebAPI which are useful to you,
without having to know about those parts which you are not using.  In addition,
you shouldn't need to install dependencies for parts of WSGIWebAPI which you're
not using - for example, if you're not using JSON, you don't need to have a
python JSON library installed.

It should be possible to make code using WSGIWebAPI concise and clear, so we've
tried to embrace the "Don't Repeat Yourself" principle.  As an example, document


URI resolution
==============

FIXME - document

.. Note:: arbitrary trailing path information is not accepted by default.  If you want to accept trailing path information, you need to decorate your callable with the ``@pathinfo`` decorator.

Request objects
===============

Response objects
================

Redirection
-----------

WSGIWebAPI currently has no explicit support for HTTP redirects.  For
now, you can implement it yourself by setting the appropriate headers
and returning the appropriate response code.

Returning errors
----------------

The `wsgiwebapi.Response` object allows the HTTP status code to be set
(and knows some standard reason messages for all the standard HTTP 1.1
status codes, so you can just set the numeric code if you're happy to
use the standard reason messages).  This allows you to return any HTTP
status code you like, to represent errors (or redirects, etc).

However, it is often convenient to be able to use exceptions to report
errors.  To enable this, WSGIWebAPI provides `wsgiwebapi.HTTPError`,
which is a subclass of `wsgiwebapi.Response`, and also of the standard
`Exception` class.  This can be thrown, and provided with whatever
status code and message body you like.

For even greater convenience, there are also some subclasses for
specific error conditions:

 - `wsgiwebapi.HTTPServerError`: thrown to report "500 Server Error"
 - `wsgiwebapi.HTTPNotFound`: thrown to report a "404 Not Found"
   error.  
 - `wsgiwebapi.HTTPMethodNotAllowed`: thrown to report a disallowed
   method.  Takes the method which was requested, and a list of the
   allowed methods for this URL.

If your callable raises any other exception, the WSGI application will
return a "500 Server Error".


Decorators
==========

WSGIWebAPI provides a set of useful decorators, to make it easy to
produce certain types of API.  You don't need to use any of these, but
they will often make it easier to produce a clean API.

The WSGIWebAPI decorators can be applied in any order: they all
operate by adding some extra properties to the API, and replacing the
API method with a special wrapper which interprets these properties.

If you are using other (non WSGIWebAPI) decorators which replace the
callable by a decorated callable, you need to ensure that the
properties used by WSGIWebAPI are copied onto the decorated callable.
If you do not do this, WSGIWebAPI will raise an exception at runtime,
to ensure that inconsistent behaviour doesn't result.

Well-behaved decorators will copy the properties by default (by coping
the contents of __dict__ from the original callable to the decorated
callable), but it's best to use one of two approaches provided by
wsgiwebapi to ensure that 

 - If you are writing the decorator yourself, include a call to
   ``wsgiwebapi.copyprops`` at the end of the decorator: pass this the
   original callable, and the decorated callable, and it will copy all
   the appropriate properties across.

   FIXME - example.

 - If you are using an existing decorator, wrap it in the
   ``wsgiwebapi.decorate`` decorator (ie, pass it as an argument to
   this decorator).  This decorator first applies the decorator it is
   given, and then applies ``wsgiwebapi.copyprops`` to fix up the
   properties.

   FIXME - example.

Validation
==========

Restricting HTTP methods
------------------------

By default, WSGIWebAPI will allow any HTTP method to be used to call
your API.  It is often desirable to restrict the set of methods which
are allowed at a particular path.  To do this, you can use the
`allow_method` decorator.  This decorator takes one or more parameters
listing allowable methods.  If the decorator is used multiple times,
any of the methods listed in any of its invocations will be allowed::

    FIXME - example

Some convenient shortcuts are available:

 - allow_GET: allow GET requests; equivalent to allow_method('GET')
 - allow_HEAD: allow HEAD requests; equivalent to allow_method('HEAD')
 - allow_GETHEAD: allow GET or HEAD requests; equivalent to
   allow_method('GET', 'HEAD')
 - allow_POST: allow POST requests; equivalent to allow_method('POST')

If any of these decorators have been used, and the method used is not
listed, the request will return an HTTP 405 or 501 error (depending on
whether the request method is one of the standard HTTP 1.1 methods),
as suggested by the HTTP 1.1 specification.  In this case, the
callable you specified for the URL will not be called.

Query parameters
----------------

FIXME - document more

By default, any query parameters can be supplied to a method - it is
up to the method to check that they are valid.

The parameters allowed at a particular path can be specified using the
"param" decorator.  This performs validation of the parameters, and
will raise a ValidationError if the parameters are not valid (the
default validation error handler will translate this into an HTTP 400
error, but you can override this behaviour with your own handler).

This allows parameters to be taken from the query string part of the
URL, or from POST request bodies (if both are specified, they are
merged, and the POST ones are returned first).

Pathinfo
--------

FIXME - document

.. Warning:: if you've decorated with the @pathinfo decorator, and also decorated with another (non-WSGIWebAPI) decorator, you may find that the method still doesn't seem to accept trailing path information.  This is because ... to fix it call copyprops, or use the wsgiwebapi.decorate decorator.

JSON output
===========

To use the JSON support, your python environment must contain the
``simplejson`` module.

Returning JSON
--------------

Often, you will want to return JSON output from an API.  This can be done very
simply by using the `jsonreturning` decorator.  The return type of a method
wrapped in this decorator should be an object which is capable of being
converted to JSON (typically, a string, integer, or a sequence or dictionary
containing strings, integers, sequences or dictionaries).  The returned value
will automatically be converted to JSON, and the content type will be set
appropriately.

Here's an example of this decorator (which you can see in a cherrypy wrapper at
`<examples/jsonsumapp_cp.py>`_)::

    import wsgiwebapi
    @wsgiwebapi.jsonreturning
    @wsgiwebapi.param("num", 1, None, "^[0-9]+$", None, "A number to be added")
    @wsgiwebapi.allow_GETHEAD
    def calc_sum(request):
        """Return the sum of the values supplied in the `num` parameter.

        """
        res = sum(int(val) for val in request.params.get('num', []))
        return res
    app = wsgiwebapi.make_application({
        'sum': calc_sum
    }, autodoc='doc')

Returning JSONP
---------------

FIXME - document, and add notes on why JSONP might be a bad idea in some cases.


Unicode issues
==============

Ideally, WSGIWebAPI would require all strings supplied to it to be
unicode objects, so that users don't need to worry about character set
issues.  However, HTTP has various limitations on the character sets
used, and it is sometimes desirable to pass through data which cannot
be represented as valid unicode strings, so the API provided by
WSGIWebAPI isn't quite as straightforward as this.

WSGIWebAPI allows byte string objects (ie, "str" objects in Python
2.x, "bytes" objects in Python 3.0 onwards) to be supplied in all
places where a string is supplied by your application.  WSGIWebAPI
will also accept unicode objects in all places where a string is
supplied.  These unicode objects will be encoded appropriately for
passing over HTTP: if this encoding is not possible due to
restrictions in HTTP, an exception will be raised.  In particular:

 - Status codes and the associated reason messages must only use
   characters which can be translated into US-ASCII.

 - For headers, the header name must also be composed of characters
   which can be translated into US-ASCII.  The header value must
   currently also be composed of such characters.  Note - some HTTP
   clients now support encoding parameter values using RFC2231, which
   allows arbitrary unicode values to be supplied in parameters.
   WSGIWebAPI doesn't yet support this.

If a unicode object is supplied for the response body, it will be
converted to UTF-8 for transmission.

Extra utilities
===============

Built-in server
---------------

Testing framework
-----------------

