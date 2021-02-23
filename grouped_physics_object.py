"""
A Grouped Physics Object manages the data through a dataframe that is populated based on a join table
and the data table. It is a base class so child classes should populate self data during init
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

from warnings import warn
from typing import NewType, List, NamedTuple, Optional
from pandas import DataFrame, Series, read_sql
from psycopg2.sql import SQL, Identifier, Placeholder, Composed
from psycopg2 import OperationalError
from psycopg2.extras import NamedTupleCursor

from db_utils import my_connect
from latex_data import LatexData
from time_logging import TimeLogger


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


def generic_pull_grouped_data(table_name: str = None, parent_table_name: str = None,
                              verbose: bool = False, my_conn: Optional[dict] = None,
                              t_log: Optional[TimeLogger] = None) -> DataFrame:
    """Multi-index Extract DataFrame DB"""

    table_id_name: str = table_name + '_id'
    parent_id_name: str = parent_table_name + '_id'
    join_table: str = table_name + '_' + parent_table_name

    if verbose is True and t_log is None:
        t_log = TimeLogger()

    my_conn = my_connect(my_conn=my_conn, t_log=t_log, verbose=verbose)
    conn = my_conn['conn']

    sql = 'SELECT * FROM {join_table} RIGHT JOIN {table} USING({table_id})'

    query = SQL(sql).format(
        table=Identifier(table_name),
        join_table=Identifier(join_table),
        table_id=Identifier(table_id_name)
    )

    if verbose is True:
        t_log.new_event('Loading Database: ' + table_name)

    data_df = read_sql(query, con=conn, index_col=[parent_id_name, table_id_name])
    # This was a good example of loading objects to file
    # data_df['latex'] = data_df['latex'].apply(loads)

    data_df['latex_obj'] = None

    for row in data_df.itertuples():
        data_df.loc[row.Index, 'latex_obj'] = \
            LatexData(my_conn=my_conn, latex=row.latex, template_id=row.template_id,
                      image=row.image, compiled_at=row.compiled_at)

    data_df.sort_values([parent_id_name, 'insertion_order', 'created_at'], inplace=True)

    if verbose is True:
        t_log.new_event('Database Loaded: ' + table_name)

    return data_df


def generic_associate_parent(parent_id: int = None, child_id: int = None,
                             table_name: str = None, parent_table_name: str = None,
                             insertion_order: int = None, inserted_by: str = None,
                             new_record: dict = None, verbose: bool = False,
                             my_conn: Optional[dict] = None, t_log: Optional[TimeLogger] = None):
    """Associate the parent and child tables using parent id. Insertion_order and inserted_by are optional"""
    parent_key = parent_table_name + '_id'
    self_key = table_name + '_id'

    join_table = table_name + '_' + parent_table_name

    if verbose is True and t_log is None:
        t_log = TimeLogger()

    my_conn = my_connect(my_conn=my_conn, t_log=t_log, verbose=verbose)
    conn = my_conn['conn']
    db_params = my_conn['db_params']

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

    cur = conn.cursor(cursor_factory=NamedTupleCursor)

    if verbose is True:
        t_log.new_event('Associating Tables: ' + join_table)

    try:
        cur.execute(query, new_record)
    except OperationalError as error:
        print(error)

    conn.commit()
    cur.close()

    data_df = \
        generic_pull_grouped_data(table_name=table_name, parent_table_name=parent_table_name,
                                  my_conn=my_conn, t_log=t_log, verbose=verbose)

    if verbose is True:
        t_log.new_event('Finished Associating: ' + join_table)

    return data_df


def generic_disassociate_parent(parent_id: int = None, child_id: int = None,
                                table_name: str = None, parent_table_name: str = None,
                                my_conn: Optional[dict] = None, t_log: Optional[TimeLogger] = None,
                                verbose: bool = False):
    """Associate the parent and child tables using parent id. Insertion_order and inserted_by are optional"""
    parent_key = parent_table_name + '_id'
    self_key = table_name + '_id'

    join_table = table_name + '_' + parent_table_name

    if verbose is True and t_log is None:
        t_log = TimeLogger()

    my_conn = my_connect(my_conn=my_conn, t_log=t_log, verbose=verbose)
    conn = my_conn['conn']

    sql = 'DELETE FROM {table} WHERE ({self_id}, {parent_id}) = (%s, %s)'

    query = SQL(sql).format(table=Identifier(join_table),
                            self_id=Identifier(self_key),
                            parent_id=Identifier(parent_key))

    cur = conn.cursor(cursor_factory=NamedTupleCursor)

    if verbose is True:
        print(query.as_string(conn))
        print(cur.mogrify(query, (child_id, parent_id)))
        t_log.new_event('Disassociating Tables: ' + join_table)

    try:
        cur.execute(query, (child_id, parent_id))
    except OperationalError as error:
        print(error)

    conn.commit()

    data_df = \
        generic_pull_grouped_data(table_name=table_name, parent_table_name=parent_table_name,
                                  my_conn=my_conn, t_log=t_log, verbose=verbose)

    if verbose is True:
        t_log.new_event('Finished disassociating: ' + join_table)

    return data_df


def generic_last_equation_number(table_data: DataFrame) -> int:
    """Record Count using dataframe"""
    if len(table_data.index) == 0:
        rcount = 1  # Starts at 1, because Genesis & Revelation are Equation  and Variable 1, respectively
    else:
        numbers: Series = table_data.loc[slice(None), 'name'].str.extract(r'^[a-zA-Z]+\s([0-9]+)$')
        rcount_s: Series = numbers.fillna(0).astype(int).max()
        rcount = int(rcount_s.iloc[0])
    return rcount


def generic_new_record_db(parent_id: int = None, table_name: str = None, parent_table_name: str = None,
                          data_df: Optional[DataFrame] = None, name: str = None, new_record=None,
                          latex: LatexData = None, notes: str = None,
                          dimensions: int = 1, insertion_order: int = None, created_by: str = None,
                          unit_id: int = 1, verbose: bool = None,
                          my_conn: Optional[dict] = None, t_log: Optional[TimeLogger] = None
                          ) -> DataFrame:
    """Insert New Record Into math_object"""

    if verbose is True and t_log is None:
        t_log = TimeLogger()

    if new_record is None:
        new_record = {}

    my_conn = my_connect(my_conn=my_conn, t_log=t_log, verbose=verbose)
    conn = my_conn['conn']
    db_params = my_conn['db_params']

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
            updated_df = generic_associate_parent(my_conn=my_conn, t_log=t_log,
                                                  parent_id=parent_id, child_id=getattr(record, table_id),
                                                  insertion_order=insertion_order,
                                                  table_name=table_name, parent_table_name=parent_table_name,
                                                  inserted_by=created_by, verbose=verbose
                                                  )
    else:
        updated_df = \
            generic_pull_grouped_data(table_name=table_name, parent_table_name=parent_table_name,
                                      my_conn=my_conn, t_log=t_log, verbose=verbose)

    return updated_df


def add_field(key: str = None, value=None):
    """Convenience Wrapper to Beautify If value is none"""
    data = {}
    if value is not None:
        data = {key: value}
    return data


class GroupedPhysicsObject:
    """Base class for Equations, Variables, and Units"""
    def __init__(self, table_name: str, parent_table_name: str,
                 my_conn: Optional[dict] = None, t_log: Optional[TimeLogger] = None,
                 verbose: bool = False,):
        """Constructor for MathObject"""
        self.table_name = table_name
        self.parent_table_name = parent_table_name  # For equations it is eqn_group. For variables it is equations
        self.grouped_data: Optional[DataFrame] = None
        self.all_records: Optional[DataFrame] = None
        self.selected_parent_id: Optional[int] = None
        self.selected_data_records: Optional[Records] = None
        self.records_not_selected_unique: Optional[Records] = None
        self.my_conn = my_connect(my_conn=my_conn, t_log=t_log, verbose=verbose)
        self.pull_grouped_data(my_conn=my_conn, t_log=t_log, verbose=verbose)

    def id_name(self):
        """Convenience method to return id_name"""
        return self.table_name + '_id'

    def parent_table_id_name(self):
        """Convenenience method to return parent_table_id_name"""
        return self.parent_table_name + '_id'

    def pull_grouped_data(self, my_conn: Optional[dict] = None, t_log: Optional[TimeLogger] = None,
                          verbose: bool = False):
        """Extract grouped data from database"""

        if my_conn is None:
            my_conn = self.my_conn
        else:
            self.my_conn = my_conn

        self.grouped_data = \
            generic_pull_grouped_data(table_name=self.table_name, parent_table_name=self.parent_table_name,
                                      my_conn=my_conn, t_log=t_log, verbose=verbose)
        self._set_all_records()

    def associate_parent(self, parent_id: int = None, child_id: int = None, new_record: dict = None,
                         insertion_order: int = None, inserted_by: str = None,
                         my_conn: Optional[dict] = None, t_log: Optional[TimeLogger] = None, verbose: bool = False):
        """Associate a record with a group"""
        table_name = self.table_name
        parent_table_name = self.parent_table_name

        if my_conn is None:
            my_conn = self.my_conn
        else:
            self.my_conn = my_conn

        self.grouped_data = \
            generic_associate_parent(parent_id=parent_id, child_id=child_id, new_record=new_record,
                                     table_name=table_name, parent_table_name=parent_table_name,
                                     insertion_order=insertion_order, inserted_by=inserted_by,
                                     my_conn=my_conn, t_log=t_log, verbose=verbose)

        if self.selected_parent_id is not None:
            self.set_records_for_parent(parent_id=int(self.selected_parent_id))

    def disassociate_parent(self, parent_id: int = None, child_id: int = None,
                            my_conn: Optional[dict] = None, t_log: Optional[TimeLogger] = None,
                            verbose: bool = False):
        """Associate a record with a group"""
        table_name = self.table_name
        parent_table_name = self.parent_table_name

        if my_conn is None:
            my_conn = self.my_conn
        else:
            self.my_conn = my_conn

        self.grouped_data = \
            generic_disassociate_parent(parent_id=parent_id, child_id=child_id,
                                        table_name=table_name, parent_table_name=parent_table_name,
                                        my_conn=my_conn, t_log=t_log, verbose=verbose)

        if self.selected_parent_id is not None:
            self.set_records_for_parent(parent_id=int(self.selected_parent_id))

    def new_record(self, parent_id: int = None, name: str = None, latex: LatexData = None,
                   new_record: dict = None, notes: str = None, dimensions: int = 1,
                   insertion_order: int = None, created_by: str = None,
                   my_conn: Optional[dict] = None, t_log: Optional[TimeLogger] = None,
                   unit_id: int = 1, verbose: bool = None):
        """Insert a new_record Into """
        table_name = self.table_name
        parent_table_name = self.parent_table_name

        if my_conn is None:
            my_conn = self.my_conn
        else:
            self.my_conn = my_conn

        self.grouped_data = \
            generic_new_record_db(
                parent_id=parent_id, table_name=table_name, parent_table_name=parent_table_name,
                name=name, latex=latex, notes=notes, new_record=new_record,
                data_df=self.grouped_data, dimensions=dimensions, unit_id=unit_id,
                insertion_order=insertion_order, created_by=created_by,
                my_conn=my_conn, t_log=t_log, verbose=verbose
            )

    def _set_all_records(self):
        self.all_records = self.grouped_data.drop_duplicates('name').droplevel(self.parent_table_id_name()).sort_index()

    def update(self, an_id: id = None, where_key: str = None, name: str = None,
               data=None, latex: LatexData = None, notes: str = None, unit_id: int = None,
               dimensions: int = None, modified_by: str = None, created_by: str = None,
               my_conn: Optional[dict] = None, t_log: Optional[TimeLogger] = None, verbose: bool = None):
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
            else:
                self.my_conn = my_conn

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

                self.pull_grouped_data(verbose=verbose)

    def selected_data_df(self, parent_id: int = None) -> DataFrame:
        """Retern selected data in DataFrame form"""
        if parent_id is None:
            parent_id = self.selected_parent_id
        else:
            self.selected_parent_id = int(parent_id)

        if parent_id is None:
            warn('No Parent ID set', NoRecordIDError)

        try:
            df = self.grouped_data.loc[parent_id, :]
        except KeyError:
            df: Optional[DataFrame] = None
        return df

    def set_records_for_parent(self, parent_id: int = None):
        """Sets records for parents after an update"""
        if parent_id is None:
            parent_id = self.selected_parent_id
        else:
            self.selected_parent_id = int(parent_id)

        if parent_id is None:
            warn('No Parent ID set', NoRecordIDError)

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

    def other_parents(self, child_id: int = None, my_conn: Optional[dict] = None,
                      t_log: Optional[TimeLogger] = None, verbose: bool = None):
        """Pulls list of other parents"""
        gd = self.grouped_data
        gd_inds = gd.index.dropna()
        if len(gd_inds) > 0:
            parent_df = gd.loc[(slice(None), child_id), :].droplevel(self.id_name())
            pids = tuple(parent_df.index.to_list())

            if verbose is True and t_log is None:
                t_log = TimeLogger()

            if my_conn is None:
                my_conn = self.my_conn
            else:
                self.my_conn = my_conn

            my_conn = my_connect(my_conn=my_conn, t_log=t_log, verbose=verbose)
            conn = my_conn['conn']

            sql = "SELECT * FROM {parent_table} WHERE {parent_id} IN %s;"

            query = SQL(sql).format(
                parent_table=Identifier(self.parent_table_name),
                parent_id=Identifier(self.parent_table_id_name())
            )

            if verbose is True:
                t_log.new_event('Loading Database: ' + self.parent_table_name)

            cur = conn.cursor(cursor_factory=NamedTupleCursor)

            cur.execute(query, (pids, ))
            records = cur.fetchall()
            if verbose is True:
                t_log.new_event('Database Loaded: ' + self.parent_table_name)
        else:
            if verbose is True:
                t_log.new_event('No Other Parents')
            records = []

        return records

    def latest_record(self):
        """Returns latest record"""
        return list(self.grouped_data.sort_values('created_at').tail(1).itertuples())

    def update_insertion_order_for_selected(self, order: dict, my_conn: Optional[dict] = None,
                                            t_log: Optional[TimeLogger] = None, verbose: bool = False):
        """Populates insertion_order attribute"""
        self.pull_grouped_data()
        df = self.selected_data_df()

        join_table: str = self.table_name + '_' + self.parent_table_name

        if verbose is True and t_log is None:
            t_log = TimeLogger()

        if my_conn is None:
            my_conn = self.my_conn
        else:
            self.my_conn = my_conn

        my_conn = my_connect(my_conn=my_conn, t_log=t_log, verbose=verbose)
        self.my_conn = my_conn
        conn = my_conn['conn']

        sql = 'UPDATE {table} SET insertion_order = %s WHERE ({c_table_id}, {p_table_id}) = (%s, %s)'

        query = SQL(sql).format(table=Identifier(join_table),
                                c_table_id=Identifier(self.id_name()),
                                p_table_id=Identifier(self.parent_table_id_name())
                                )

        cur = conn.cursor(cursor_factory=NamedTupleCursor)

        if verbose is True:
            t_log.new_event('Updating Insertion order for: ' + join_table)
            print(query.as_string(conn))

        for eq_name, i in order.items():
            p_id = self.selected_parent_id
            c_id = int(df.name[df.name == eq_name].index[0])

            if verbose:
                print(cur.mogrify(query, (i, c_id, p_id)))
            try:
                cur.execute(query, (i, c_id, p_id))
            except OperationalError as error:
                print(error)

        conn.commit()

        self.pull_grouped_data()

        if verbose is True:
            t_log.new_event('Finished Updating Insertion Order: ' + join_table)

    # def __repr__(self):
    #     return self.grouped_data.__repr__()
    #
    # def __str__(self):
    #     return self.grouped_data.__str__()
