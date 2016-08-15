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
r"""Test a simple API built with wsgiwebapi.

"""
__docformat__ = "restructuredtext en"

from harness import *
import apps
import wsgiwebapi

class SimpleApiTest(TestCase):
    """Test a simple API build with wsgiwebapi.

    """
    def test_simple(self):
        """Test basic use of the simple API.

        """
        app = wsgiwebapi.make_application(apps.simple(),
                                          logger = wsgiwebapi.SilentLogger)
        r = simulate_get(app, '/')
        self.assertEqual(r.status, u'200 OK')
        self.assertEqual(dict(r.headers)[u'Content-Type'], u'text/plain')
        self.assertEqual(r.body, u'Static')

        r = simulate_get(app, '/foo')
        self.assertEqual(r.status, u'404 Not Found')
        self.assertEqual(dict(r.headers)[u'Content-Type'], u'text/plain')
        self.assertEqual(r.body, u'404 Not Found\nPath \'/foo\' not found')

        r = simulate_get(app, '/2')
        self.assertEqual(r.status, u'200 OK')
        self.assertEqual(dict(r.headers)[u'Content-Type'], u'text/plain')
        self.assertEqual(r.body, u'Static2')

        r = simulate_post(app, '/2', {})
        self.assertEqual(r.status, u'405 Method Not Allowed')
        self.assertEqual(dict(r.headers)[u'Content-Type'], u'text/plain')
        self.assertEqual(dict(r.headers)[u'Allow'], u'GET, HEAD')
        self.assertEqual(r.body, u'405 Method Not Allowed')

        r = simulate_get(app, '/3')
        self.assertEqual(r.status, u'405 Method Not Allowed')
        self.assertEqual(dict(r.headers)[u'Content-Type'], u'text/plain')
        self.assertEqual(dict(r.headers)[u'Allow'], u'POST')
        self.assertEqual(r.body, u'405 Method Not Allowed')

        r = simulate_post(app, '/3', {})
        self.assertEqual(r.status, u'200 OK')
        self.assertEqual(dict(r.headers)[u'Content-Type'], u'text/plain')
        self.assertEqual(r.body, u'Static3')

        r = simulate_post(app, '/4', {})
        self.assertEqual(r.status, u'200 OK')
        self.assertEqual(dict(r.headers)[u'Content-Type'], u'text/plain')
        self.assertEqual(r.body, u'Static4')

        r = simulate_get(app, '/5')
        self.assertEqual(r.status, u'200 OK')
        self.assertEqual(dict(r.headers)[u'Content-Type'], u'text/javascript')
        self.assertEqual(r.body, u'"Static5"')

        r = simulate_get(app, '/5/')
        self.assertEqual(r.status, u'404 Not Found')

if __name__ == '__main__': main()
# vim: set fileencoding=utf-8 :
