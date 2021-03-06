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
r"""Support for converting responses to JSON formats.

"""
__docformat__ = "restructuredtext en"

have_json = False
try:
    # json is a built-in module from python 2.6 onwards
    import json
    if hasattr(json, 'dumps'):
        have_json = True
    else:
        del json
except ImportError:
    pass
if not have_json:
    import simplejson as json

from application import JsonResponse
from wsgisupport import Response

def convert_to_json(request, response, props,
                    content_type="application/json"):
    """Convert a response to JSON.

    The supplied content type will be overridden by any type set in the
    response object.

    """
    jsonobj = response
    status = 200

    if isinstance(response, JsonResponse):
        jsonobj = response.jsonobj
        if response.status_code is not None:
            status = response.status_code
        if response.content_type is not None:
            content_type = response.content_type

    return Response(json.dumps(jsonobj), status, content_type)

def convert_to_jsonp(request, response, props):
    """Convert a response to JSONP, according to the props.

    """
    # FIXME - do something about the character set.
    # First comment on http://simonwillison.net/2009/Feb/6/json/ implies that
    # it needs to be ascii to work correctly with IE.
    response = convert_to_json(request, response, props,
                               content_type='text/javacsript')

    paramname = props['return_JSONP_paramname']
    jsonp = request.validated.get(paramname)
    if jsonp != '':
        response.body = jsonp + '(' + response.body + ')'
    return response

def parse_json_body(request):
    """Parse json in a request body.

    """
    request.json = json.loads(request.raw_post_data)

# vim: set fileencoding=utf-8 :
