#!/usr/bin/env python

import os
import sys

try:
    import _elementtidy
except ImportError:
    print 'Please install the python bindings for tidy.\nOn Ubuntu, run "sudo apt-get install python-elementtidy"'
    sys.exit(1)

try:
    import polib
except ImportError:
    print 'Please install polib.\nOn Ubuntu, run "sudo apt-get install python-polib"'

try:
    import argparse
except ImportError:
    print 'You\'re running an older version of Python that doesn\'t include the argparse module.\n' + \
             'You can install it by running "sudo easy_install argparse"\n' + \
             'On Ubuntu, run "sudo apt-get install python-argparse"'
    sys.exit()

# Setup command line arguments
parser = argparse.ArgumentParser(description='A teansy python script for validating HTML content in PO files')
parser.add_argument("FILE", default=None, help="a PO file to validate")
args = parser.parse_args()

class PoValidator:

    # TODO: We should use a proper doctype, but the following makes
    # _elementtidy segfault
    #HEADER = r'''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
    #                    "http://www.w3.org/TR/html4/strict.dtd">
    HEADER = r'''<html>
                    <head>
                        <title>Test title</title>
                    </head>
                    <body>'''
    FOOTER = r'''</body></html>'''

    def _validate_html (self, html):
        '''validate an html string with tidy and return a list of errors'''
        text = PoValidator.HEADER + html + PoValidator.FOOTER
        fixed_html, errors = _elementtidy.fixup(text)
        return errors.strip().split("\n")

    def validate_po (self, filename):
        '''loads, parses, and validates all html content in a .po file'''
        po = polib.pofile(filename)
        for entry in po.translated_entries():
            msg = entry.msgstr
            errors = self._validate_html(msg)
            if len(errors) > 1:
                print 'Error in string "%s"' % (msg,)
                for error in errors[1:]:
                    print '\n'.join(error.split('-')[1:])
                print '\n'

if __name__ == '__main__':
    if args.FILE is not None:
        file = os.path.abspath(args.FILE)
    validator = PoValidator()
    validator.validate_po(file)
