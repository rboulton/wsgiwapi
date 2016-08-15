#!/usr/bin/env python

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
r"""Test postdata support.

"""
__docformat__ = "restructuredtext en"

from harness import *
import wsgiwapi

class PostdataTest(TestCase):
    """Test validation support.

    """
    def test_default(self):
        """Test basic use of the default postdata handler.

        """
        def app_fn1(request):
            return str(request.params.get('foo'))
        
        app = makeapp({'': app_fn1})
        r = simulate_post(app, '/', {'foo': 'some data'})
        self.assertEqual(r.status, u'200 OK')
        self.assertEqual(dict(r.headers)[u'Content-Type'], u'text/plain')
        self.assertEqual(r.body, u"['some data']")

    def test_json(self):
        """Test use of the default postdata handler with JSON body.

        """
        def app_fn1(request):
            return request.json[0] + request.json[1]

        app = makeapp({'': app_fn1})
        r = simulate_post(app, '/', ['cat', 'dog'], 'text/json')
        self.assertEqual(r.status, u'200 OK')
        self.assertEqual(dict(r.headers)[u'Content-Type'], u'text/plain')
        self.assertEqual(r.body, u'catdog')

    def test_stream(self):
        """Test the rawinput decorator.

        """
        @wsgiwapi.rawinput
        def app_fn1(request):
            return request.input.read(request.content_length).upper()

        app = makeapp({'': app_fn1})
        data = 'and now for something completely different'
        r = simulate_post(app, '/', data, 'text/plain')
        self.assertEqual(r.status, u'200 OK')
        self.assertEqual(dict(r.headers)[u'Content-Type'], u'text/plain')
        self.assertEqual(r.body, data.upper())

if __name__ == '__main__': main()
# vim: set fileencoding=utf-8 :
