"""
Equation Group Provides helper functions for pulling the LaTeX template from the equations database

https://www.psycopg.org/docs/sql.html#
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

from collections import defaultdict
from warnings import warn
from psycopg2.sql import SQL, Identifier, Placeholder, Composed
from psycopg2 import connect, OperationalError
from psycopg2.extras import NamedTupleCursor
from config import config


class NoRecordIDError(UserWarning):
    """UserWarning for EquationGroup"""


class EquationGroup:
    """Class for managing and interfacing with Postgres Table eqn_group"""
    def __init__(self):
        """Constructor for eqn_group"""
        self.table = 'eqn_group'
        self.records: dict = self.get_equation_group_data()
        self.last_inserted = None

    def get_equation_group_data(self, as_columns: bool = True, verbose: bool = False):
        """Method to pull data from database"""
        sql = "SELECT * FROM {tbl}"
        query = SQL(sql).format(tbl=Identifier(self.table))

        db_params = config()
        conn = connect(**db_params)

        cur = conn.cursor(cursor_factory=NamedTupleCursor)

        if verbose:
            print('Extracting records from Table: ' + self.table)

        try:
            cur.execute(query)
        except OperationalError as error:
            print(error)

        records = cur.fetchall()

        if as_columns is True:
            records = self.as_columns(records)

        cur.close()
        conn.close()

        return records

    def insert(self, name: str = None, notes: str = None, create_by: str = None,
               verbose: bool = False):
        """Method to Insert New Equation Records"""
        db_params = config()

        next_id: int = self.record_count_total(verbose=verbose) + 1

        if name is None:
            name = "{aTable} {ID:d}".format(ID=next_id, aTable=self.table)
        if create_by is None:
            create_by = db_params['user']

        # data = {'name': 'New Group', 'notes': 'I hope this works', 'created_by': 'razor'}

        data = {
            'name': name,
            'notes': notes,
            'created_by': create_by
        }

        sql = 'INSERT INTO eqn_group ({}) VALUES ({}) RETURNING *'

        keys = data.keys()

        query = SQL(sql).format(
            SQL(', ').join(map(Identifier, keys)),
            SQL(', ').join(map(Placeholder, keys))
        )

        conn = connect(**db_params)

        cur = conn.cursor(cursor_factory=NamedTupleCursor)

        if verbose:
            print(query.as_string(conn))

        try:
            cur.execute(query, data)
        except OperationalError as error:
            print(error)

        conn.commit()

        new_record = cur.fetchall()

        cur.close()
        conn.close()

        self.last_inserted = self.as_columns(new_record)
        self.append(new_record)

    def update(self, an_id: id = None, where_key: str = 'id', name: str = None,
               data=None, notes: str = None, modified_by: str = None, created_by: str = None,
               verbose: bool = None):
        """Insert New Record Into math_object"""

        if an_id is None:
            warn("No Record ID Specified", NoRecordIDError)
        else:
            if data is None:
                data = {}

            db_params = config()

            if name is not None:
                data.update(name=name)

            if notes is not None:
                data.update(notes=notes)

            if created_by is not None:
                data.update(created_by=created_by)

            # If there is no data, then skip. Of course one could still change modified by:
            if len(data) > 0 or modified_by is not None:

                # Always require a modified by and because one can change data without specifying a modifer,
                # this is necessary. We don't check it before the previous if, because we don't want to create
                # a modified_by if not data was set and no modified_by was set.
                if modified_by is None:
                    modified_by = db_params['user']

                data.update(modified_by=modified_by)

                fields = data.keys()

                sql = "UPDATE {table} SET {fields} WHERE {pkey} = {a_value} RETURNING *"

                query = SQL(sql).format(table=Identifier(self.table),
                                        fields=SQL(', ').join(
                                            Composed([Identifier(k), SQL(' = '), Placeholder(k)]) for k in fields
                                        ),
                                        pkey=Identifier(where_key),
                                        a_value=Placeholder('where_key')
                                        )

                data.update(where_key=an_id)

                conn = connect(**db_params)
                cur = conn.cursor(cursor_factory=NamedTupleCursor)

                if verbose:
                    print(query.as_string(conn))
                    print(cur.mogrify(query, data))

                try:
                    cur.execute(query, data)
                except OperationalError as error:
                    print(error)

                new_record = cur.fetchall()

                conn.commit()

                cur.close()
                conn.close()

                self.last_inserted = self.as_columns(new_record)

                self.records = self.get_equation_group_data()

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

    def record_count_total(self, verbose: bool = False) -> int:
        """Method to get total number of eqn_groups"""
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

    @staticmethod
    def as_columns(records):
        """Helper function to turn NameTuple records into column-like dictionaries"""
        res = defaultdict(list)

        for data in records:
            record: dict = data._asdict()
            for key, value in record.items():
                res[key].append(value)
        return res
