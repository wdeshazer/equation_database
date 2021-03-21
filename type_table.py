"""
Equation Group Provides helper functions for pulling the LaTeX show_template_manager from the equations database

https://www.psycopg.org/docs/sql.html#
https://naysan.ca/2020/05/09/pandas-to-postgresql-using-psycopg2-bulk-insert-performance-benchmark/
https://github.com/psycopg/psycopg2/commit/a95fd3df1abc0282f1c47fa2170191f037c3c8de
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

from typing import Optional
from pandas import read_sql
from numpy import logical_not
from psycopg2.sql import SQL, Identifier, Literal
from psycopg2 import DatabaseError
from psycopg2.extras import execute_values
from time_logging import TimeLogger
from db_utils import my_connect


class NoRecordIDError(UserWarning):
    """UserWarning for EquationGroup"""


class TypeTable:
    """Class to handle database managment of types - Includes Equations, Units and Variables"""

    def __init__(self, name: str, my_conn: Optional[dict] = None, t_log: Optional[TimeLogger] = None,
                 verbose: bool = False):
        self.name = name
        self.my_conn = my_conn
        self.types_df = self.pull_data(my_conn=my_conn, t_log=t_log, verbose=verbose)

    def pull_data(self, my_conn: Optional[dict] = None, t_log: Optional[TimeLogger] = None, verbose: bool = False):
        """Method to pull data from database"""
        table = self.name

        if verbose is True and t_log is None:
            t_log = TimeLogger()

        sql = "SELECT * FROM {tbl}"
        query = SQL(sql).format(tbl=Identifier(table))

        if my_conn is None:
            my_conn = self.my_conn
        else:
            self.my_conn = my_conn

        my_conn = my_connect(my_conn=my_conn, t_log=t_log, verbose=verbose)
        conn = my_conn['conn']

        out_data = read_sql(query, con=conn, index_col='type_name')

        if verbose:
            t_log.new_event('Extracting records from Table: ' + table)

        return out_data

    def insert(self, new_data, my_conn: Optional[dict] = None, t_log: Optional[TimeLogger] = None,
               verbose: bool = False):
        """Method to Insert New Equation Records"""

        if verbose is True and t_log is None:
            t_log = TimeLogger()

        if my_conn is None:
            my_conn = self.my_conn
        else:
            self.my_conn = my_conn

        my_conn = my_connect(my_conn=my_conn, t_log=t_log, verbose=verbose)
        conn = my_conn['conn']

        cur = conn.cursor()

        self.types_df = self.types_df.append(new_data)

        sql = 'INSERT INTO {table} (type_name) VALUES %s;'
        query = SQL(sql).format(table=Identifier(self.name))

        tuples = [tuple([x]) for x in new_data.index]

        if verbose is True:
            print(query.as_string(cur))
            print('Values', tuples)
            t_log.new_event('Loading: ' + self.name)

        try:
            execute_values(cur, query, tuples)
            conn.commit()
        except DatabaseError as error:
            print("Error: %s" % error)
            conn.rollback()
            cur.close()

        if verbose is True:
            t_log.new_event("execute_values() done")
        cur.close()

    def types(self):
        """Returns Types as Numpy"""
        return self.types_df.index.to_list()

    def record_count(self) -> int:
        """Method to get total number of eqn_groups"""
        return len(self.types_df)

    def reinitialize_types_df(self, my_conn: Optional[dict] = None, t_log: Optional[TimeLogger] = None,
                              verbose: bool = False):
        """Proper way to re-initialize types_df"""
        if my_conn is True:
            my_conn = self.my_conn
        else:
            self.my_conn = my_conn

        self.types_df = self.pull_data(my_conn=my_conn, t_log=t_log, verbose=verbose)

    def save_records(self, my_conn: Optional[dict] = None, t_log: Optional[TimeLogger] = None, verbose: bool = False):
        """Method to store all data"""
        # find type_df values not stored.

        if my_conn is True:
            my_conn = self.my_conn
        else:
            self.my_conn = my_conn

        stored_data = self.pull_data(my_conn=my_conn, t_log=t_log, verbose=verbose)
        ind = logical_not(self.types_df.index.isin(stored_data.index))
        self.insert(my_conn=my_conn, t_log=t_log, new_data=self.types_df[ind])

    def delete_types(self, types, my_conn: Optional[dict] = None, t_log: Optional[TimeLogger] = None,
                     verbose: bool = False):
        """Method to Insert New Equation Records"""
        if my_conn is None:
            my_conn = self.my_conn
        else:
            self.my_conn = my_conn

        if verbose is True and t_log is None:
            t_log = TimeLogger()

        my_conn = my_connect(my_conn=my_conn, t_log=t_log, verbose=verbose)
        conn = my_conn['conn']
        cur = conn.cursor()

        if verbose is True:
            t_log.new_event(type(types))
            if isinstance(types, str):
                print('you are here')
                types = tuple([types])

        sql: str = 'DELETE FROM {table} WHERE type_name IN ({values});'
        query = SQL(sql).format(values=SQL(', ').join(map(Literal, types)),
                                table=Identifier(self.name)
                                )

        if verbose is True:
            print(query.as_string(cur))
            t_log.new_event('Values' + str(types))
            t_log.new_event('Pulling Data for: ' + self.name)

        try:
            cur.execute(query, types)
            conn.commit()
        except DatabaseError as error:
            print("Error: %s" % error)
            conn.rollback()
            cur.close()

        self.reinitialize_types_df(my_conn=my_conn, t_log=t_log, verbose=verbose)

        if verbose is True:
            t_log.new_event("execute_values() done")

        cur.close()

    def index(self, type_name: str) -> int:
        """Convenience function to return the location of a type with the DataFrame"""
        return self.types_df.index.get_loc(type_name)
