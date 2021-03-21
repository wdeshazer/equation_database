"""
Template table Functions

https://www.psycopg.org/docs/sql.html#
https://naysan.ca/2020/05/09/pandas-to-postgresql-using-psycopg2-bulk-insert-performance-benchmark/
https://github.com/psycopg/psycopg2/commit/a95fd3df1abc0282f1c47fa2170191f037c3c8de
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

from collections import namedtuple
from typing import Optional, List, Tuple
from pathlib import Path
from pandas import DataFrame, read_sql
from psycopg2.sql import SQL, Identifier, Literal, Placeholder
from psycopg2 import DatabaseError
from psycopg2.extras import NamedTupleCursor
from time_logging import TimeLogger
from db_utils import my_connect


class NoRecordIDError(UserWarning):
    """UserWarning"""


TemplateRecord = namedtuple('TemplateRecord', ['id', 'data', 'created_at', 'created_by'])
TemplateRecordInput = namedtuple('TemplateRecordInput', ['data', 'created_by'])


class TemplateTable:
    """Class to handle database managment of templates"""
    name = 'template'
    data_df: DataFrame
    records: List[TemplateRecord]

    def __init__(self, my_conn: Optional[dict] = None, t_log: Optional[TimeLogger] = None,
                 verbose: bool = False):
        self.my_conn = my_conn
        self.pull_data(my_conn=my_conn, t_log=t_log, verbose=verbose)
        self.recors = list(self.data_df.itertuples())

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
        self.my_conn = my_conn

        out_data = read_sql(query, con=conn, index_col='id')

        if verbose:
            t_log.new_event('Extracting records from Table: ' + table)

        self.data_df = out_data
        self.records = list(out_data.itertuples())

    def new_record(self, new_record: TemplateRecordInput, my_conn: Optional[dict] = None,
                   t_log: Optional[TimeLogger] = None, verbose: bool = False):
        """Method to Insert New Equation Records"""
        table_name = self.name

        if verbose is True and t_log is None:
            t_log = TimeLogger()

        if my_conn is None:
            my_conn = self.my_conn
        else:
            self.my_conn = my_conn

        my_conn = my_connect(my_conn=my_conn, t_log=t_log, verbose=verbose)
        conn = my_conn['conn']

        query = SQL('INSERT INTO {table} ({fields}) VALUES ({values})'
                    ).format(table=Identifier(table_name),
                             fields=SQL(', ').join(map(Identifier, new_record._fields)),
                             values=SQL(', ').join(map(Placeholder, new_record._fields))
                             )

        if verbose:
            t_log.new_event(query.as_string(conn))

        cur = conn.cursor(cursor_factory=NamedTupleCursor)

        if verbose:
            t_log.new_event('Adding new record to Table: {aTable}'.format(aTable=table_name))

        try:
            cur.execute(query, new_record._asdict())
        except DatabaseError as error:
            print(error)

        conn.commit()

        cur.close()

        self.pull_data()

    def available_template_ids(self):
        """Returns Types as Numpy"""
        return self.data_df.index.tolist()

    def record_count(self) -> int:
        """Method to get total number of eqn_groups"""
        return len(self.data_df)

    def delete(self, id_tup: Tuple, my_conn: Optional[dict] = None, t_log: Optional[TimeLogger] = None,
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

        sql: str = 'DELETE FROM {table} WHERE id IN ({values});'
        query = SQL(sql).format(values=SQL(', ').join(map(Literal, id_tup)),
                                table=Identifier(self.name)
                                )

        self.pull_data()

        if verbose is True:
            t_log.new_event("execute_values() done")
        try:
            cur.execute(query, id_tup)
            conn.commit()
        except DatabaseError as error:
            print("Error: %s" % error)
            conn.rollback()
            cur.close()

    @staticmethod
    def import_template_from_file(path: str = 'LaTeX', filename: str = 'eq_template.tex'):
        p = Path(path, filename)

        with open(p) as f:
            data = f.read()

        return data

    def new_record_from_file(self, path: str = 'LaTeX', filename: str = 'eq_template.tex',
                             created_by: Optional[str] = None, verbose: bool = False):  # noqa

        if created_by is None:
            created_by = self.my_conn['db_params']['user']

        record_dict = dict(data=self.import_template_from_file(path=path, filename=filename),
                           created_by=created_by)

        record = TemplateRecordInput(**record_dict)
        self.new_record(new_record=record, )
