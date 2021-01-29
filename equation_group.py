"""
Equation Group Provides helper functions for pulling the LaTeX template from the equations database

https://www.psycopg.org/docs/sql.html#
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

from config import config
from psycopg2.sql import SQL, Identifier, Placeholder
from psycopg2 import connect, OperationalError
from psycopg2.extras import NamedTupleCursor


class NoRecordIDWarning(UserWarning):
    pass


class EquationGroup:
    """"""
    def __init__(self):
        """Constructor for MathObject"""
        self.table = 'eqn_group'
        self.eqn_table = 'equation_eqn_group'
        self.records: list = self.getEquationGroupData()
        self.last_inserted = None

    def getEquationGroupData(self, verbose=False):
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

        cur.close()
        conn.close()

        return records

    def insert(self, name: str = None, notes: str = None, create_by: str = None, verbose: bool = False):
        db_params = config()

        next_id: int = self.recordCountTotal(verbose=verbose) + 1

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

        self.last_inserted = new_record[0]
        self.records.append(new_record)

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
