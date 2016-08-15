# Copyright (c) 2009 Richard Boulton
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
r"""Support utilities for building a WSGI application.

"""
__docformat__ = "restructuredtext en"

import cgi
import re
import StringIO
import overlaydict
import pathinfo

import reason_phrases

def to_uni(text):
    """Convert text into unicode, if it's not already unicode.

    """
    if isinstance(text, str):
        return text.decode('utf-8')
    return text

def method_known(method):
    """Return True iff the method string is one of the known HTTP methods.

    """
    return method in (
                      'OPTIONS',
                      'GET',
                      'HEAD',
                      'POST',
                      'PUT',
                      'DELETE',
                      'TRACE',
                      'CONNECT',
    )

class Request(object):
    """Request object, used to represent a request via WSGI.

    """
    def __init__(self, environ):
        self.path = to_uni(environ.get('PATH_INFO', u'/'))
        if not self.path:
            self.path = u'/'
        self.path_components = self.path.split(u'/')[1:]

        # FIXME - set method
        self.method = environ['REQUEST_METHOD'].upper()

        self.GET = cgi.parse_qs(environ.get('QUERY_STRING', ''))
        self.POST = {}

        if self.method == 'POST':
            try:
                content_length = int(environ.get('CONTENT_LENGTH', 0))
            except (ValueError, TypeError):
                content_length = 0
            if content_length > 0:
                fd = environ['wsgi.input']
                buf = StringIO.StringIO()
                while content_length > 0:
                    chunk = fd.read(min(content_length, 65536))
                    if not chunk:
                        break
                    buf.write(chunk)
                    content_length -= len(chunk)
                self.raw_post_data = buf.getvalue()
                buf.close()
            else:
                self.raw_post_data = ''
            self.POST = cgi.parse_qs(self.raw_post_data)

        self.params = overlaydict.OverlayDict(self.POST, self.GET)

    def _set_handler_props(self, handler_props):
        """Set the WSGIWebAPI properties found on the handler.

        This is used to warn when the properties on the handler do not match
        those used by the decorator - this is usually due to a second decorator
        dropping the properties.

        """
        self._handler_props = handler_props

    def _set_pathinfo(self, components):
        """Set the path info to a list of components.

        """
        self.pathinfo = pathinfo.PathInfo(components)

    def __str__(self):
        return u"Request(%s, \"%s\", %r)" % (
                                             self.method,
                                             self.path,
                                             self.GET
                                            )

class WSGIResponse(object):
    """Object satisfying the WSGI protocol for making a response.

    This object should be passed the start_reponse parameter (as supplied by
    the WSGI protocol), and the Response object for the response.  The status
    code, headers, and response body will be read from the Response object.

    """
    def __init__(self, start_response, response):
        self.start_response = start_response
        self.response = response

    def __iter__(self):
        self.start_response(self.response.status,
                            self.response.get_encoded_header_list())
        yield self.response.body

    def __len__(self):
        return len(self.response.body)

