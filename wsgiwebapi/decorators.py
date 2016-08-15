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
r"""Decorators of WSGIWebAPI callables.

"""
__docformat__ = "restructuredtext en"

from wsgisupport import Request, Response, HTTPMethodNotAllowed, HTTPError
import re

def _apply_request_checks_and_transforms(request, props):
    """Apply all the checks and transforms listed in props to a request.

    This is typically called from a decorator, and the props are read from the
    decorated function.

    """
    request_filters = props.get('request_filters', [])
    for request_filter in request_filters:
        request = request_filter(request, props)
    return request

def _apply_response_checks_and_transforms(request, response, props):
    """Apply all the checks and transforms listed in props to a response.

    This is typically called from a decorator, and the props are read from the
    decorated function.

    """
    response_filters = props.get('response_filters', [])
    for response_filter in response_filters:
        response = response_filter(request, response, props)
    return response

def _decorate_once(fn):
    """Decorate a function with the standard decorator pair, if not already decorated.

    """
    if hasattr(fn, '_wsgiwebapi_props'):
        props = fn._wsgiwebapi_props
        if props.get('decorated', False) == True:
            return fn, props
    props = {'decorated': True}
    def res(*args, **kwargs):
        if isinstance(args[0], Request):
            request = args[0]
            have_self = False
        else:
            assert isinstance(args[1], Request)
            request = args[1]
            have_self = True

        if request._handler_props is not props:
            raise RuntimeError("Handler properties do not match decorated properties.  Probably missing call to wsgiwebapi.copyprops.")

        request = _apply_request_checks_and_transforms(request, props)

        if not have_self:
            args = [request]
            args.extend(args[1:])
        else:
            args = [args[0], request]
            args.extend(args[2:])

        response = fn(*args, **kwargs)
        return _apply_response_checks_and_transforms(request, response, props)
    res.__doc__ = fn.__doc__
    res.__name__ = fn.__name__
    res.__dict__.update(fn.__dict__)
    res._wsgiwebapi_props = props
    return res, props

def _get_props(fn):
    """Get the WSGIWebAPI properties from an object.

    """
    if not hasattr(fn, '_wsgiwebapi_props'):
        return None
    return fn._wsgiwebapi_props

def jsonreturning(fn):
    """Decorator to wrap function's return value as JSON.

    Before the decorator is applied, the function should return a structure to
    be converted to JSON.  The decorator will set the content_type
    automatically (to text/javascript).

    """
    fn, props = _decorate_once(fn)
    import jsonsupport
    response_filters = props.setdefault('response_filters', [])
    response_filters.append(jsonsupport.convert_to_json)
    props['return_type'] = 'JSON'
    return fn

def jsonpreturning(paramname='jsonp', valid=r'^[a-zA-Z._\[\]]*$'):
    """Decorator to add JSONP support to an API function.

    This adds a query parameter (by default, ``jsonp``, but this may be altered
    with the `paramname` parameter) to the function.  If the parameter is not
    supplied, the return value is a plain JSON object, otherwise the return
    value is preceded by the value in the parameter and an open bracket, and
    followed by a close bracket.  The parameter must not be specified multiple
    times in a single request.

    By default, the ``jsonp`` parameter may only contain upper and lowercase
    ASCII alphabetic characters (A-Z, a-z), numbers (0-9), full stops (.),
    underscores (_), and brackets ([ and ]), but this may be altered by setting
    the `valid` parameter to a string containing a regular expression matching
    the valid parameter values.  To avoid performing any validation of the
    value of the ``jsonp`` parameter, set the `valid` parameter to None.
    
    See http://bob.pythonmac.org/archives/2005/12/05/remote-json-jsonp/ for
    some of the rationale behind JSONP support.

    """
    def deco(fn):
        fn, props = _decorate_once(fn)
        import jsonsupport
        response_filters = props.setdefault('response_filters', [])
        response_filters.append(jsonsupport.convert_to_jsonp)
        props['return_type'] = 'JSONP'
        props['return_JSONP_paramname'] = paramname
        props['return_JSONP_valid'] = valid
        return fn
    return deco

def _check_allowed_methods(request, props):
    """Perform check that method is allowed.

    """
    allowed_methods = props.get('allowed_methods', None)
    if allowed_methods is not None and request.method not in allowed_methods:
        raise HTTPMethodNotAllowed(request.method, allowed_methods)
    return request

def allow_method(method_type, *other_methods):
    """Decorator to restrict the methods allowed to a specific set.

    May be applied multiple times, to allow more than one method to be allowed.

    If applied at all, any methods other than those specified will result in a
    405 or 501 error (depending whether the exception is one of the standard
    known methods).

    (This stores the allowed methods in an attribute of the decorated function,
    so tht repeated application can allow 

    """

    def deco(fn):
        fn, props = _decorate_once(fn)
        request_filters = props.setdefault('request_filters', [])
        if _check_allowed_methods not in request_filters:
            request_filters.append(_check_allowed_methods)
        allowed = props.setdefault('allowed_methods', set())
        allowed.add(method_type)
        for method in other_methods:
            allowed.add(method)
        return fn
    return deco

