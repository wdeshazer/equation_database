"""
latex_template Provides helper functions for pulling the LaTeX show_template_manager from the equations database

Example:
    python latex_template.py --verbose --keep --pattern '\\si{\\km}^3' --show
    python latex_template.py --verbose --keep
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


def template(version: int = None, verbose: bool = False) -> NamedTupleCursor:
    db_params = config()
    conn = psycopg2.connect(**db_params)

    cur = conn.cursor(cursor_factory=NamedTupleCursor)
    t: Timer = Timer()

    if version is None:
        if verbose:
            print('Extracting Latest Template from Database')
            t.start()

        cur.execute('SELECT * FROM show_template_manager ORDER BY created_at DESC LIMIT 1')

        if verbose:
            t.stop()

    else:
        try:
            if verbose:
                print('Extracting Template with id: {} from Database'.format(version))
                t.start()

            cur.execute('SELECT * FROM show_template_manager WHERE ID=%s', version)

            if verbose:
                t.stop()

        except Exception as error:
            print("Couldn't retrieve that show_template_manager.", error)
            print("Returning latest show_template_manager.")
            cur.execute('SELECT * FROM show_template_manager ORDER BY created_at DESC LIMIT 1')

    if verbose:
        print('Fetching data from Database')
        t.start()

    theTemplate = cur.fetchone()

    if verbose:
        t.stop()

    return theTemplate


def compile_pattern(pattern: str = 'm^3', keep: bool = True, temp_fname: str = "eq_db", version: int = None,
                    aTemplate: str = None, verbose: bool = False, show: bool = False) -> bytes:

    if verbose:
        print('{called} Called By: {caller}'.format(called=called_func(), caller=calling_func()))
        print('\tArguments:')
        pprint.PrettyPrinter(indent=12).pprint(locals())

    if aTemplate is None:
        aTemplate_record = template(version=version, verbose=verbose)
        aTemplate = aTemplate_record.data

    t = Timer()

    if verbose:
        print('Replacing pattern in Template')
        t.start()

    os.chdir('LaTeX')

    text_file = open(temp_fname+'.tex', "w")
    text_file.write(aTemplate.replace('%__REPLACEMENT__TEXT', pattern))
    text_file.close()

    if verbose:
        t.stop()

    # try:
    if verbose:
        print("Operating System: ", os.name)

    if os.name == 'nt':
        shell = True
    else:
        shell = False

    try:
        if verbose:
            print('Executing XeLaTeX:')
            t.start()

        p1 = subprocess.run(['xelatex.exe', temp_fname + '.tex', '-interaction=batchmode'],
                            shell=shell, capture_output=True, text=True, check=True)

        if verbose:
            t.stop()
            pprint.PrettyPrinter(indent=8).pprint(p1)

    except subprocess.CalledProcessError as error:
        print(error.output)

    try:
        if verbose:
            print('Converting to png:')
            t.start()

        p2 = subprocess.run(['convert.exe', '-density', '300', '-depth', '8', '-quality', '85', temp_fname + '.pdf',
                             'png32:'+temp_fname+'.png'], shell=shell, capture_output=True, text=True, check=True)

        if verbose:
            t.stop()
            pprint.PrettyPrinter(indent=8).pprint(p2)

    except subprocess.CalledProcessError as error:
        print('Failed to make png:')
        print(error.output)

    if verbose:
        print('Pulling png data into python')
        t.start()

    with open(temp_fname + '.png', 'rb') as file:
        png_data: bytes = file.read()

    if show:
        if verbose:
            print('Displaying Graphic')
        stream = BytesIO(png_data)
        image = Image.open(stream).convert("RGBA")
        stream.close()
        image.show()

    os.chdir('..')

    if verbose:
        t.stop()

    if keep is False:
        clean_files(temp_fname)

    return png_data


def clean_files(temp_fname="eq_db"):
    os.remove(temp_fname+'.aux')
    os.remove(temp_fname+'.log')
    os.remove(temp_fname+'.pdf')
    os.remove(temp_fname+'.tex')
    os.remove(temp_fname+'.png')


def main(pattern: str = 'm^3', keep: bool = False, temp_fname: str = "eq_db", version: int = None,
         aTemplate: str = None, template_file: str = None, verbose: bool = False, show: bool = False):

    if verbose:
        print('{called} Called By: {caller}'.format(called=called_func(), caller=calling_func()))
        print('\tArguments:')
        pprint.PrettyPrinter(indent=12).pprint(locals())

    # Both aTemplate and template_file are provided here, because programmatically specifying the string seems
    # reasonable in addition to specifying a filename. However, it doesn't seem like a reasonable thing to do on the
    # command line. It does make sense as a redirected pipe, but I don't have interest in making that happen,
    # because it's not even my preferred way of interracting
    if template_file is not None:
        if verbose:
            print('Reading LaTeX Template File: {}'.format(template_file))
        with open(template_file, 'r') as myFile:
            aTemplate = myFile.readlines()

    compile_pattern(pattern=pattern, keep=keep, version=version, temp_fname=temp_fname, aTemplate=aTemplate,
                    verbose=verbose, show=show)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='LaTeX Template Resources')
    parser.add_argument("--pattern", dest='pattern', help='str: Valid LaTeX Pattern', default="m^3")
    parser.add_argument("--keep", dest='keep', help='bool: Remove Support Files',
                        default=False, action='store_true')
    parser.add_argument("--temp_fname", dest='temp_fname', help='str: Filename Token for Temp Files', default="eq_db")
    parser.add_argument("--version", dest='version',
                        help='int: Template Version. None value or non-existent returns latest',
                        default=None)
    parser.add_argument("--template_file", dest='template_file', help='User specified LaTeX show_template_manager file',
                        default=None)
    parser.add_argument("--verbose", dest='verbose', help='Output run messages', action='store_true')
    parser.add_argument("--show", dest='show', help='Show image file', action='store_true')
    args = parser.parse_args()

    t = Timer()

    if args.verbose:
        print(args)
        t.start()

    main(pattern=args.pattern, keep=args.keep, temp_fname=args.temp_fname,
         version=args.version, template_file=args.template_file, verbose=args.verbose, show=args.show)

    if args.verbose:
        print('Total Elapsed Time:')
        t.stop()