class Response(object):
    """Response object, used to return stuff via WSGI protocol.

    The Response object is a container fr the details of the response.  It
    contains three significant members:

     - status: The status code (as a string, with code and reason phrase) for
       the reponse.
     - headers: The headers to return about the request.
     - body: The body of the page to return.

    """
    def __init__(self, body=u'', status=200, content_type=u'text/plain'):
        """Create a new Response object.

        The body defaults to being empty, the status defaults to "200 OK", and
        the content_type defaults to 'text/plain'.

         - body: The value to store in the body member.  Defaults to ''.
         - status: The status to set for the response.  May be specified as a
           number, or as a string (optionally, with a reason phrase).  Defaults
           to 200.
         - content_type: The content type to set for the response (as specified
           for the set_content_type() method).  Defaults to 'text/plain'.

        """
        self.body = body
        self.status = status
        self.headers = []
        self.set_content_type(content_type)

    def get_encoded_header_list(self):
        """Get the list of headers, encoded suitably for HTTP.

        This converts the unicode headers to byte strings, suitable for passing
        through HTTP.

        """
        result = []
        for header, value in self.headers:
            if not isinstance(header, str):
                header = header.encode('iso-8859-1')
            if not isinstance(value, str):
                # FIXME - if the header value is not valid iso-8859-1, encode
                # it according to rfc 2231.
                # See: email.utils.encode_rfc2231
                value = value.encode('iso-8859-1')
            result.append((header, value))
        return result

    VALID_STATUS_RE = re.compile(r'[12345][0-9][0-9]')
    def _set_status(self, status):
        if isinstance(status, basestring):
            if len(status) == 3:
                pass # Fall through to string processing.
            elif len(status) <= 4:
                raise ValueError(u"Supplied status (%r) is not valid" % status)
            elif status[3] == ' ':
                if not Response.VALID_STATUS_RE.match(status[:3]):
                    raise ValueError(u"Supplied status (%r) is not valid" %
                                     status)
                if isinstance(status, unicode):
                    try:
                        self._status = status.encode('us-ascii')
                    except UnicodeError, e:
                        e.reason += ", HTTP status line must be " \
                                    "encodable as US-ASCII"
                        raise
                else:
                    self._status = status
                return

        try:
            statusint = int(status)
        except ValueError:
            raise ValueError(u"Supplied status (%r) is not a valid "
                             "status code" % status)

        if statusint < 100 or statusint >= 600:
            raise ValueError(u"Supplied status (%r) is not in valid range" %
                             status)

        try:
            self._status = reason_phrases.phrase_dict[statusint]
        except KeyError:
            raise ValueError(u"Supplied status (%r) is not known" %
                             status)

    def _get_status(self):
        return self._status
    status = property(_get_status, _set_status, doc=
        """The status line to return.

        This may be set to either a string or a number.  If a string, it may
        either contain only the status code, or may contain a reason phrase
        following the status code (separated by a space).
        
        If there is no reason phrase, or the status code is a number, an
        appropriate reason phrase will be used, as long as the status code is
        one of the standard HTTP 1.1 codes.  For non-standard codes, the reason
        phrase must be supplied.

        If `status` is a unicode string, it must contain only characters which
        can be encoded in the US-ASCII character set.  Any other characters
        will cause an exception to be thrown.

        """)

    def set_unique_header(self, header, value):
        """Set the value of a header which should only occur once.

        If any values for the header already exist in the list of headers, they
        are first removed.  The comparison of header names is performed case
        insensitively.

        """
        self.headers = filter(lambda x: x[0].lower() != header.lower(), self.headers)
        self.headers.append((header, value))

    def set_content_type(self, content_type):
        """Set the content type to return.

        """
        self.set_unique_header(u'Content-Type', content_type)

    def __str__(self):
        return "Response(%s, %s, %s)" % (
            self.status,
            self.headers,
            self.body
        )

class HTTPError(Exception, Response):
    def __init__(self, status=500, message=None):
        Exception.__init__(self)
        Response.__init__(self, status=status)
        if message is None:
            self.body = self.status
        else:
            self.body = self.status + "\n" + message

class HTTPNotFound(HTTPError):
    """Raise this exception if a requested resource is not found.

    """
    def __init__(self, path):
        HTTPError.__init__(self, 404, 'Path \'%s\' not found' % path)

class HTTPMethodNotAllowed(HTTPError):
    """Raise this exception if a method which is not allowed was used.

    """
    def __init__(self, request_method, allowed_methods):
        if method_known(request_method):
            HTTPError.__init__(self, 405)
            # Return the list of allowed methods in sorted order
            allow = list(allowed_methods)
            allow.sort()
            self.set_unique_header(u'Allow', u', '.join(allow))
        else:
            raise HTTPError(501, "Request method %s is not implemented" %
                            request_method)

class HTTPServerError(HTTPError):
    """Raise this exception if a server error occurs.

    """
    def __init__(self, body):
        HTTPError.__init__(self, 500, body)

# vim: set fileencoding=utf-8 :
