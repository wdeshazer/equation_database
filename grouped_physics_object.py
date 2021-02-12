"""
A Grouped Physics Object manages the data through a dataframe that is populated based on a join table
and the data table. It is a base class so child classes should populate self data during init
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

from math import isnan
from warnings import warn
from typing import NewType, List, NamedTuple, Optional
from pandas import DataFrame, Series, read_sql
from psycopg2.sql import SQL, Identifier, Placeholder, Composed
from psycopg2 import connect, OperationalError
from psycopg2.extras import NamedTupleCursor
from latex_data import LatexData
from config import config


class RecordIDTypeError(UserWarning):
    """UserWarning for EquationGroup"""


class ImageWithoutTemplateIDError(UserWarning):
    """UserWarning for EquationGroup"""


class NoRecordIDError(UserWarning):
    """UserWarning for EquationGroup"""


class NoGroupRecordAssociationsError(UserWarning):
    """UserWarning for EquationGroup"""


Record = NewType("Record", NamedTuple)
Records = NewType("Records", List[Record])


def generic_pull_grouped_data(table_name: str = None, parent_table_name: str = None) -> DataFrame:
    """Multi-index Extract DataFrame DB"""
    table_id_name: str = table_name + '_id'
    parent_id_name: str = parent_table_name + '_id'
    join_table: str = table_name + '_' + parent_table_name

    sql = 'SELECT * FROM {join_table} RIGHT JOIN {table} USING({table_id})'

    query = SQL(sql).format(
        table=Identifier(table_name),
        join_table=Identifier(join_table),
        table_id=Identifier(table_id_name)
    )

    db_params = config()
    conn = connect(**db_params)

    data_df = read_sql(query, con=conn, index_col=[parent_id_name, table_id_name])
    # This was a good example of loading objects to file
    # data_df['latex'] = data_df['latex'].apply(loads)

    data_df['latex_obj'] = None

    for row in data_df.itertuples():
        data_df.loc[row.Index, 'latex_obj'] = \
            LatexData(latex=row.latex, template_id=row.template_id,
                      image=row.image, compiled_at=row.compiled_at)

    data_df.sort_values([parent_id_name, 'insertion_order'], inplace=True)

    return data_df


def generic_associate_parent(parent_id: int = None, child_id: int = None,
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

    data_df = \
        generic_pull_grouped_data(table_name=table_name, parent_table_name=parent_table_name)

    return data_df


def generic_last_equation_number(table_data: Optional[DataFrame] = None) -> int:
    """Record Count using dataframe"""
    numbers: Series = table_data.loc[slice(None), 'name'].str.extract(r'^[a-zA-Z]+\s([0-9]+)$')
    rcount: Series = numbers.astype(int).max()

    if isnan(rcount.iloc[0]) is True:
        return 0

    return rcount.iloc[0]


def generic_new_record_db(parent_id: int = None, table_name: str = None, parent_table_name: str = None,
                          data_df: Optional[DataFrame] = None, name: str = None, new_record=None,
                          latex: LatexData = None, notes: str = None,
                          dimensions: int = 1, insertion_order: int = None, created_by: str = None,
                          unit_id: int = 1, verbose: bool = None) -> DataFrame:
    """Insert New Record Into math_object"""

    if new_record is None:
        new_record = {}

    db_params = config()

    table_id = table_name + '_id'
    next_id: int = generic_last_equation_number(data_df) + 1

    if name is None:
        name = "{aTable} {ID:d}".format(ID=next_id, aTable=table_name)
    if created_by is None:
        created_by = db_params['user']

    if latex is None:
        latex = LatexData()

    new_record.update(name=name, notes=notes, dimensions=dimensions, unit_id=unit_id,  type_name='Unassigned',
                      latex=latex.latex, image=latex.image, compiled_at=latex.compiled_at,
                      template_id=latex.template_id, created_by=created_by)

    query = SQL('INSERT INTO {table} ({fields}) VALUES ({values}) RETURNING *'
                ).format(table=Identifier(table_name),
                         fields=SQL(', ').join(map(Identifier, new_record.keys())),
                         values=SQL(', ').join(map(Placeholder, new_record.keys())))

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
    updated_df: Optional[DataFrame] = None

    if parent_id is not None:
        for record in new_records:
            updated_df = generic_associate_parent(
                parent_id=parent_id, child_id=getattr(record, table_id), insertion_order=insertion_order,
                table_name=table_name, parent_table_name=parent_table_name, inserted_by=created_by, verbose=verbose
            )
    else:
        updated_df = \
            generic_pull_grouped_data(table_name=table_name, parent_table_name=parent_table_name)

    return updated_df


def add_field(key: str = None, value=None):
    """Convenience Wrapper to Beautify If value is none"""
    data = {}
    if value is not None:
        data = {key: value}
    return data


class GroupedPhysicsObject:
    """Base class for Equations, Variables, and Units"""
    def __init__(self, table_name: str, parent_table_name: str):
        """Constructor for MathObject"""
        self.table_name = table_name
        self.parent_table_name = parent_table_name  # For equations it is eqn_group. For variables it is equations
        self.grouped_data: Optional[DataFrame] = None
        self.all_records: Optional[DataFrame] = None
        self.selected_parent_id: Optional[int] = None
        self.selected_data_records: Optional[Records] = None
        self.records_not_selected_unique: Optional[Records] = None
        self.pull_grouped_data()

    def id_name(self):
        """Convenience method to return id_name"""
        return self.table_name + '_id'

    def parent_table_id_name(self):
        """Convenenience method to return parent_table_id_name"""
        return self.parent_table_name + '_id'

    def pull_grouped_data(self):
        """Extract grouped data from database"""
        self.grouped_data = \
            generic_pull_grouped_data(table_name=self.table_name, parent_table_name=self.parent_table_name)
        self._set_all_records()

    def associate_parent(self, parent_id: int = None, child_id: int = None, new_record: dict = None,
                         insertion_order: int = None, inserted_by: str = None, verbose: bool = False):
        """Associate a record with a group"""
        table_name = self.table_name
        parent_table_name = self.parent_table_name

        self.grouped_data = \
            generic_associate_parent(parent_id=parent_id, child_id=child_id, new_record=new_record,
                                     table_name=table_name, parent_table_name=parent_table_name,
                                     insertion_order=insertion_order, inserted_by=inserted_by,
                                     verbose=verbose)

        if self.selected_parent_id is not None:
            self.set_records_for_parent(parent_id=self.selected_parent_id)

    def new_record(self, parent_id: int = None, name: str = None, latex: LatexData = None,
                   new_record: dict = None, notes: str = None, dimensions: int = 1,
                   insertion_order: int = None, created_by: str = None,
                   unit_id: int = 1, verbose: bool = None):
        """Insert a new_record Into """
        table_name = self.table_name
        parent_table_name = self.parent_table_name
        self.grouped_data = \
            generic_new_record_db(
                parent_id=parent_id, table_name=table_name, parent_table_name=parent_table_name,
                name=name, latex=latex, notes=notes, new_record=new_record,
                data_df=self.grouped_data, dimensions=dimensions, unit_id=unit_id,
                insertion_order=insertion_order, created_by=created_by,  verbose=verbose
            )

    def _set_all_records(self):
        self.all_records = self.grouped_data.drop_duplicates('name').droplevel(self.parent_table_id_name()).sort_index()

    def update(self, an_id: id = None, where_key: str = None, name: str = None,
               data=None, latex: LatexData = None, notes: str = None, unit_id: int = None,
               dimensions: int = None, modified_by: str = None, created_by: str = None,
               verbose: bool = None):
        """Insert New Record Into grouped_physics_object"""

        if where_key is None:
            where_key = self.id_name()

        if an_id is None:
            warn("No Record ID Specified", NoRecordIDError)
        else:
            if data is None:
                data = {}

            db_params = config()

            data.update(add_field('name', name))
            data.update(add_field('notes', notes))
            if latex is not None:
                data.update(latex=latex.latex)
                data.update(image=latex.image)
                data.update(template_id=latex.template_id)
                data.update(compiled_at=latex.compiled_at)
            data.update(add_field('dimensions', dimensions))
            data.update(add_field('unit_id', unit_id))
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

                conn = connect(**db_params)
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

                self.pull_grouped_data()

    def selected_data_df(self, parent_id: int = None) -> DataFrame:
        """Retern selected data in DataFrame form"""

        try:
            df = self.grouped_data.loc[parent_id, :]
        except KeyError:
            df: Optional[DataFrame] = None
        return df

    def set_records_for_parent(self, parent_id: int = None):
        """Sets records for parents after an update"""
        selected_data_df = self.selected_data_df(parent_id)

        if selected_data_df is None:
            self.selected_data_records = None
        else:
            self.selected_data_records = Records(list(selected_data_df.itertuples()))
        self._set_records_not_in_parent(parent_id=parent_id)

    def data_not_selected_full_df(self, parent_id: int = None):
        """Method to return data not in selected set as DataFrame"""
        if self.selected_data_records is None:
            rcd_nums_in = []
        else:
            rcd_nums_in = self.selected_data_df(parent_id=parent_id).index
        rcds_not_in = self.grouped_data.query(self.id_name() + '!=' + str(tuple(rcd_nums_in)))
        return rcds_not_in

    def data_not_selected_unique_df(self, parent_id: int = None):
        """Method to return unique data not in selected set as DataFrame"""
        rcds_not_in = self.data_not_selected_full_df(parent_id=parent_id)
        uniq = rcds_not_in.drop_duplicates('name').droplevel(self.parent_table_id_name()).sort_index()
        return uniq

    def data_not_selected_unique_rcds(self, parent_id: int = None):
        """Method to return unique data not in selected set as Records"""
        uniq = self.data_not_selected_unique_df(parent_id=parent_id)
        return Records(list(uniq.itertuples()))

    def _set_records_not_in_parent(self, parent_id: int = None):
        """Store Unique Records to file"""
        self.records_not_selected_unique = self.data_not_selected_unique_rcds(parent_id=parent_id)
