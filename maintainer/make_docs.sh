#!/bin/sh

epydoc -o ../docs/epydoc --exclude unittests --exclude testsupport --no-private --name="WSGIWebAPI" --parse-only -u "../index.html" -q ../wsgiwebapi
rst2html --link-stylesheet --stylesheet=media/docs.css ../docs/introduction.rst ../docs/introduction.html
rst2html --link-stylesheet --stylesheet=media/docs.css ../docs/reference.rst ../docs/reference.html
