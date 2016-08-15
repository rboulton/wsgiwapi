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
r"""Applications used by tests.

"""
__docformat__ = "restructuredtext en"

from harness import *

def simple():
    def staticreturn(request):
        return wsgiwebapi.Response('Static')
    @wsgiwebapi.allow_GET
    @wsgiwebapi.allow_HEAD
    def staticreturn2(request):
        return wsgiwebapi.Response('Static2')
    @wsgiwebapi.allow_POST
    def staticreturn3(request):
        return wsgiwebapi.Response('Static3')
    @wsgiwebapi.allow_method('GET', 'POST')
    def staticreturn4(request):
        return wsgiwebapi.Response('Static4')
    @wsgiwebapi.jsonreturning
    def staticreturn5(request):
        return 'Static5'

    @wsgiwebapi.noparams
    def staticreturn6(request):
        return wsgiwebapi.Response('Static6')

    @wsgiwebapi.param('foo', 2, 2, None, None)
    def staticreturn7(request):
        return wsgiwebapi.Response('Static7')

    @wsgiwebapi.param('foo', 2, 2, None, ['bar'])
    def mirror8(request):
        return wsgiwebapi.Response(u','.join(request.params['foo']))
    return {
                '': staticreturn,
                '2': staticreturn2,
                '3': staticreturn3,
                '4': staticreturn4,
                '5': staticreturn5,
                '6': staticreturn6,
                '7': staticreturn7,
                '8': mirror8,
    }
