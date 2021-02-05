"""
Equation Group Provides helper functions for pulling the LaTeX template from the equations database

https://www.psycopg.org/docs/sql.html#
https://naysan.ca/2020/05/09/pandas-to-postgresql-using-psycopg2-bulk-insert-performance-benchmark/
https://github.com/psycopg/psycopg2/commit/a95fd3df1abc0282f1c47fa2170191f037c3c8de
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

from pandas import read_sql
from numpy import logical_not
from psycopg2.sql import SQL, Identifier, Literal
from psycopg2 import connect, DatabaseError
from psycopg2.extras import execute_values
from config import config


class NoRecordIDError(UserWarning):
    """UserWarning for EquationGroup"""


class TypeTable:
    """Class to handle database managment of types - Includes Equations, Units and Variables"""

    def __init__(self, name: str = None, verbose: bool = False):
        self.name = name

        self.types_df = self.pull_data(verbose=verbose)

    def pull_data(self, verbose: bool = False):
        """Method to pull data from database"""
        table = self.name

        sql = "SELECT * FROM {tbl}"
        query = SQL(sql).format(tbl=Identifier(table))

        db_params = config()
        conn = connect(**db_params)

        out_data = read_sql(query, con=conn, index_col='type')

        if verbose:
            print('Extracting records from Table: ' + table)

        return out_data

    def insert(self, new_data, verbose: bool = False):
        """Method to Insert New Equation Records"""
        db_params = config()
        conn = connect(**db_params)
        cur = conn.cursor()

        self.types_df = self.types_df.append(new_data)

        sql = 'INSERT INTO {table} (type) VALUES %s;'
        query = SQL(sql).format(table=Identifier(self.name))

        tuples = [tuple([x]) for x in new_data.index]

        if verbose is True:
            print(query.as_string(cur))
            print('Values', tuples)

        try:
            execute_values(cur, query, tuples)
            conn.commit()
        except DatabaseError as error:
            print("Error: %s" % error)
            conn.rollback()
            cur.close()
        print("execute_values() done")
        cur.close()

    def record_count(self) -> int:
        """Method to get total number of eqn_groups"""
        return len(self.types_df)

    def reinitialize_types_df(self, verbose: bool = False):
        """Proper way to re-initialize types_df"""
        self.types_df = self.pull_data(verbose=verbose)

    def save_records(self, verbose: bool = False):
        """Method to store all data"""
        # find type_df values not stored.

        stored_data = self.pull_data(verbose)
        ind = logical_not(self.types_df.index.isin(stored_data.index))
        self.insert(new_data=self.types_df[ind])

    def delete_types(self, types, verbose: bool = False):
        """Method to Insert New Equation Records"""
        db_params = config()
        conn = connect(**db_params)
        cur = conn.cursor()

        print(type(types))

        if isinstance(types, str):
            print('you are here')
            types = tuple([types])

        sql: str = 'DELETE FROM {table} WHERE type IN ({values});'
        query = SQL(sql).format(values=SQL(', ').join(map(Literal, types)),
                                table=Identifier(self.name)
                                )

        if verbose is True:
            print(query.as_string(cur))
            print('Values', types)

        try:
            cur.execute(query, types)
            conn.commit()
        except DatabaseError as error:
            print("Error: %s" % error)
            conn.rollback()
            cur.close()

        self.reinitialize_types_df()
        print("execute_values() done")
        cur.close()

    def index(self, type_name: str) -> int:
        """Convenience function to return the location of a type with the DataFrame"""
        return self.types_df.index.get_loc(type_name)

    @staticmethod
    def if_not_none(key: str = None, value=None):
        """Add values to a dictionary if they are not None"""
        data = {}
        if value is not None:
            data = {key: value}
        return data
