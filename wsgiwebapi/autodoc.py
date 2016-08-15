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
r"""Support for automatically documenting an API.

"""
__docformat__ = "restructuredtext en"

import inspect
from decorators import allow_GET
from wsgisupport import Response, HTTPNotFound

def get_property(obj, prop, default):
    if not hasattr(obj, '_wsgiwebapi_props'):
        return default
    return obj._wsgiwebapi_props.get(prop, default)

def make_doc(appurls):
    def build_link_tree(result, urls, leadingcomponents, thiscomponent):
        components = urls.keys()
        components.sort()
        for component in components:
            value = urls[component]
            fullcomponents = leadingcomponents + (component, )
            componentpath = thiscomponent + '/' + component
            result.append('<li><a href="%(component)s">/%(fullpath)s</a>' %
                          {'component': componentpath,
                          'fullpath': '/'.join(fullcomponents)})
            if hasattr(value, '__call__'):
                doc = inspect.getdoc(value)
                if doc is None:
                    doc = ''
                else:
                    doc = doc.partition('\n')[0]
                result.append(' ')
                rettype = get_property(value, 'return_type', '')
                if rettype:
                    result.append("[%s] " % rettype)
                result.append(doc)
            else:
                result.append('<ul>')
                build_link_tree(result, value, fullcomponents, componentpath)
                result.append('</ul>')
            result.append('</li>')

    def path_description(callable):
        """Generate a description of the subsequent path items.

        """
        args, varargs, varkw, defaults = inspect.getargspec(callable)
        args = args[1:]
        if len(args) == 0 and varargs is None:
            return "<li>No extra path components allowed.</li>\n"
        result = []
        for arg in args:
            result.append("<li>%s</li>" % arg)
        if varargs is not None:
            result.append("<li>...</li>")
        return '\n'.join(result)

    def param_descriptions(constraints):
        """Generate a description of the parameters allowed.

        """
        if len(constraints) == 0:
            return "No parameters allowed"
        result = []
        for name, values in constraints.iteritems():
            min, max, pattern, default, doc = values
            required = (default is None and min > 0)
            desc = []
            desc += name
            if required:
                desc += " (required)"
            else:
                desc += " (optional)"

            if doc is not None:
                desc += " - " + doc

            desc += "<br/>\n"

            if min is not None:
                desc += "Minimum occurrences: %d<br/>\n" % min
            if max is not None:
                desc += "Maximum occurrences: %d<br/>\n" % max
            if pattern is not None:
                desc += "Must match %s<br/>\n" % pattern

            result.append("<li>" + ''.join(desc) + "</li>")
        return '\n'.join(result)

    @allow_GET
    def doc(request, *args):
        """Display documentation about the API.

        """
        urls = appurls
        for arg in args:
            if arg not in urls:
                raise HTTPNotFound(request.path)
            if hasattr(urls, '__call__'):
                raise HTTPNotFound(request.path)
            urls = urls[arg]

        if hasattr(urls, '__call__'):
            body = '<pre>%s</pre>' % inspect.getdoc(urls)
            rettype = get_property(urls, 'return_type', '')
            if rettype:
                body += "<b>Return type: %s</b><br/>\n" % rettype
            body += "<b>Path items</b>\n<ul>"
            body += path_description(urls)
            body += "</ul><br/>\n"
            constraints = get_property(urls, 'valid_params', None)
            if constraints != None:
                body += "<b>Parameters:</b>\n<ul>"
                body += param_descriptions(constraints)
                body += "</ul><br/>\n"
            methods = get_property(urls, 'allowed_methods', None)
            if methods != None:
                methods = list(methods)
                methods.sort()
                body += "<b>Allowed methods:</b><ul>\n<li>"
                body += '</li><li>'.join(methods)
                body += "</li></ul><br/>\n"
        else:
            body = ['<ul>']
            thiscomponent = 'doc'
            if len(args):
                thiscomponent = args[-1]
            build_link_tree(body, urls, args, thiscomponent)
            body.append('</ul>')
            body = ''.join(body)
        return Response(
                """<html><head><title>%(reqpath)s</title></head><body>%(body)s</body></html>""" %
                {
                    'reqpath': request.path,
                    'body': body,
                }, content_type='text/html'
            )
    return doc

# vim: set fileencoding=utf-8 :
