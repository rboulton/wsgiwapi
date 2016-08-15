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
r"""Test handling of flat urls in the application specification.

"""
__docformat__ = "restructuredtext en"

from harness import *
import wsgiwapi

def handler(prefix=''):
    def res(request):
        return prefix + request.path + ":" + str(request.pathinfo) + ":" + \
            '/'.join(request.pathinfo.tail)
    return res

class FlatUrlsTest(TestCase):
    """Test handling of flat urls in application specification.

    """

    def test_one_path(self):
        """An application with one path.

        """
        app = makeapp({'bar': handler()})
        r = simulate_get(app, '/bar')
        self.assertEqual(r.status, u'200 OK')
        self.assertEqual(r.body, u'/bar:{}:')

        r = simulate_get(app, '/bar/')
        self.assertEqual(r.status, u'404 Not Found')
        self.assertEqual(r.body, u"404 Not Found\nPath '/bar/' not found")

    def test_two_paths(self):
        """An application with two paths sharing an initial prefix.

        """
        app = makeapp({'bar/foo': handler('A'), 'bar/baz': handler('B')})
        r = simulate_get(app, '/bar')
        self.assertEqual(r.status, u'404 Not Found')
        r = simulate_get(app, '/bar/baz')
        self.assertEqual(r.status, u'200 OK')
        self.assertEqual(r.body, u'B/bar/baz:{}:')

    def test_subpath_flat(self):
        """An application with flat paths which are subpaths of each other.

        """
        app = makeapp({
            'bar': handler('A'),
            'bar/': handler('B'),
        })
        app = makeapp({
            'bar': handler('A'),
            'bar/': handler('B'),
            'bar/baz': handler('C'),
        })

        r = simulate_get(app, '/bar')
        self.assertEqual(r.status, u'200 OK')
        self.assertEqual(r.body, u'A/bar:{}:')

        r = simulate_get(app, '/bar/')
        self.assertEqual(r.status, u'200 OK')
        self.assertEqual(r.body, u'B/bar/:{}:')

        r = simulate_get(app, '/bar/baz')
        self.assertEqual(r.status, u'200 OK')
        self.assertEqual(r.body, u'C/bar/baz:{}:')

    def test_subpath_notflat(self):
        """An application with non-flat paths which are subpaths of each other.

        """

        app = makeapp({
            'bar': {None: handler('A'),
                    '': handler('B'),
                    'baz': handler('C'),
            },
        })

        r = simulate_get(app, '/bar')
        self.assertEqual(r.status, u'200 OK')
        self.assertEqual(r.body, u'A/bar:{}:')

        r = simulate_get(app, '/bar/')
        self.assertEqual(r.status, u'200 OK')
        self.assertEqual(r.body, u'B/bar/:{}:')

        r = simulate_get(app, '/bar/baz')
        self.assertEqual(r.status, u'200 OK')
        self.assertEqual(r.body, u'C/bar/baz:{}:')

    def test_duplicated_component(self):
        """An application with two paths sharing an initial prefix.

        """
        self.assertRaisesMessage(TypeError,
                                 "duplicated component at end of path 'bar/'",
                                 makeapp,
                                 {'bar/': handler('A'),
                                  'bar': {'': handler('B')}})

        # Test things with a *
        # Test things with a * which conflict

if __name__ == '__main__': main()
# vim: set fileencoding=utf-8 :
