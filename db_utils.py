"""
Equation Group Provides helper functions for pulling the LaTeX template from the equations database

https://www.psycopg.org/docs/sql.html#
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

from collections import defaultdict
from warnings import warn
from typing import NamedTuple, Union
from psycopg2.sql import SQL, Identifier, Placeholder, Composed
from psycopg2 import connect, OperationalError
from psycopg2.extras import NamedTupleCursor
from config import config


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
