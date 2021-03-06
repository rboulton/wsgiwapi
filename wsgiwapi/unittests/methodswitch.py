#!/usr/bin/env python

# Copyright (c) 2009 Lemur Consulting Ltd
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
r"""Test the Resource functionality.

"""
__docformat__ = "restructuredtext en"

from harness import *
import wsgiwapi

class ResourceTest(TestCase):
    """Test the Resource class.

    """
    def test_constructor_args(self):
        """Test a Resource constructed using constructor arguments.

        """
        def foo(request):
            return u'foo'

        def bar(request):
            return u'bar'

        app = makeapp({'': wsgiwapi.Resource(foo, bar)})

        r = simulate_get(app, '/')
        self.assertEqual(r.status, u'200 OK')
        self.assertEqual(dict(r.headers)[u'Content-Type'], u'text/plain')
        self.assertEqual(r.body, u'foo')

        r = simulate_post(app, '/', {})
        self.assertEqual(r.status, u'200 OK')
        self.assertEqual(dict(r.headers)[u'Content-Type'], u'text/plain')
        self.assertEqual(r.body, u'bar')

    def test_constructor_args(self):
        """Test a Resource subclass.

        """
        class myres(wsgiwapi.Resource):
            def get(self, request):
                return u'foo'
            def post(self, request):
                return u'bar'

        app = makeapp({'': myres()})

        r = simulate_get(app, '/')
        self.assertEqual(r.status, u'200 OK')
        self.assertEqual(dict(r.headers)[u'Content-Type'], u'text/plain')
        self.assertEqual(r.body, u'foo')

        r = simulate_post(app, '/', {})
        self.assertEqual(r.status, u'200 OK')
        self.assertEqual(dict(r.headers)[u'Content-Type'], u'text/plain')
        self.assertEqual(r.body, u'bar')


    def test_nodefault(self):
        """Test that absense of a handler works.

        """
        def foo(request):
            return u'foo'

        app = makeapp({'': wsgiwapi.Resource(foo)})
                      

        r = simulate_post(app, '/', {})
        self.assertEqual(r.status, u'405 Method Not Allowed')

    def test_pathinfo(self):
        """Test that pathinfo decorator works with Resource.

        """
        @wsgiwapi.pathinfo(('arg1', '^[a-z]+$', None,),)
        def foo(request):
            return request.pathinfo.get('arg1') or ''

        app = makeapp({'foo': wsgiwapi.Resource(foo)})

        r = simulate_get(app, '/foo')
        self.assertEqual(r.status, u'200 OK')
        self.assertEqual(dict(r.headers)[u'Content-Type'], u'text/plain')
        self.assertEqual(r.body, u'')

        r = simulate_get(app, '/foo/wombat')
        self.assertEqual(r.status, u'200 OK')
        self.assertEqual(dict(r.headers)[u'Content-Type'], u'text/plain')
        self.assertEqual(r.body, u'wombat')

if __name__ == '__main__': main()
# vim: set fileencoding=utf-8 :
