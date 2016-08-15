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
r"""Test the wsgiwapi decorators.

"""
__docformat__ = "restructuredtext en"

from harness import *
import wsgiwapi

class DecoratorTest(TestCase):
    """Test some decorators.

    """
    def test_decorate(self):
        """Test the decorate decorator.

        """
        def mydecor(fn):
            def myreq(request):
                return wsgiwapi.Response(fn(request))
            return myreq

        @wsgiwapi.allow_GET
        @wsgiwapi.decorate(mydecor)
        @wsgiwapi.noparams
        def foo(request):
            return u'foo'

        app = wsgiwapi.make_application({'': foo},
                                        logger=wsgiwapi.SilentLogger)

        r = simulate_get(app, '/')
        self.assertEqual(r.status, u'200 OK')
        self.assertEqual(dict(r.headers)[u'Content-Type'], u'text/plain')
        self.assertEqual(r.body, u'foo')

        r = simulate_post(app, '/', {})
        self.assertEqual(r.status, u'405 Method Not Allowed')

        r = simulate_get(app, '/?a=1')
        self.assertEqual(r.status, u'400 Bad Request')
        self.assertEqual(dict(r.headers)[u'Content-Type'], u'text/plain')
        self.assertEqual(r.body, u'Validation Error: This resource does not '
                         'accept parameters')

if __name__ == '__main__': main()
# vim: set fileencoding=utf-8 :
