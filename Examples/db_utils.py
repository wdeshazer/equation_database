"""
Equation Group Provides helper functions for pulling the LaTeX template from the equations database

https://www.psycopg.org/docs/sql.html#
https://stackoverflow.com/questions/41837339/pandas-multilevel-index-to-and-from-sql
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

from collections import defaultdict, namedtuple
from warnings import warn
from typing import NamedTuple, Union
from pandas import DataFrame, read_sql
from psycopg2.sql import SQL, Identifier, Placeholder, Composed
from psycopg2 import connect, OperationalError, Binary
from psycopg2.extras import NamedTupleCursor
from config import config
from latex_template import compile_pattern, template


class NoRecordIDError(UserWarning):
    """UserWarning for EquationGroup"""


def get_data(table: str = None, as_columns: bool = True, verbose: bool = False):
    """Method to pull data from database"""
    sql = "SELECT * FROM {tbl}"
    query = SQL(sql).format(tbl=Identifier(table))

    db_params = config()
    conn = connect(**db_params)

    cur = conn.cursor(cursor_factory=NamedTupleCursor)

    if verbose:
        print('Extracting records from Table: ' + table)

    try:
        cur.execute(query)
    except OperationalError as error:
        print(error)

    records = cur.fetchall()

    if as_columns is True:
        records = columnify(records)

    cur.close()
    conn.close()

    return records


def insert(table: str = None, data: dict = None, as_column=True, verbose: bool = False):
    """Method to Insert New Equation Records"""
    db_params = config()

    sql = 'INSERT INTO {table} ({}) VALUES ({}) RETURNING *'

    keys = data.keys()

    query = SQL(sql).format(
        SQL(', ').join(map(Identifier, keys)),
        SQL(', ').join(map(Placeholder, keys)),
        table=Identifier(table)
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

    if as_column is True:
        new_record = columnify(new_record)
    return new_record


def update(table: str = None, an_id: id = None, where_key: str = 'id',
           data: dict = None, as_column: bool = True, verbose: bool = None):
    """Insert New Record Into math_object"""

    db_params = config()

    if 'modified_by' not in data:
        data.update(modified_by=db_params['user'])

    fields = data.keys()

    sql = "UPDATE {table} SET {fields} WHERE {pkey} = {a_value} RETURNING *"

    query = SQL(sql).format(table=Identifier(table),
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

    if as_column is True:
        new_record = columnify(new_record)

    return new_record


def self_named_tuple_example(table_name: str = None, parent_table_name: str = None):
    """Multi-index Extract DataFrame DB"""
    table_id: str = table_name + '_id'
    parent_id: str = parent_table_name + '_id'
    join_table: str = table_name + '_' + parent_table_name

    sql = 'SELECT * FROM {join_table} RIGHT JOIN {table} USING({table_id})'

    self_dict = dict(table_name=table_name, join_table=join_table,
                     table_id=table_id, parent_id=parent_id)
    MyTuple = namedtuple('MyTuple', self_dict)
    # noinspection PyArgumentList
    self = MyTuple(**self_dict)

    query = SQL(sql).format(
        table=Identifier(self.table_name),
        join_table=Identifier(self.join_table),
        table_id=Identifier(self.table_id)
    )

    db_params = config()
    conn = connect(**db_params)

    df = read_sql(query, con=conn, index_col=[self.parent_id, self.table_id])
    return df


def append(existing_records: dict = None, new_records: Union[NamedTuple, dict] = None):
    """Append new records to existing records. Because the data is stored as a dictionary instead of
    NamedTuples, it requires a helper function to append new data"""
    res = existing_records

    if isinstance(new_records, NamedTuple):
        for data in new_records:
            # noinspection PyProtectedMember
            record: dict = data._asdict()
            for key, value in record.items():
                res[key].append(value)
    elif isinstance(new_records, dict):
        for key, value in new_records.items():
            res[key].append(value)
    else:
        warn("Unrecognized type to append", UserWarning)

    return res


def record_count_total(table: str = None, verbose: bool = False) -> int:
    """Method to get total number of eqn_groups"""
    sql = "SELECT COUNT(*) from {table}"

    query = SQL(sql).format(table=Identifier(table))

    db_params = config()
    conn = connect(**db_params)

    cur = conn.cursor(cursor_factory=NamedTupleCursor)

    if verbose:
        print('Getting Count of Records in table: {table}'.format(table=table))

    cur.execute(query)  # self.table))

    record_count = cur.fetchone()

    cur.close()
    conn.close()

    return record_count[0]


def if_not_none(key: str = None, value=None):
    """Add values to a dictionary if they are not None"""
    data = {}
    if value is not None:
        data = {key: value}
    return data


def columnify(records):
    """Helper function to turn NameTuple records into column-like dictionaries"""
    res = defaultdict(list)

    # https://gist.github.com/pylover/7870c235867cf22817ac5b096defb768
    for data in records:

        # noinspection PyProtectedMember
        record = data._asdict()  # type: dict
        for key, value in record.items():
            res[key].append(value)
    return res

# region DataFrame
# The following utilities manage the database using MultiIndex dataframes,
# which is a combination of parent and child tables

# DataFrame Notes
# df.loc[('equation_id', 'variable_id'), fields] - This is not how to use, but the structure
# df.loc[(1, 22), :] all fields for eq=1 v=22
# df.loc[1, :] all fields and vars for eq=1
# a = df.loc[1, 'name'], type(a) pandas.core.series.Series, a[22]='variable 22', a.iloc[0]='variable 22'
# df.loc[(1, slice(None)), 'name']
# df.loc[slice(None), 'name'] all names for equations and variables
# df.loc[(slice(None), 22), 'name'] all names for variable 22
#


def extract_db(table_name: str = None, parent_table_name: str = None) -> DataFrame:
    """Multi-index Extract DataFrame DB"""
    table_id: str = table_name + '_id'
    parent_id: str = parent_table_name + '_id'
    join_table: str = table_name + '_' + parent_table_name

    sql = 'SELECT * FROM {join_table} RIGHT JOIN {table} USING({table_id})'

    query = SQL(sql).format(
        table=Identifier(table_name),
        join_table=Identifier(join_table),
        table_id=Identifier(table_id)
    )

    db_params = config()
    conn = connect(**db_params)

    df = read_sql(query, con=conn, index_col=[parent_id, table_id])
    return df


def save_db(table_name: str = None, parent_table_name: str = None):
    """Multi-index Extract DataFrame DB"""
    table_id: str = table_name + '_id'
    parent_id: str = parent_table_name + '_id'
    join_table: str = table_name + '_' + parent_table_name

    sql = 'SELECT * FROM {join_table} RIGHT JOIN {table} USING({table_id})'

    query = SQL(sql).format(
        table=Identifier(table_name),
        join_table=Identifier(join_table),
        table_id=Identifier(table_id)
    )

    db_params = config()
    conn = connect(**db_params)

    df = read_sql(query, con=conn, index_col=[parent_id, table_id])
    return df


def new_record_db(parent_id: int = None, table_name: str = None, parent_table_name: str = None,
                  data_df: DataFrame = None,
                  name: str = None, new_record=None, latex: str = None, notes: str = None,
                  image: bytes = None, template_id: int = None, dimensions: int = 1,
                  insertion_order: int = None, created_by: str = None, unit_id: int = 1,
                  verbose: bool = None) -> DataFrame:
    """Insert New Record Into math_object"""

    if new_record is None:
        new_record = {}

    db_params = config()

    table_id = table_name + '_id'
    next_id: int = record_count_total_db(data_df, table_id=table_id) + 1

    if name is None:
        name = "{aTable} {ID:d}".format(ID=next_id, aTable=table_name)
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

    new_record.update(name=name, latex=latex, image=image, notes=notes, dimensions=dimensions,
                      unit_id=unit_id, template_id=template_id, created_by=created_by,
                      type='Conservation')

    sql = 'INSERT INTO {table} ({fields}) VALUES ({values}) RETURNING *'

    keys = new_record.keys()

    query = SQL(sql).format(table=Identifier(table_name),
                            fields=SQL(', ').join(map(Identifier, keys)),
                            values=SQL(', ').join(map(Placeholder, keys)))

    conn = connect(**db_params)

    if verbose:
        print(query.as_string(conn))

    cur = conn.cursor(cursor_factory=NamedTupleCursor)

    if verbose:
        print('Adding new record to Table: {aTable}'.format(aTable=table_name))

    try:
        cur.execute(query, new_record)
    except OperationalError as error:
        print(error)

    new_records = cur.fetchall()
    conn.commit()
    cur.close()

    if parent_id is not None:
        for record in new_records:
            associate_parent(parent_id=parent_id, child_id=getattr(record,table_id), insertion_order=insertion_order,
                             table_name=table_name, parent_table_name=parent_table_name)

    updated_df = extract_db(table_name=table_name, parent_table_name=parent_table_name)
    return updated_df


def record_count_total_db(table_data: DataFrame, table_id: str = None) -> int:
    return table_data.index.get_level_values(table_id).max()


# def record_count_for_parent(self, parent_id: Tuple[int, ...] = None,
#                             verbose: bool = False):
#     """Return record count for Parent Table"""
#     sql: str = None
#
#     if isinstance(parent_id, tuple):
#         sql = "SELECT COUNT(*) from {table} WHERE {parent_key} IN %s"
#     elif isinstance(parent_id, int):
#         sql = "SELECT COUNT(*) from {table} WHERE {parent_key}= %s"
#     else:
#         warn("Unrecognized type for parent_id", RecordIDTypeError)
#
#     query = SQL(sql).format(table=Identifier(self.join_table()),
#                             parent_key=Identifier(self.parent_key())
#                             )
#
#     db_params = config()
#     conn = connect(**db_params)
#
#     cur = conn.cursor(cursor_factory=NamedTupleCursor)
#
#     if verbose:
#         print('Getting Count of Records in table: {table} for Group ID: {gid}'.format(table=self.join_table(),
#                                                                                       gid=parent_id))
#         print(query.as_string(conn))
#         if isinstance(parent_id, int):
#             cur.mogrify(query, parent_id)
#         elif isinstance(parent_id, tuple):
#             cur.mogrify(query, (parent_id, ))
#
#     try:
#         cur.execute(query, (parent_id,))
#     except TypeError:
#         cur.execute(query, parent_id)  # self.table))
#     except OperationalError as error:
#         print(error)
#
#     record_count = cur.fetchone()
#
#     cur.close()
#     conn.close()
#
#     return record_count[0]


def associate_parent(parent_id: int = None, child_id: int = None,
                     table_name: str = None, parent_table_name: str = None,
                     insertion_order: int = None, inserted_by: str = None,
                     new_record: dict = None, verbose: bool = False):
    """Associate the parent and child tables using parent id. Insertion_order and inserted_by are optional"""
    parent_key = parent_table_name + '_id'
    self_key = table_name + '_id'

    join_table = table_name + '_' + parent_table_name

    db_params = config()

    if new_record is None:
        new_record = {}

    if inserted_by is None:
        inserted_by = db_params['user']

    new_record.update(
        {parent_key: parent_id, self_key: child_id},
        insertion_order=insertion_order,
        inserted_by=inserted_by
    )

    sql = 'INSERT INTO {table} ({fields}) VALUES ({values})'

    keys = new_record.keys()

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
        cur.execute(query, new_record)
    except OperationalError as error:
        print(error)

    conn.commit()

    cur.close()


# endregion