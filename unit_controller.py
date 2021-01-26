"""
unit_controller Provides helper functions for interfacing with  from the equations database
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

from config import config
import psycopg2
from psycopg2.extras import NamedTupleCursor
# import textwrap
import subprocess
import os
import argparse
import pprint
from code_auditing import Timer, called_func, calling_func
from PIL import Image
from io import BytesIO


def latex_text_changed(self, text):
    print("LaTeX is:\n\t" + text.toPlainText())

# def main(pattern: str = 'm^3', keep: bool = False, temp_fname: str = "eq_db", version: int = None,
#          aTemplate: str = None, template_file: str = None, verbose: bool = False, show: bool = False):
#
#     if verbose:
#         print('{called} Called By: {caller}'.format(called=called_func(), caller=calling_func()))
#         print('\tArguments:')
#         pprint.PrettyPrinter(indent=12).pprint(locals())
#
#     # Both aTemplate and template_file are provided here, because programmatically specifying the string seems
#     # reasonable in addition to specifying a filename. However, it doesn't seem like a reasonable thing to do on the
#     # command line. It does make sense as a redirected pipe, but I don't have interest in making that happen,
#     # because it's not even my preferred way of interracting
#     if template_file is not None:
#         if verbose:
#             print('Reading LaTeX Template File: {}'.format(template_file))
#         with open(template_file, 'r') as myFile:
#             aTemplate = myFile.readlines()

    # compile_pattern(pattern=pattern, keep=keep, version=version, temp_fname=temp_fname, aTemplate=aTemplate,
    #                 verbose=verbose, show=show)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='LaTeX Template Resources')
    parser.add_argument("--pattern", dest='pattern', help='str: Valid LaTeX Pattern', default="m^3")
    parser.add_argument("--keep", dest='keep', help='bool: Remove Support Files',
                        default=False, action='store_true')
    parser.add_argument("--temp_fname", dest='temp_fname', help='str: Filename Token for Temp Files', default="eq_db")
    parser.add_argument("--version", dest='version',
                        help='int: Template Version. None value or non-existent returns latest',
                        default=None)
    parser.add_argument("--template_file", dest='template_file', help='User specified LaTeX template file',
                        default=None)
    parser.add_argument("--verbose", dest='verbose', help='Output run messages', action='store_true')
    parser.add_argument("--show", dest='show', help='Show image file', action='store_true')
    args = parser.parse_args()

    t = Timer()

    if args.verbose:
        print(args)
        t.start()

    # main(pattern=args.pattern, keep=args.keep, temp_fname=args.temp_fname,
    #      version=args.version, template_file=args.template_file, verbose=args.verbose, show=args.show)

    if args.verbose:
        print('Total Elapsed Time:')
        t.stop()