allow_GET = allow_method('GET')
allow_GET.__doc__ = """Directly equivalent to allow_method('GET')."""
allow_HEAD = allow_method('HEAD')
allow_HEAD.__doc__ = """Directly equivalent to allow_method('HEAD')."""
allow_GETHEAD = allow_method('GET', 'HEAD')
allow_GETHEAD.__doc__ = "Directly equivalent to allow_method('GET', 'HEAD')."
allow_POST = allow_method('POST')
allow_POST.__doc__ = """Directly equivalent to allow_method('POST')."""

def param(paramname, minreps=None, maxreps=None, pattern=None, default=None, doc=None):
    """Decorator to add parameter validation.
    
    If this is used at all, the ``noparams`` decorator may not also be used.

    This decorator may only be used once for each parameter name.

     - `paramname` is required - the name of the parameter in
       ``request.params``.
     - `minreps`: the minimum number of times the parameter must be specified.
       If omitted or None, the parameter need not be specified.  (Note that, if
       default is specified, it is always valid to supply the parameter exactly
       0 times, regardless of the setting of this parameter.)
     - `maxreps`: the maximum number of times the parameter may be specified.
       If omitted or None, there is no limit on the number of times the
       parameter may be specified.
     - `pattern`: a (python regular expression) pattern which the parameter
       must match.  If None, no validation is performed.
     - `default`: a default value for the parameter list.  Note - this is used
       only if the parameter doesn't occur at all, and is simply entered into
       ``request.params`` instead of the parameter (it should usually be a
       sequence, to make the normal values placed into ``request.params``).
     - `doc`: a documentation string for the parameter.

    """
    import validation
    def deco(fn):
        fn, props = _decorate_once(fn)
        request_filters = props.setdefault('request_filters', [])
        if validation.check_no_params in request_filters:
            raise RuntimeError("Can't decorate with param and noparams")
        if validation.check_valid_params not in request_filters:
            request_filters.append(validation.check_valid_params)
        constraints = props.setdefault('valid_params', {})
        if paramname in constraints:
            raise RuntimeError("Already set validation constraints for "
                               "parameter '%s'" % paramname)
        compiled_pattern = None
        if pattern is not None:
            compiled_pattern = re.compile(pattern)
        constraints[paramname] = (minreps, maxreps, pattern,
                                  compiled_pattern, default, doc)
        return fn
    return deco

def noparams(fn):
    """Decorator to indicate that no parameters may be supplied.

    """
    import validation
    fn, props = _decorate_once(fn)
    request_filters = props.setdefault('request_filters', [])
    if validation.check_valid_params in request_filters:
        raise RuntimeError("Can't decorate with param and noparams")
    if validation.check_no_params not in request_filters:
        request_filters.append(validation.check_no_params)
    props['valid_params'] = {}
    return fn

def pathinfo(*args, **kwargs):
    """Decorator to indicate the parameter names allowed in pathinfo.

    """
    import validation
    tail = kwargs.get('tail', None)
    # Check that there aren't any other keyword arguments.
    for key in kwargs:
        if key not in ('tail',):
            raise TypeError("pathinfo decorator got an unexpected keyword"
                            " argument '%s'" % key)

    # Parse the rules
    param_rules, tail_rules = validation.parse_pathinfo_rules(args, tail)

    def deco(fn):
        fn, props = _decorate_once(fn)

        # Check that we only decorate once.
        if props.get('pathinfo_decorated'):
            raise RuntimeError("Can't decorate with pathinfo twice")
        props['pathinfo_decorated'] = True

        if len(args) == 0 and tail_rules is None:
            # Don't set pathinfo_allow; use default behaviour of raising
            # HTTPNotFound if pathinfo is supplied.
            return fn

        # Enable checking of path information (rather, disable automatic
        # complaint).
        props['pathinfo_allow'] = True

        # Store the allowed parameters.
        props['pathinfo_params_rules'] = param_rules
        props['pathinfo_tail_rules'] = tail_rules

        # Add validation filter to request_filters.
        request_filters = props.setdefault('request_filters', [])
        if validation.check_pathinfo not in request_filters:
            request_filters.append(validation.check_pathinfo)

        return fn
    return deco

def copyprops(original_fn, decorated_fn):
    """Copy the WSGIWebAPI properties from a function to a decorated function.

    If you write your own decorators and apply them to WSGIWebAPI decorated
    functions, you should call this method in your decorator to copy the
    WSGIWebAPI properties into your decorated function.  If you don't do this,
    you may get confusing failures, such as pathinfo not being allowed.

    """
    if hasattr(original_fn, '_wsgiwebapi_props'):
        decorated_fn._wsgiwebapi_props = original_fn._wsgiwebapi_props
    if hasattr(original_fn, '__doc__'):
        decorated_fn.__doc__ = original_fn.__doc__

def decorate(decorator):
    """Apply a decorator, but also copy the WSGIWebAPI properties across.

    To use this, pass the decorator you wish to apply as a parameter to this
    decorator.  The returned decorator will apply this decorator, and then copy
    the WSGIWebAPI properties across.

    """
    def deco(fn):
        newfn = decorator(fn)
        copyprops(fn, newfn)
        return newfn
    return deco

# vim: set fileencoding=utf-8 :
