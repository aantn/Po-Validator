#!/usr/bin/env python

import sys

try:
    import _elementtidy
except ImportError:
    print 'Please install the python bindings for tidy. On Ubuntu, run "sudo apt-get install python-elementtidy"'
    sys.exit(1)

try:
    import polib
except ImportError:
    print 'Please install polib. On Ubuntu, run "sudo apt-get install python-polib"'

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
    validator = PoValidator()
    validator.validate_po('/home/natan/Downloads/en_GB.po')
