"""
math_object Provides helper functions for pulling the LaTeX template from the equations database

update method: https://stackoverflow.com/questions/34774409/build-a-dynamic-update-query-in-psycopg2

this is bad code and is ideal for sql injection. Values must be passed in through an execute statement
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

from config import config
import psycopg2
from psycopg2.extras import NamedTupleCursor
from latex_template import compile_pattern, template
from textwrap import dedent
from warnings import warn


class MathObject:
    """"""
    def __init__(self, table: str, join_table: str):
        """Constructor for MathObject"""
        self.table = table
        self.join_table = join_table

    def records(self, verbose: bool = False):
        sql = 'SELECT * FROM {aTable}'.format(aTable=self.table)
        db_params = config()
        conn = psycopg2.connect(**db_params)

        cur = conn.cursor(cursor_factory=NamedTupleCursor)

        if verbose:
            print('Extracting records from Table: {aTable}'.format(aTable=self.table))

        try:
            cur.execute(sql)
        except psycopg2.OperationalError as error:
            print(error)

        records = cur.fetchall()

        cur.close()
        conn.close()

        return records

    def insert(self, parent: str = None, name: str = None, latex: str = None, notes: str = None,
               image: bytes = None, template_id: int = None, table_order: int = None, table_order_prev: int = None,
               created_by: str = None, verbose: bool = None):
        db_params = config()

        next_id: int = self._getNextID(verbose=verbose)

        if name is None:
            name = "{aTable} {ID:d}".format(ID=next_id, aTable=self.table)

        if latex is None:
            latex = 'a^2 + b^2 = c^2'

        theTemplate = template(version=template_id, verbose=verbose)
        aTemplate = theTemplate.data
        template_id = aTemplate.id

        if image is None:
            # If aTemplate is None the most recent template is used
            image = psycopg2.Binary(compile_pattern(pattern=latex, aTemplate=aTemplate, verbose=verbose))

        if table_order is None:
            table_order = self.record_count() + 1

        if table_order_prev is None:
            table_order_prev = table_order

        if created_by is None:
            created_by = db_params['user']

        data = {
            'id': next_id,
            'name': name,
            'latex': latex,
            'image': image,
            'notes': notes,
            'template_id': template_id,
            'tableOrder': table_order,
            'tableOrderPrev': table_order_prev,
            'created_by': created_by
        }

        sql = dedent(""" \
        INSERT INTO {table} (id, name, latex, image, table_order, table_order_prev, created_by)
            VALUES (%(id)s, %(name)s, %(latex)s, %(image)s, %(tableOrder)s, %(tableOrderPrev)s, %(created_by)s);
        """).format(table=self.table)
        conn = psycopg2.connect(**db_params)

        cur = conn.cursor(cursor_factory=NamedTupleCursor)

        if verbose:
            print('Adding new record to Table: {aTable}'.format(aTable=self.table))

        try:
            cur.execute(sql, data)
        except psycopg2.OperationalError as error:
            print(error)

        conn.commit()

        cur.close()
        conn.close()

    # def update(self, name: str = None, latex: str = None, notes: str = None, image: bytes = None,
    #            template_id: int = None, table_order: int = None, table_order_prev: int = None,
    #            created_by: str = None, verbose: bool = None):
    #     updates = {}
    #
    #     if name is not None:
    #         updates['name'] = name
    #     if latex is not None:
    #         updates['latex'] = latex
    #         if image is None:
    #             theTemplate = template(version=template_id, verbose=verbose)
    #             aTemplate = theTemplate.data
    #             template_id = theTemplate.id
    #             updates['template_id'] = template_id
    #
    #             image = psycopg2.Binary(compile_pattern(pattern=latex, aTemplate=aTemplate, verbose=verbose))
    #             updates['image'] = image
    #     if table_order is not None:
    #         table_order_prev = table_order
    #
    #
    #
    #     sql_template = "UPDATE foo SET ({}) = %s WHERE id = {}"
    #     sql = sql_template.format(', '.join(updates.keys()), 10)
    #     params = (tuple(addr_dict.values()),)
    #     print
    #     cur.mogrify(sql, params)
    #     cur.execute(sql, params)

    # Simple return statement. More sophisticated ones will have to be purpose built
    def values_for_fields(self, whereKey: str = 'id', whereValues: tuple = None,
                          name: bool = True, table: str = None, verbose: bool = False, **kwargs):
        """where_key could be 'id', 'name', etc.
            For any other field, you just set the fieldname to True"""

        if whereValues is None:
            where_statement = ''
        else:
            where_statement = "WHERE {field} IN {values}".format(field=whereKey, values=whereValues)

        keys = ['id']

        if name is True:
            keys.append('name')
        for kw in kwargs:
            if kwargs[kw] is True:
                keys.append(kw)

        if table is None:
            table = self.table

        select_stmt = "SELECT " + ", ".join(keys) + " FROM " + table + where_statement

        db_params = config()
        conn = psycopg2.connect(**db_params)

        cur = conn.cursor(cursor_factory=NamedTupleCursor)

        if verbose:
            print('Extracting records from Table: {aTable}'.format(aTable=self.table))

        try:
            cur.execute(select_stmt)
        except psycopg2.OperationalError as error:
            print(error)

        records = cur.fetchall()

        cur.close()
        conn.close()

        return records

    def record_count(self) -> int:
        record_cnt: int = 0

        records = self.records()

        if bool(records):
            record_cnt: int = len(records)

        return record_cnt

    @staticmethod
    def _getNextID(verbose: bool = False) -> int:
        # sql = "Select nextval(pg_get_serial_sequence('{table}', 'id')) as new_id;"
        # Normally, one would use the previous command to get the sequences name based on the table.
        # However, all mathobjects pull tables that inherit from latex_object. I'm not sure how to
        # find info that is associated with the parent, so I am hard wiring this. If something breaks
        # in the future, we might want to look here.
        sql = "Select nextval('schema_templates.latex_object_id_seq'::regclass) as new_id;"

        db_params = config()
        conn = psycopg2.connect(**db_params)

        cur = conn.cursor(cursor_factory=NamedTupleCursor)

        if verbose:
            print('Extracting Latest Template from Database')

        cur.execute(sql)  # self.table))
        newID_record = cur.fetchone()
        newID: int = newID_record.new_id

        cur.close()
        conn.close()

        return newID

    def vivify_record(self, verbose: bool = False, data: dict = None):
        lpattern = 'a^2 + b^2 = c^2'
        next_id: int = self._getNextID(verbose=verbose)
        table_order = self.record_count() + 1

        if data is None:
            data = {}

        if 'id' not in data:
            data['id'] = next_id
        if 'name' not in data:
            data['name'] = "{aTable} {ID:d}".format(ID=next_id, aTable=self.table)
        if 'latex' not in data:
            data['latex'] = lpattern
        if 'image' not in data:
            data['image'] = psycopg2.Binary(compile_pattern(pattern=lpattern, verbose=verbose))
        if 'unit_id' not in data:
            data['unit_id'] = 1
        if 'table_order' not in data:
            data['table_order'] = table_order
        if 'table_order_prev' not in data:
            data['table_order_prev'] = table_order

        db_params = config()
        if 'created_by' not in data:
            data['created_by'] = db_params['user']

        sql = "INSERT INTO {table} ".format(table=self.table)
        sql += "(" + ",".join(data.keys()) + ")\n"
        sql += "    VALUES (%(" + ")s, %(".join(data.keys()) + ")s);"

        # db_params = config()
        conn = psycopg2.connect(**db_params)

        cur = conn.cursor(cursor_factory=NamedTupleCursor)

        if verbose:
            print('Adding new record to Table: {aTable}'.format(aTable=self.table))

        try:
            cur.execute(sql, data)
        except psycopg2.OperationalError as error:
            print(error)

        conn.commit()

        cur.close()
        conn.close()

        records = self.records()
        return records
