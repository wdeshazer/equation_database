"""
math_object Provides helper functions for pulling the LaTeX template from the equations database

update method: https://stackoverflow.com/questions/34774409/build-a-dynamic-update-query-in-psycopg2
https://www.psycopg.org/docs/sql.html#
Type Hinting Tuple: https://stackoverflow.com/questions/47533787/typehinting-tuples-in-python

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
from typing import Tuple


class MathObject:
    """"""
    def __init__(self, table: str, parent_table: str):
        """Constructor for MathObject"""
        self.table = table
        self.parent_table = parent_table  # For equations it is eqn_group. For variables it is equations
        self.records: list = self.allRecords()
        self.last_inserted = None

    def allRecords(self, verbose: bool = False):
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

    def insert(self, parent_id: int = None, name: str = None,
               data=None, latex: str = None, notes: str = None,
               image: bytes = None, template_id: int = None,
               insertion_order: int = None, created_by: str = None,
               verbose: bool = None):

        if data is None:
            data = {}

        db_params = config()

        next_id: int = self.recordCountTotal(verbose=verbose) + 1

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

        data.update({
            'name': name,
            'latex': latex,
            'image': image,
            'notes': notes,
            'template_id': template_id,
            'created_by': created_by
        })

        sql = 'INSERT INTO {table} ({fields}) VALUES ({values}) RETURNING *'

        keys = data.keys()

        query = SQL(sql).format(table=Identifier(self.table),
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

        new_records = cur.fetchall()

        conn.commit()

        cur.close()
        conn.close()

        if parent_id is not None:
            for record in new_records:
                self.associateParent(parent_id=parent_id, child_id=record.id)

        self.last_inserted = new_records[0]
        self.records.append(new_records)

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

    def recordCountTotal(self, verbose: bool = False) -> int:
        sql = "SELECT COUNT(id) from {table}"

        query = SQL(sql).format(table=Identifier(self.table))

        db_params = config()
        conn = connect(**db_params)

        cur = conn.cursor(cursor_factory=NamedTupleCursor)

        if verbose:
            print('Getting Count of Records in table: {table}'.format(table=self.table))

        cur.execute(query)  # self.table))

        record_count = cur.fetchone()

        cur.close()
        conn.close()

        return record_count[0]

    def recordCountForParent(self, parent_table: str = None, parent_record: Tuple[int, ...] = None,
                             verbose: bool = False):
        record_cnt: int = 0

        records = self.recordsForParent(parentTable=parent_table, parent_record=parent_record, verbose=verbose)

        if bool(records):
            record_cnt: int = len(records)

        return record_cnt

    def associateParent(self, parent_id: int = None, child_id: int = None,
                        insertion_order: int = None, inserted_by: str = None,
                        verbose: bool = False):
        parent_key = self.parent_table + '_id'
        self_key = self.table + '_id'

        join_table = self.table + '_' + self.parent_table

        db_params = config()

        data = {}

        if inserted_by is None:
            inserted_by = db_params['user']

        data.update({
            parent_key: parent_id,
            self_key: child_id,
            'insertion_order': insertion_order,
            'inserted_by': inserted_by
        })

        sql = 'INSERT INTO {table} ({fields}) VALUES ({values})'

        keys = data.keys()

        query = SQL(sql).format(table=Identifier(join_table),
                                fields=SQL(', ').join(map(Identifier, keys)),
                                values=SQL(', ').join(map(Placeholder, keys)))

        conn = connect(**db_params)

        if verbose:
            print(query.as_string(conn))

        cur = conn.cursor(cursor_factory=NamedTupleCursor)

        if verbose:
            print('Adding new record to Table: {aTable}'.format(aTable=join_table))

        try:
            cur.execute(query, data)
        except OperationalError as error:
            print(error)

        conn.commit()

        cur.close()
        conn.close()

    def recordsForParent(self, parentTable: str = None, parent_record: Tuple[int, ...] = None, verbose: bool = False):
        parent_key = parentTable + '_id'

        join_table = self.table + '_' + parentTable

        db_params = config()

        sql = 'SELECT * FROM {table} WHERE {pkey}= %s ORDER BY insertion_order ASC;'

        query = SQL(sql).format(
            table=Identifier(join_table),
            pkey=Identifier(parent_key))

        conn = connect(**db_params)

        if verbose:
            print(query.as_string(conn))

        cur = conn.cursor(cursor_factory=NamedTupleCursor)

        try:
            cur.execute(query, parent_record)
        except OperationalError as error:
            print(error)

        records = cur.fetchall()

        cur.close()
        conn.close()

        return records
