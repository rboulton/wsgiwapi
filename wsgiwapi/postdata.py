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
r"""Processing for POST and PUT data.

"""
__docformat__ = "restructuredtext en"

import cgi
import StringIO

import overlaydict

def read_raw_post_data(request):
    """Read data from the request input and store in raw_post_data attr.
    
    """
    if request.content_length > 0:
        content_length = request.content_length
        buf = StringIO.StringIO()
        while content_length > 0:
            chunk = request.input.read(min(content_length, 65536))
            if not chunk:
                break
            buf.write(chunk)
            content_length -= len(chunk)
        request.raw_post_data = buf.getvalue()
        buf.close()
    else:
        request.raw_post_data = ''

def process_default(request):
    """Read and parse request body and add to request params.
    
    """
    read_raw_post_data(request)
    if request.content_type == 'application/x-www-form-urlencoded':
        request.POST = cgi.parse_qs(request.raw_post_data)
        request.params = overlaydict.OverlayDict(request.POST, request.GET)
    elif request.content_type == 'text/json':
        import jsonsupport
        jsonsupport.parse_json_body(request)

# vim: set fileencoding=utf-8 :
