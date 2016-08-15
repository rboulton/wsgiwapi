Introduction to WSGIWebAPI
==========================

WSGIWebAPI is intended to make it extremely easy to make web APIs based on
Python programs.  With WSIGWebAPI, it should take only a few minutes to
produce a working, and documented, API for your code.

Here's a simple WSGIWebAPI application::

    import wsgiwebapi
    app = wsgiwebapi.make_application({
        '': lambda x: wsgiwebapi.Response('My First WSGIWebAPI application!'),
    })

The ``app`` object produced by this code is a class implementing the WSGI
protocol, as defined by `PEP 333 <http://www.python.org/dev/peps/pep-0333/>`_.
This can be passed to any WSGI web server to publish the API, but for
convenience WSGIWebAPI includes a copy of the standalone WSGI server from
CherryPy.  A server for the application can be created and started by::

    server = wsgiwebapi.make_server(app(), ('0.0.0.0', 8080))
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()

Note that the return value of `make_application()` is a class, but the server
needs to be passed an instance of that class.

See `<examples/myfirstapp.py>`_ for a ready-to-run copy of the code so far.
If you run this application, and then visit `<http://127.0.0.1:8080/>`_ you
will see the output of the application: a text/plain page containing "My First
WSGIWebAPI application!".

A more useful application
=========================

Starting with myfirstapp.py, replace the lines which create the app object
with the following to produce a more "useful" application (this can be found as
`<examples/sumapp.py>`_)::

    import wsgiwebapi
    def calc_sum(request):
        """Return the sum of the values supplied in the `num` parameter.

        """
        res = sum(int(val) for val in request.params.get('num', []))
        return wsgiwebapi.Response(str(res))
    app = wsgiwebapi.make_application({
        'sum': calc_sum
    }, autodoc='doc')

In this example, we've changed the lambda into a full function definition, for
easier reading.  The `request` parameter is an object which provides easy
access to the parameters passed in the request: one of the facilities it
provides is the `params` member, which is a dictionary of the query parameters
passed.  Each query parameter may occur multiple times, so the params
dictionary contains a list of values for each parameter which was specified,
even if the parameter was only specified once.  Our application adds up the
values in the `num` query parameter, and returns their sum, as a string wrapped
in a `wsgiwebapi.Response` object.

All the callables listed in the dict supplied to `make_application()` must
return `wsgiwebapi.Response` objects.  These provide a rich set of methods
allowing the headers and status code of a response type to be controlled.
However, here we're just setting the body of the response type, and leaving the
response status as the default ("200 OK"), and the "Content Type" of the
response as the default ("text/plain").

We've changed the key in the `make_application()` call from '' to 'sum'.  This
key represents the path component used to address the callable.  If we run the
application now, we'll find that `<http://127.0.0.1:8080/>`_ returns a "404 Not
Found" error status; any path not listed in the dictionary passed to
`make_application()` automatically returns a 404 error.  However,
`<http://127.0.0.1:8080/sum>`_ returns 0, and
`<http://127.0.0.1:8080/sum?num=2&num=3>`_ returns 5, as expected.

The other new feature introduced in this example is the `autodoc` parameter
supplied to the `make_application()` call.  This specifies a path at which
documentation of the API will be made available.  If you look at
`<http://127.0.0.1:8080/doc>`_, you will be able to browse documentation of the
API.  The description of the API methods is taken from the doccomments of the
corresponding callables, which should make it easy to keep the documentation
up-to-date as the API changes.

Decorating the methods
======================

WSGIWebAPI provides a set of useful decorators, to make it easy to produce
certain types of API.  You don't need to use any of these, but they will often
make it easier to produce a clean API.  The WSGIWebAPI decorators can be
applied in any order: they all operate by adding some extra properties to the
API, and replacing the API method with a special wrapper which interprets these
properties.

Decorators are available to perform parameter validation, check the HTTP
methods being used to access your API, and support different response formats
(currently, JSON and "JSONP" are supported).  Here's an example similar to our
previous example, but using decorators to return a JSON formatted result, check
that the "num" parameter is valid and supplied at least once, and ensuring that
the HTTP method used was GET or HEAD.  A complete ready-to-run script
containing this example is available at `<examples/jsonsumapp.py>`_::

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

Accessing path information
==========================

