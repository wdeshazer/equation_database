"""
Unit Provides helper functions for managing Unit and their associations
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

from collections import namedtuple
from warnings import warn
from typing import Optional, List, Tuple, NamedTuple
from pandas import DataFrame, read_sql, Timestamp
from psycopg2.sql import SQL, Identifier, Placeholder, Composed
from psycopg2 import OperationalError
from psycopg2.extras import NamedTupleCursor
from latex_data import LatexData
from time_logging import TimeLogger
from db_utils import my_connect


class NoRecordIDError(UserWarning):
    """UserWarning for EquationGroup"""


def generic_pull_data(table_name: str = None, my_conn: Optional[dict] = None,
                      t_log: Optional[TimeLogger] = None, verbose: bool = False) -> DataFrame:
    """Multi-index Extract DataFrame DB"""
    table_id_name: str = table_name + '_id'

    query = SQL('SELECT * FROM {table}').format(table=Identifier(table_name))

    my_conn = my_connect(my_conn=my_conn, t_log=t_log, verbose=verbose)
    conn = my_conn['conn']

    data_df = read_sql(query, con=conn, index_col=table_id_name)

    data_df['latex_obj'] = None

    for row in data_df.itertuples():
        data_df.loc[row.Index, 'latex_obj'] = \
            LatexData(my_conn=my_conn, latex=row.latex, template_id=row.template_id,
                      image=row.image, compiled_at=row.compiled_at)

    return data_df


def generic_record_count(data_df: DataFrame) -> int:
    """Method to get total number of eqn_groups"""
    return len(data_df)


def generic_new_record_db(table_name: str = None, data_df: Optional[DataFrame] = None, name: str = None,
                          new_record=None, latex: LatexData = None, notes: str = None, created_by: str = None,
                          my_conn: Optional[dict] = None, t_log: Optional[TimeLogger] = None,
                          verbose: bool = None) -> DataFrame:
    """Insert New Record Into math_object"""

    if new_record is None:
        new_record = {}

    my_conn = my_connect(my_conn=my_conn, t_log=t_log, verbose=verbose)
    conn = my_conn['conn']
    db_params = my_conn['db_params']

    next_id: int = generic_record_count(data_df) + 1

    if name is None:
        name = "{aTable} {ID:d}".format(ID=next_id, aTable=table_name)
    if created_by is None:
        created_by = db_params['user']

    if latex is None:
        latex = LatexData()

    new_record.update(name=name, notes=notes, latex=latex.latex, image=latex.image, compiled_at=latex.compiled_at,
                      template_id=latex.template_id, created_by=created_by)

    query = SQL('INSERT INTO {table} ({fields}) VALUES ({values})'
                ).format(table=Identifier(table_name),
                         fields=SQL(', ').join(map(Identifier, new_record.keys())),
                         values=SQL(', ').join(map(Placeholder, new_record.keys())))

    if verbose:
        print(query.as_string(conn))

    cur = conn.cursor(cursor_factory=NamedTupleCursor)

    if verbose:
        print('Adding new record to Table: {aTable}'.format(aTable=table_name))

    try:
        cur.execute(query, new_record)
    except OperationalError as error:
        print(error)

    conn.commit()
    cur.close()
    updated_df = \
        generic_pull_data(table_name=table_name, my_conn=my_conn, t_log=t_log, verbose=verbose)
    return updated_df


def add_field(key: str = None, value=None):
    """Convenience Wrapper to Beautify If value is none"""
    data = {}
    if value is not None:
        data = {key: value}
    return data


class PhysicsObject(NamedTuple):
    Index: int
    name: str
    latex: str
    notes: str
    image: bytes
    template_id: int
    image_is_dirty: bool
    created_at: Timestamp
    created_by: str
    modified_at: Timestamp
    modified_by: str
    compiled_at: Timestamp
    dimension: int
    unit_id: int
    type_name: str
    latex_obj: LatexData


class PhysicsObjectInput(NamedTuple):
    name: str
    latex_obj: LatexData
    notes: str
    created_by: str
    dimensions: int
    unit_id: int
    type_name: str


ExistingEquationRecordInput = \
    namedtuple('ExistingEquationRecordInput',
               ['equation_id', 'name', 'latex_obj', 'modified_by', 'dimensions', 'unit_id', 'type_name'])


class PhysicsObjects:
    """Class for managing and interfacing with Postgres Table eqn_group"""
    def __init__(self, table_name: str, my_conn: Optional[dict] = None, t_log: Optional[TimeLogger] = None,
                 verbose: bool = False):
        """Constructor for eqn_group"""
        self.table_name = table_name
        self.all_records_df: Optional[DataFrame] = None
        self.all_records: Optional[List[Tuple]] = None
        self.my_conn = my_conn
        self.pull_data(my_conn=my_conn, t_log=t_log, verbose=verbose)

    def id_name(self):
        """Convenience method to return id_name"""
        return self.table_name + '_id'

    def pull_data(self, my_conn: Optional[dict] = None, t_log: Optional[TimeLogger] = None, verbose: bool = False):
        """Method to pull data from database"""
        if my_conn is None:
            my_conn = self.my_conn
        self.all_records_df = generic_pull_data(table_name=self.table_name, my_conn=my_conn,
                                                t_log=t_log, verbose=verbose)
        self.all_records = list(self.all_records_df.itertuples())

    def new_record(self, name: str = None, latex: LatexData = None,
                   new_record: dict = None, notes: str = None, created_by: str = None,
                   my_conn: Optional[dict] = None, t_log: Optional[TimeLogger] = None, verbose: bool = False
                   ):
        """Insert a new_record Into """
        table_name = self.table_name

        if my_conn is None:
            my_conn = self.my_conn

        self.all_records_df = \
            generic_new_record_db(
                table_name=table_name, name=name, latex=latex, notes=notes, new_record=new_record,
                my_conn=my_conn, t_log=t_log, data_df=self.all_records_df, created_by=created_by,
                verbose=verbose
            )
        self.all_records = list(self.all_records_df.itertuples())

    def update(self, an_id: int = None, where_key: str = None, name: str = None,
               data=None, latex: LatexData = None, notes: str = None,
               modified_by: str = None, created_by: str = None,
               my_conn: Optional[dict] = None, t_log: Optional[TimeLogger] = None, verbose: bool = False
               ):
        """Insert New Record Into grouped_physics_object"""

        if where_key is None:
            where_key = self.id_name()

        if an_id is None:
            warn("No Record ID Specified", NoRecordIDError)
        else:
            if data is None:
                data = {}

            if my_conn is None:
                my_conn = self.my_conn

            my_conn = my_connect(my_conn=my_conn, t_log=t_log, verbose=verbose)
            conn = my_conn['conn']
            db_params = my_conn['db_params']

            data.update(add_field('name', name))
            data.update(add_field('notes', notes))
            if latex is not None:
                data.update(latex=latex.latex)
                data.update(image=latex.image)
                data.update(template_id=latex.template_id)
                data.update(compiled_at=latex.compiled_at)
            data.update(add_field('created_by', created_by))

            # If there is no data, then skip. Of course one could still change modified by:
            if len(data) > 0 or modified_by is not None:

                # Always require a modified by and because one can change data without specifying a modifer,
                # this is necessary. We don't check it before the previous if, because we don't want to create
                # a modified_by if not data was set and no modified_by was set.
                if modified_by is None:
                    modified_by = db_params['user']

                data.update(modified_by=modified_by)

                fields = data.keys()

                sql = "UPDATE {table} SET {fields} WHERE {pkey} = {a_value}"

                query = SQL(sql).format(
                    table=Identifier(self.table_name),
                    fields=SQL(', ').join(
                        Composed([Identifier(k), SQL(' = '), Placeholder(k)]) for k in fields
                    ),
                    pkey=Identifier(where_key),
                    a_value=Placeholder('where_key')
                )

                data.update(where_key=an_id)

                cur = conn.cursor(cursor_factory=NamedTupleCursor)

                if verbose:
                    print(query.as_string(conn))
                    print(cur.mogrify(query, data))

                try:
                    cur.execute(query, data)
                except OperationalError as error:
                    print(error)

                conn.commit()

                cur.close()

                self.pull_data(my_conn=my_conn, t_log=t_log, verbose=verbose)

    def record(self, an_id: int = None):
        """Returns individual record based on id"""
        record_series: List = self.all_records_df.loc[an_id].to_list()
        record_series.insert(0, an_id)
        record = PhysicsObject(*record_series)
        return record
