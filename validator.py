#!/usr/bin/env python

import os
import sys
from HTMLParser import HTMLParser

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


class HTMLTag:
    
    IGNORED = ['title', 'alt']
    
    def __init__(self, name, attrs, is_start_tag):
        self.name = name
        self.attrs = attrs
        self.is_start_tag = is_start_tag
        
        # cleanup attrs and remove attributes that the translation is allowed to change
        if self.attrs is not None:
            filtered = []
            for (k,v) in self.attrs:
                if k not in HTMLTag.IGNORED:
                    filtered.append((k,v))
            self.attrs = filtered

class TagList (HTMLParser, list):
    '''Simple HTMLParser that stores all parsed tags and their attributes as a list.'''
    
    def __init__ (self, html):
        super(TagList, self).__init__()
        self.feed(html)
        
    def handle_starttag(self, tag, attrs):
        self.append(HTMLTag(tag, attrs, True))

    def handle_endtag(self, tag):
        self.append(HTMLTag(tag, None, False))
        
        
class PoValidator:
    '''Validates HTML content in PO files and compares the translated strings to the original strings'''
    
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
        try:
            fixed_html, errors = _elementtidy.fixup(text)
        except UnicodeEncodeError:
            print 'Improper encoding settings. Please add the following lines to python2.6/sitecustomize.py:'
            print '    import sys'
            print "    sys.setdefaultencoding('iso-8859-1')"
            sys.exit(1)
        errors_list = errors.strip().split("\n")
        errors_list.pop(0)
        return errors_list

    def validate (self, filename):
        '''loads, parses, and validates all html content in a .po file'''
        po = polib.pofile(filename)
        no_errors = True
        
        for entry in po.translated_entries():
            errors = self._validate_html(entry.msgstr)
            if errors:
                no_errors = False
                print 'Error in string "%s"' % (entry.msgstr,)
                for e in errors:
                    print '\n'.join(e.split('-')[1:])
                print '\n'
            
            # If there are no errors in the string, then compare it to the original
            else:
                translationTags = TagList(entry.msgstr)
                originalTags = TagList(entry.msgid)
                mismatch = False
                
                while len(translationTags) and len(originalTags):
                    a = translationTags.pop(0)
                    b = originalTags.pop(0)
                    
                    if a.name != b.name or a.attrs != b.attrs or a.is_start_tag != b.is_start_tag:
                        mismatch = True
                
                if mismatch or len(translationTags) != 0 or len(originalTags) != 0:
                    no_errors = False
                    print "In the following entry, the translation's HTML markup doesn't match the original string:"
                    print entry
        
        if no_errors:
            print 'File validated without errors.'
            
if __name__ == '__main__':
    if args.FILE is not None:
        file = os.path.abspath(args.FILE)
    
    validator = PoValidator()
    validator.validate(file)