With the previous example, a request to `<http://127.0.0.1:8080/sum/foo>` would
return a "404 Not Found" error.  By default, WSGIWebAPI applications will raise
this error if there are any path components after a mapping to a callable has
been found.  However, it is sometimes desirable to allow extra information to
be passed on the URL path, so WSGIWebAPI provides a decorator (``pathinfo``)
which makes the path information available in ``request.pathinfo``.

The ``pathinfo`` decorator has support for validating the path information, for
providing named access to the path information, and for default values.  This
decorator also works with the autodoc feature to provide documentation of the
path information supported.

For example, if we wanted to change the previous example to allow a path
component after "/sum" to specify whether to add or multiply the values, and
then to read the numbers from subsequent path components rather than the query
string, we could do the following (note that the ``tail`` argument to the
pathinfo decorator, which describes the validation pattern to apply to training
path components, is very similar to the arguments applied to the ``param``
decorator in the earlier example)::

    import wsgiwebapi
    @wsgiwebapi.jsonreturning
    @wsgiwebapi.allow_GETHEAD
    @wsgiwebapi.pathinfo(
                         ("op", '^[a-z]+$', None,),
                         tail=(1, None, "^[0-9]+$", None, "A number to be added")
                        )
    def calc_sum(request):
        """Return the sum of the values supplied in the `num` parameter.

        """
        op = request.pathinfo.get('op')
        nums = request.pathinfo.tail
        if op == 'add':
            res = sum(int(val) for val in nums)
        elif op == 'mul':
            res = reduce(lambda x, y: x * y, (int(val) for val in nums))
        else:
            raise wsgiwebapi.HTTPNotFound(request.path)
        return res
    app = wsgiwebapi.make_application({
        'sum': calc_sum
    }, autodoc='doc')

With this code, `<http://127.0.0.1:8080/sum/add/2/3>`_ returns 5, and
`<http://127.0.0.1:8080/sum/mul/2/3>`_ returns 6.

Returning errors
================

The `wsgiwebapi.Response` object allows the HTTP status code to be set (and
knows some standard reason messages for all the standard HTTP 1.1 status codes,
so you can just set the numeric code if you're happy to use the standard reason
messages).  This allows you to return any HTTP status code you like, to
represent errors (or redirects, etc).

However, it is often convenient to be able to use exceptions to report errors.
To enable this, WSGIWebAPI provides `wsgiwebapi.HTTPError`, which is a subclass
of `wsgiwebapi.Response`, and also of the standard `Exception` class.  This can
be thrown, and provided with whatever status code and message body you like.

For even greater convenience, there are also some subclasses for specific
error conditions:

 - `wsgiwebapi.HTTPServerError`: thrown to report "500 Server Error"
 - `wsgiwebapi.HTTPNotFound`: thrown to report a "404 Not Found" error.  
 - `wsgiwebapi.HTTPMethodNotAllowed`: thrown to report a disallowed method.
   Takes the method which was requested, and a list of the allowed methods for
   this URL.

If your callable raises any other exception, the WSGI application will return a
"500 Server Error".

Unicode issues
==============

Ideally, WSGIWebAPI would require all strings supplied to it to be unicode
objects, so that users don't need to worry about character set issues.
However, HTTP has various limitations on the character sets used, and it is
sometimes desirable to pass through data which cannot be represented as valid
unicode strings, so the API provided by WSGIWebAPI isn't quite as
straightforward as this.

WSGIWebAPI allows byte string objects (ie, "str" objects in Python 2.x, "bytes"
objects in Python 3.0 onwards) to be supplied in all places where a string is
supplied by your application.  WSGIWebAPI will also accept unicode objects in
all places where a string is supplied.  These unicode objects will be encoded
appropriately for passing over HTTP: if this encoding is not possible due to
restrictions in HTTP, an exception will be raised.  In particular:

 - Status codes and the associated reason messages must only use characters
   which can be translated into US-ASCII.

 - For headers, the header name must also be composed of characters which can
   be translated into US-ASCII.  The header value must currently also be
   composed of such characters.
   Note - some HTTP clients now support encoding parameter values using
   RFC2231, which allows arbitrary unicode values to be supplied in parameters.
   WSGIWebAPI doesn't yet support this.

If a unicode object is supplied for the response body, it will be converted to
UTF-8 for transmission.
