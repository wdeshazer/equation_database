"""
latex_template Provides helper functions for pulling the LaTeX template from the equations database

Example:
        python latex_template.py --verbose --keep --pattern '\\si{\\km}^3' --show
    python latex_template.py --verbose --keep

Database Errors and Warnings: https://www.tutorialspoint.com/database-handling-errors-in-python
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

import os
import subprocess
import argparse
import pprint
from io import BytesIO
from datetime import datetime
from dataclasses import dataclass, field
from typing import NewType, List
from pickle import dumps
from psycopg2 import connect, DatabaseError
from psycopg2.extras import NamedTupleCursor
from PIL import Image
from config import config

TemplateID = NewType("TemplateID", int)
TemplateIDs = NewType("Templates", List[TemplateID])


def available_templates(verbose: bool = False) -> TemplateIDs:
    """Function to pull available templates from ddtatbase"""
    db_params = config()
    conn = connect(**db_params)

    if verbose is True:
        print('Extracting available Templates')

    cur = conn.cursor()
    try:
        cur.execute('SELECT id FROM template ORDER BY created_at')
    except DatabaseError as error:
        print("Couldn't retrieve templates", error)

    output = cur.fetchall()
    cur.close()

    template_ids = TemplateIDs([x[0] for x in output])

    return template_ids


def template(version: int = None, verbose: bool = False) -> NamedTupleCursor:
    """Function to pull the data for a specified template"""
    db_params = config()
    conn = connect(**db_params)

    cur = conn.cursor(cursor_factory=NamedTupleCursor)

    if version is None:
        if verbose:
            print('Extracting Latest Template from Database')

        cur.execute('SELECT * FROM template ORDER BY created_at DESC LIMIT 1')
    else:
        try:
            if verbose:
                print('Extracting Template with id: {} from Database'.format(version))

            cur.execute('SELECT * FROM template WHERE ID=%s', (version,))
        except DatabaseError as error:
            print("Couldn't retrieve that template.", error)
            print("Returning latest template.")
            cur.execute('SELECT * FROM template ORDER BY created_at DESC LIMIT 1')

    if verbose:
        print('Fetching data from Database')

    the_template = cur.fetchone()
    cur.close()

    return the_template


def compile_pattern(pattern: str = 'm^3', keep: bool = True, temp_fname: str = "eq_db", version: int = None,
                    a_template: str = None, verbose: bool = False, show: bool = False) -> bytes:
    """General Latex Compile Function"""

    if verbose:
        print('\tArguments:')
        pprint.PrettyPrinter(indent=12).pprint(locals())

    if a_template is None:
        a_template_record = template(version=version, verbose=verbose)
        a_template = a_template_record.data

    os.chdir('LaTeX')

    text_file = open(temp_fname+'.tex', "w")
    text_file.write(a_template.replace('%__REPLACEMENT__TEXT', pattern))
    text_file.close()

    # try:
    if verbose:
        print("Operating System: ", os.name)
        print('Executing XeLaTeX:')

    shell = os.name == 'nt'

    try:
        p_1 = subprocess.run(['xelatex.exe', temp_fname + '.tex', '-interaction=batchmode'],
                             shell=shell, capture_output=True, text=True, check=True)

        if verbose:
            pprint.PrettyPrinter(indent=8).pprint(p_1)
    except subprocess.CalledProcessError as error:
        print(error.output)

    try:
        if verbose:
            print('Converting to png:')

        p_2 = subprocess.run(['convert.exe', '-density', '300', '-depth', '8', '-quality', '85', temp_fname + '.pdf',
                             'png32:'+temp_fname+'.png'], shell=shell, capture_output=True, text=True, check=True)

        if verbose:
            pprint.PrettyPrinter(indent=8).pprint(p_2)

    except subprocess.CalledProcessError as error:
        print('Failed to make png:')
        print(error.output)

    if verbose:
        print('Pulling png data into python')

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

    if keep is False:
        clean_files(temp_fname)

    return png_data


def clean_files(temp_fname="eq_db"):
    """Removes associated LaTeX Files. Unactive by default"""
    os.remove(temp_fname+'.aux')
    os.remove(temp_fname+'.log')
    os.remove(temp_fname+'.pdf')
    os.remove(temp_fname+'.tex')
    os.remove(temp_fname+'.png')


def main(pattern: str = 'm^3', keep: bool = False, temp_fname: str = "eq_db", version: int = None,
         a_template: str = None, template_file: str = None, verbose: bool = False, show: bool = False):
    """Main function for executing a compile"""

    if verbose:
        print('\tArguments:')
        pprint.PrettyPrinter(indent=12).pprint(locals())

    # Both aTemplate and template_file are provided here, because programmatically specifying the string seems
    # reasonable in addition to specifying a filename. However, it doesn't seem like a reasonable thing to do on the
    # command line. It does make sense as a redirected pipe, but I don't have interest in making that happen,
    # because it's not even my preferred way of interracting
    if template_file is not None:
        if verbose:
            print('Reading LaTeX Template File: {}'.format(template_file))
        with open(template_file, 'r') as my_file:
            a_template = my_file.readlines()

    compile_pattern(pattern=pattern, keep=keep, version=version, temp_fname=temp_fname, a_template=a_template,
                    verbose=verbose, show=show)


# noinspection PyMethodParameters
@dataclass
class LatexData:
    """Class for managing LaTeX data, including image"""
    latex: str = "a^2 + b^2 = c^2"
    template_ids: TemplateIDs = field(default_factory=available_templates)
    template_id: TemplateID = None
    image: bytes = None
    compiled_at: datetime = None
    image_is_dirty: bool = False

    def __post_init__(self):
        """Template ID is set during Initialization and an update/potential
            recompile if either there is no image or the image is inconsistent with the LaTeX.
             An inconsistency can only happen when the LaTeX field is update manually with an SQL query"""
        if self.template_id is None or self.template_id == 'latest':
            self.template_id = self.template_ids[-1]
        self.update(image=self.image, image_is_dirty=self.image_is_dirty)

    def update(self, latex: str = None, template_id: TemplateID = None, image: bytes = None,
               image_is_dirty: bool = False, verbose: bool = False):
        """Main method. Maintains integrity of latex text and image by recompiling if core data gets updated"""
        if latex is not None:
            self.latex = latex
        if template_id is not None:
            self.template_id = template_id
        if image is not None and image_is_dirty is False:
            self.image = image
        else:
            self.image = \
                compile_pattern(pattern=self.latex, version=self.template_id, verbose=verbose)
            self.compiled_at = datetime.now()
            self.image_is_dirty = False

    def show(self):
        """Display associated image"""
        stream = BytesIO(self.image)
        image = Image.open(stream).convert("RGBA")
        stream.close()
        image.show()

    def as_binary(self) -> bytes:
        """Convience function to store data"""
        return dumps(self)


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

    if args.verbose:
        print(args)

    main(pattern=args.pattern, keep=args.keep, temp_fname=args.temp_fname,
         version=args.version, template_file=args.template_file, verbose=args.verbose, show=args.show)

    if args.verbose:
        print('Total Elapsed Time:')
