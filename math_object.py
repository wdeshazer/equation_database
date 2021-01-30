"""
math_object Provides helper functions for pulling the LaTeX template from the equations database

update method: https://stackoverflow.com/questions/34774409/build-a-dynamic-update-query-in-psycopg2
https://www.psycopg.org/docs/sql.html#
Type Hinting Tuple: https://stackoverflow.com/questions/47533787/typehinting-tuples-in-python

"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

from typing import Tuple
from collections import defaultdict
from warnings import warn
from psycopg2.sql import SQL, Identifier, Placeholder
from psycopg2 import connect, OperationalError, Binary
from psycopg2.extras import NamedTupleCursor
from latex_template import compile_pattern, template
from config import config


class RecordIDTypeError(UserWarning):
    """UserWarning for EquationGroup"""


class MathObject:
    """Base class for Equations, Variables, and Units"""
    def __init__(self, table: str, parent_table: str):
        """Constructor for MathObject"""
        self.table = table
        self.parent_table = parent_table  # For equations it is eqn_group. For variables it is equations
        self.records: dict = self.all_records()
        self.last_inserted = None

    def all_records(self, as_columns: bool = True, verbose: bool = False):
        """Returns all records for math_object"""
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

        if as_columns is True:
            records = self.as_columns(records)

        return records

    def insert(self, parent_id: int = None, name: str = None,
               data=None, latex: str = None, notes: str = None,
               image: bytes = None, template_id: int = None,
               insertion_order: int = None, created_by: str = None,
               verbose: bool = None):
        """Insert New Record Into math_object"""

        if data is None:
            data = {}

        db_params = config()

        next_id: int = self.record_count_total(verbose=verbose) + 1

        if name is None:
            name = "{aTable} {ID:d}".format(ID=next_id, aTable=self.table)
        if created_by is None:
            created_by = db_params['user']

        if latex is None:
            latex = 'a^2 + b^2 = c^2'

        the_template = template(version=template_id, verbose=verbose)
        a_template = the_template.data
        template_id = the_template.id

        if image is None:
            # If a_template is None the most recent template is used
            image = Binary(compile_pattern(pattern=latex, aTemplate=a_template, verbose=verbose))

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
                self.associate_parent(parent_id=parent_id, child_id=record.id, insertion_order=insertion_order)

        self.last_inserted = new_records[0]

        self.append(new_records)

    def append(self, new_records):
        """Append new records to existing records. Because the data is stored as a dictionary instead of
        NamedTuples, it requires a helper function to append new data"""
        res = self.records

        for data in new_records:
            # noinspection PyProtectedMember
            record: dict = data._asdict()
            for key, value in record.items():
                res[key].append(value)

        self.records = res

    # Simple return statement. More sophisticated ones will have to be purpose built
    def values_for_fields(self, where_key: str = 'id', where_values: Tuple[int, ...] = None,
                          name: bool = True, as_column: bool = True, verbose: bool = False, **kwargs):
        """where_key could be 'id', 'name', etc.
            For any other field, you just set the fieldname to True"""

        fields = ['id']

        if name is True:
            fields.append('name')
        for a_key in kwargs:
            if kwargs[a_key] is True:
                fields.append(a_key)

        db_params = config()
        conn = connect(**db_params)

        if where_values is None:
            sql = "SELECT {fields} FROM {table}"
            query = SQL(sql).format(table=Identifier(self.table),
                                    fields=SQL(', ').join(map(Identifier, fields)))
            if verbose:
                print(query.as_string(conn))
        else:
            sql = "SELECT {fields} from {table} where {pkey} IN %s"
            query = SQL(sql).format(table=Identifier(self.table),
                                    fields=SQL(', ').join(map(Identifier, fields)),
                                    pkey=Identifier(where_key)
                                    )
            if verbose:
                print(query.as_string(conn))

        cur = conn.cursor(cursor_factory=NamedTupleCursor)

        if verbose:
            print('Extracting records from Table: {aTable}'.format(aTable=self.table))

        try:
            cur.execute(query, where_values)
        except OperationalError as error:
            print(error)

        records = cur.fetchall()

        cur.close()
        conn.close()

        if as_column is True:
            records = self.as_columns(records)

        return records

    def record_count_total(self, verbose: bool = False) -> int:
        """Get the total record count for {table}""".format(table=self.table)
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

    def record_count_for_parent(self, parent_id: Tuple[int, ...] = None,
                                verbose: bool = False):
        """Return record count for Parent Table"""
        sql = "SELECT COUNT(*) from {table} WHERE {parent_key} IN %s"

        query = SQL(sql).format(table=Identifier(self.join_table()),
                                parent_key=Identifier(self.parent_key())
                                )

        db_params = config()
        conn = connect(**db_params)

        cur = conn.cursor(cursor_factory=NamedTupleCursor)

        if verbose:
            print('Getting Count of Records in table: {table} for Group ID: {gid}'.format(table=self.join_table(),
                                                                                          gid=parent_id))

        try:
            cur.execute(query, parent_id)  # self.table))
        except TypeError:
            cur.execute(query, (parent_id,))

        record_count = cur.fetchone()

        cur.close()
        conn.close()

        return record_count[0]

    def associate_parent(self, parent_id: int = None, child_id: int = None,
                         insertion_order: int = None, inserted_by: str = None,
                         verbose: bool = False):
        """Associate the parent and child tables using parent id. Insertion_order and inserted_by are optional"""
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

    def records_for_parent(self, parent_id: Tuple[int, ...] = None, as_columns: bool = True,
                           verbose: bool = False):
        """Get the {table} records for {parent}""".format(table=self.table, parent=self.parent_table)
        db_params = config()
        sql = ''

        if isinstance(parent_id, int):
            sql = 'SELECT * FROM {table} WHERE {pkey}= %s ORDER BY insertion_order ASC;'
        elif isinstance(parent_id, tuple):
            sql = 'SELECT * FROM {table} WHERE {pkey} IN %s ORDER BY insertion_order ASC;'
        else:
            warn("parent_id type not recognized", RecordIDTypeError)

        query = SQL(sql).format(
            table=Identifier(self.join_table()),
            pkey=Identifier(self.parent_key()))

        conn = connect(**db_params)

        cur = conn.cursor(cursor_factory=NamedTupleCursor)

        if verbose:
            print(query.as_string(conn))
            if isinstance(parent_id, int):
                cur.mogrify(query, parent_id)
            elif isinstance(parent_id, tuple):
                cur.mogrify(query, (parent_id, ))

        try:
            cur.execute(query, (parent_id, ))
        except TypeError:
            cur.execute(query, parent_id)
        except OperationalError as error:
            print(error)

        records = cur.fetchall()

        cur.close()
        conn.close()

        if as_columns is True:
            records = self.as_columns(records)

        return records

    def id_for_records_not_in_parent(self, parent_id: Tuple[int, ...], verbose: bool = False):
        """Returns dictionary with ids and indexes of items not in the parent group.
        The indexes can be used with self.records"""
        ids_for_all_records = self.records['id']

        records_in_parent_table = self.records_for_parent(parent_id=parent_id, verbose=verbose)

        record_ids_in_parent_table = records_in_parent_table[self.self_key()]

        record_ids_not_in_parent = list(set(ids_for_all_records) - set(record_ids_in_parent_table))

        result = {
            'ids': record_ids_not_in_parent,
            'indexes': [ids_for_all_records.index(x) for x in record_ids_not_in_parent]
        }

        return result

    def parent_key(self):
        """Parent ID String to be used as a Key in the table"""
        return self.parent_table + '_id'

    def self_key(self):
        """Self ID String to be used as a Key in the table"""
        return self.table + '_id'

    def join_table(self):
        """Join table which is a concatenation of the table and the parent table"""
        return self.table + '_' + self.parent_table

    # NamedTuple uses underscores to prevent name collision _make, _replace, _asdict, _fields
    # noinspection PyProtectedMember
    @staticmethod
    def as_columns(records):
        """Helper function to turn NameTuple records into column-like dictionaries"""
        res = defaultdict(list)

        for data in records:
            record = data._asdict()
            for key, value in record.items():
                res[key].append(value)
        return res
