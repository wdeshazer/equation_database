"""
math_object Provides helper functions for pulling the LaTeX template from the equations database

update method: https://stackoverflow.com/questions/34774409/build-a-dynamic-update-query-in-psycopg2
https://www.psycopg.org/docs/sql.html#

"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

from config import config
from psycopg2.sql import SQL, Identifier, Placeholder
from psycopg2 import connect, OperationalError, Binary
from psycopg2.extras import NamedTupleCursor
from latex_template import compile_pattern, template
from warnings import warn


class MathObject:
    """"""
    def __init__(self, table: str):
        """Constructor for MathObject"""
        self.table = table
        # self.parent_table = parent  # For equations it is eqn_group. For variables it is equations
        # self.child_table = child  # For equations -> variables, for vaiables -> nothing. eqn_group -> not math_object

    def records(self, verbose: bool = False):
        # sql = 'SELECT * FROM {aTable}'.format(aTable=self.table)
        sql = "SELECT * FROM {tbl}"
        query = SQL(sql).format(tbl=Identifier(self.table))

        db_params = config()
        conn = connect(**db_params)

        cur = conn.cursor(cursor_factory=NamedTupleCursor)

        if verbose:
            print('Extracting records from Table: {aTable}'.format(aTable=self.table))

        try:
            cur.execute(query)
        except OperationalError as error:
            print(error)

        records = cur.fetchall()

        cur.close()
        conn.close()

        return records

    def insert(self, parent: str = None, name: str = None, data=None, latex: str = None, notes: str = None,
               image: bytes = None, template_id: int = None, table_order: int = None, table_order_prev: int = None,
               created_by: str = None, verbose: bool = None):

        if data is None:
            data = {}

        db_params = config()

        next_id: int = self._getNextID(verbose=verbose)

        if name is None:
            name = "{aTable} {ID:d}".format(ID=next_id, aTable=self.table)
        if created_by is None:
            created_by = db_params['user']

        if latex is None:
            latex = 'a^2 + b^2 = c^2'

        theTemplate = template(version=template_id, verbose=verbose)
        aTemplate = theTemplate.data
        template_id = theTemplate.id

        if image is None:
            # If aTemplate is None the most recent template is used
            image = Binary(compile_pattern(pattern=latex, aTemplate=aTemplate, verbose=verbose))

        if table_order is None:
            table_order = self.record_count() + 1

        if table_order_prev is None:
            table_order_prev = table_order

        data.update({
            'id': next_id,
            'name': name,
            'latex': latex,
            'image': image,
            'notes': notes,
            'template_id': template_id,
            'table_order': table_order,
            'table_order_prev': table_order_prev,
            'created_by': created_by
        })

        sql = 'INSERT INTO {table} ({fields}) VALUES ({values})'

        keys = data.keys()

        query = SQL(sql).format(table=Identifier('equation'),
                                fields=SQL(', ').join(map(Identifier, keys)),
                                values=SQL(', ').join(map(Placeholder, keys)))

        conn = connect(**db_params)

        if verbose:
            print(query.as_string(conn))

        cur = conn.cursor(cursor_factory=NamedTupleCursor)

        if verbose:
            print('Adding new record to Table: {aTable}'.format(aTable=self.table))

        try:
            cur.execute(query, data)
        except OperationalError as error:
            print(error)

        conn.commit()

        cur.close()
        conn.close()

    # Simple return statement. More sophisticated ones will have to be purpose built
    def values_for_fields(self, whereKey: str = 'id', whereValues: tuple = None,
                          name: bool = True, table: str = None, verbose: bool = False, **kwargs):
        """whereKey could be 'id', 'name', etc.
            For any other field, you just set the fieldname to True"""

        fields = ['id']

        if name is True:
            fields.append('name')
        for kw in kwargs:
            if kwargs[kw] is True:
                fields.append(kw)

        db_params = config()
        conn = connect(**db_params)

        if whereValues is None:
            sql = "SELECT {fields} FROM {table}"
            query = SQL(sql).format(table=Identifier(self.table),
                                    fields=SQL(', ').join(map(Identifier, fields)))
            print(query.as_string(conn))
        else:
            sql = "SELECT {fields} from {table} where {pkey} = %s"
            query = SQL(sql).format(table=Identifier(self.table),
                                    fields=SQL(', ').join(map(Identifier, fields)),
                                    pkey=Identifier(whereKey)
                                    )

        cur = conn.cursor(cursor_factory=NamedTupleCursor)

        if verbose:
            print('Extracting records from Table: {aTable}'.format(aTable=self.table))

        try:
            cur.execute(query, whereValues)
        except OperationalError as error:
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

    def associateParent(self, parentTable: str = None, parent_record: int = None, child_record: int = None,
                        insertion_order: int = None, insertion_order_prev: int = None):
        parent_key = parentTable + '_id'
        self_key = self.table + '_id'

        join_table = self.table + '_' + parentTable

    @staticmethod
    def _getNextID(verbose: bool = False) -> int:
        # sql = "Select nextval(pg_get_serial_sequence('{table}', 'id')) as new_id;"
        # Normally, one would use the previous command to get the sequences name based on the table.
        # However, all mathobjects pull tables that inherit from latex_object. I'm not sure how to
        # find info that is associated with the parent, so I am hard wiring this. If something breaks
        # in the future, we might want to look here.
        sql = "Select nextval('schema_templates.latex_object_id_seq'::regclass) as new_id;"

        db_params = config()
        conn = connect(**db_params)

        cur = conn.cursor(cursor_factory=NamedTupleCursor)

        if verbose:
            print('Extracting Latest Template from Database')

        cur.execute(sql)  # self.table))
        newID_record = cur.fetchone()
        newID: int = newID_record.new_id

        cur.close()
        conn.close()

        return newID
