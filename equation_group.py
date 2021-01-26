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

        next_id: int = self._getNextID(verbose=verbose)

        if name is None:
            name = "{aTable} {ID:d}".format(ID=next_id, aTable=self.table)
        if create_by is None:
            create_by = db_params['user']

        # data = {'name': 'New Group', 'notes': 'I hope this works', 'created_by': 'razor'}

        data = {
            'id': next_id,
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

    def record_count(self) -> int:
        record_cnt: int = 0

        records = self.getEquationGroupData()

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
