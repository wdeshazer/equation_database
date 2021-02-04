"""
Equation Group Provides helper functions for pulling the LaTeX template from the equations database

https://www.psycopg.org/docs/sql.html#
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

from warnings import warn
from config import config
from db_utils import append, get_data, insert, record_count_total, update, if_not_none


class NoRecordIDError(UserWarning):
    """UserWarning for EquationGroup"""


class EquationGroup:
    """Class for managing and interfacing with Postgres Table eqn_group"""
    def __init__(self):
        """Constructor for eqn_group"""
        self.table = 'eqn_group'
        self.records: dict = self.get_equation_group_data()
        self.last_inserted = None
        self.id_name = self.table + '_id'

    def get_equation_group_data(self, as_columns: bool = True, verbose: bool = False):
        """Method to pull data from database"""
        return get_data(table=self.table, as_columns=as_columns, verbose=verbose)

    def insert(self, name: str = None, notes: str = None,
               created_by: str = None, as_column: bool = True, verbose: bool = False):
        """Method to Insert New Equation Records"""
        db_params = config()

        next_id: int = self.record_count_total(verbose=verbose) + 1

        if name is None:
            name = "{aTable} {ID:d}".format(ID=next_id, aTable=self.table)
        if created_by is None:
            created_by = db_params['user']

        # data = {'name': 'New Group', 'notes': 'I hope this works', 'created_by': 'razor'}

        data = dict(
            name=name,
            notes=notes,
            created_by=created_by
        )

        new_records = insert(table=self.table, data=data, as_column=as_column, verbose=verbose)

        self.last_inserted = new_records
        self.records = append(existing_records=self.records, new_records=new_records)

    def update(self, an_id: id = None, where_key: str = 'id', name: str = None,
               data=None, notes: str = None, modified_by: str = None, created_by: str = None,
               code_file_path: str = None, as_column: bool = True, verbose: bool = None):
        """Insert New Record Into math_object"""

        if an_id is None:
            warn("No Record ID Specified", NoRecordIDError)
        else:
            if data is None:
                data = {}

            # add_field only add if there is a value available

            data.update(if_not_none('name', name))
            data.update(if_not_none('notes', notes))
            data.update(if_not_none('code_file_path', code_file_path))
            data.update(if_not_none('created_by', created_by))
            data.update(if_not_none('modified_by', modified_by))

            # If there is no data, then skip. Of course one could still change modified by:
            if len(data) > 0:
                new_record = update(table=self.table, an_id=an_id, where_key=where_key,
                                    as_column=as_column, verbose=verbose)

                self.last_inserted = new_record

                self.records = self.get_equation_group_data()

    def record_count_total(self, verbose: bool = False) -> int:
        """Method to get total number of eqn_groups"""
        return record_count_total(table=self.table, verbose=verbose)
