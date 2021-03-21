"""
math_object Provides helper functions for pulling the LaTeX show_template_manager from the equations database

update method: https://stackoverflow.com/questions/34774409/build-a-dynamic-update-query-in-psycopg2
https://www.psycopg.org/docs/sql.html#
Type Hinting Tuple: https://stackoverflow.com/questions/47533787/typehinting-tuples-in-python
Update borrowed from: https://stackoverflow.com/questions/34774409/build-a-dynamic-update-query-in-psycopg2
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

from typing import Tuple
from collections import defaultdict
from warnings import warn
from psycopg2.sql import SQL, Identifier, Placeholder, Composed
from psycopg2 import connect, OperationalError, Binary
from psycopg2.extras import NamedTupleCursor
from latex_template import compile_pattern, template
from config import config


class RecordIDTypeError(UserWarning):
    """UserWarning for EquationGroup"""


class ImageWithoutTemplateIDError(UserWarning):
    """UserWarning for EquationGroup"""


class NoRecordIDError(UserWarning):
    """UserWarning for EquationGroup"""


class MathObject:
    """Base class for Equations, Variables, and Units"""
    def __init__(self, table: str, parent_table: str, verbose: bool = True):
        """Constructor for MathObject"""
        self.table = table
        self.parent_table = parent_table  # For equations it is eqn_group. For variables it is equations
        self.records: dict = self.all_records(verbose=verbose)
        self.last_inserted = None
        self.id_name = self.table + "_id"
        self.records_for_parent = None

    def all_records(self, as_columns: bool = True, verbose: bool = False):
        """Returns all records for math_object"""
        # sql = 'SELECT * FROM {aTable}'.format(aTable=self.table)
        sql = "SELECT * FROM {tbl}"
        query = SQL(sql).format(tbl=Identifier(self.table))

        db_params = config()
        conn = connect(**db_params)

        cur = conn.cursor(cursor_factory=NamedTupleCursor)

        if verbose:
            print('Extracting records from Table: {aTable}'.format(aTable=self.table))

        try:
            cur.execute(query)
        except OperationalError as error:
            print(error)

        records = cur.fetchall()

        cur.close()
        conn.close()

        if as_columns is True:
            records = self.as_columns(records)

        return records

    def insert(self, parent_id: int = None, name: str = None,
               data=None, latex: str = None, notes: str = None,
               image: bytes = None, template_id: int = None, dimensions: int = 1,
               insertion_order: int = None, created_by: str = None, unit_id: int = 1,
               verbose: bool = None):
        """Insert New Record Into math_object"""

        if data is None:
            data = {}

        db_params = config()

        next_id: int = self.record_count_total(verbose=verbose) + 1

        if name is None:
            name = "{aTable} {ID:d}".format(ID=next_id, aTable=self.table)
        if created_by is None:
            created_by = db_params['user']

        if latex is None:
            latex = 'a^2 + b^2 = c^2'

        the_template = template(version=template_id, verbose=verbose)
        a_template = the_template.data
        template_id = the_template.id

        if image is None:
            # If a_template is None the most recent show_template_manager is used
            image = Binary(compile_pattern(pattern=latex, aTemplate=a_template, verbose=verbose))

        data.update({
            'name': name,
            'latex': latex,
            'image': image,
            'notes': notes,
            'dimensions': dimensions,
            'unit_id': unit_id,
            'template_id': template_id,
            'created_by': created_by
        })

        sql = 'INSERT INTO {table} ({fields}) VALUES ({values}) RETURNING *'

        keys = data.keys()

        query = SQL(sql).format(table=Identifier(self.table),
                                fields=SQL(', ').join(map(Identifier, keys)),
                                values=SQL(', ').join(map(Placeholder, keys)))

        conn = connect(**db_params)

        if verbose:
            print(query.as_string(conn))

        cur = conn.cursor(cursor_factory=NamedTupleCursor)

        if verbose:
            print('Adding new record to Table: {aTable}'.format(aTable=self.table))

        try:
            cur.execute(query, data)
        except OperationalError as error:
            print(error)

        new_records = cur.fetchall()

        conn.commit()

        cur.close()
        conn.close()

        if parent_id is not None:
            for record in new_records:
                self.associate_parent(parent_id=parent_id, child_id=record.id, insertion_order=insertion_order)

        self.last_inserted = self.as_columns(new_records)

        self.append(new_records)

    def update(self, an_id: id = None, where_key: str = None, name: str = None,
               data=None, latex: str = None, notes: str = None, unit_id: int = None,
               image: bytes = None, template_id: int = None, dimensions: int = None,
               modified_by: str = None, created_by: str = None,
               verbose: bool = None):
        """Insert New Record Into math_object"""

        if where_key is None:
            where_key = self.id_name

        if an_id is None:
            warn("No Record ID Specified", NoRecordIDError)
        else:
            if data is None:
                data = {}

            db_params = config()

            data.update(self._add_field('name', name))
            data.update(self._add_field('notes', notes))
            data.update(self._process_latex(latex, image, template_id, verbose))
            data.update(self._add_field('dimensions', dimensions))
            data.update(self._add_field('unit_id', unit_id))
            data.update(self._add_field('created_by', created_by))

            # If there is no data, then skip. Of course one could still change modified by:
            if len(data) > 0 or modified_by is not None:

                # Always require a modified by and because one can change data without specifying a modifer,
                # this is necessary. We don't check it before the previous if, because we don't want to create
                # a modified_by if not data was set and no modified_by was set.
                if modified_by is None:
                    modified_by = db_params['user']

                data.update(modified_by=modified_by)

                fields = data.keys()

                sql = "UPDATE {table} SET {fields} WHERE {pkey} = {a_value} RETURNING *"

                query = SQL(sql).format(table=Identifier(self.table),
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

                self.last_inserted = self.as_columns(new_record)

                self.records = self.all_records()

    @staticmethod
    def _process_latex(latex, image, template_id, verbose: bool = False):
        """Helper function to process latex, image and template_id flags"""
        data = {}

        if latex is not None or image is not None or template_id is not None:

            only_template_changed = template_id is not None and latex is None and image is None
            only_latex_changed = latex is not None and image is None  # regardless of template_id state
            # always need template_id when image is manually changed
            acceptable_image_change = image is not None and template_id is not None

            recompile = only_latex_changed or only_template_changed
            if recompile:
                the_template = template(version=template_id, verbose=verbose)
                a_template = the_template.data
                template_id = the_template.id
                image = Binary(compile_pattern(pattern=latex, aTemplate=a_template, verbose=verbose))

                data.update(image=image, template_id=template_id)
                if only_latex_changed:
                    data.update(latex=latex)
            elif acceptable_image_change:
                # Note if template_id is not specified
                data.update(image=image, template_id=template_id)
                if latex is not None:
                    data.update(latex=latex)
            else:
                warn('User Input Images must also specify show_template_manager used', ImageWithoutTemplateIDError)
        return data

    @staticmethod
    def _add_field(key: str = None, value=None):
        data = {}
        if value is not None:
            data = {key: value}
        return data

    def append(self, new_records):
        """Append new records to existing records. Because the data is stored as a dictionary instead of
        NamedTuples, it requires a helper function to append new data"""
        res = self.records

        for data in new_records:
            # noinspection PyProtectedMember
            record: dict = data._asdict()
            for key, value in record.items():
                res[key].append(value)

        self.records = res

    # Simple return statement. More sophisticated ones will have to be purpose built
    def values_for_fields(self, where_key: str = None, where_values: Tuple[int, ...] = None,
                          name: bool = True, as_column: bool = True, verbose: bool = False, **kwargs):
        """where_key could be 'id', 'name', etc.
            For any other field, you just set the fieldname to True"""

        if where_key is None:
            where_key = self.id_name
        fields = [self.id_name]

        if name is True:
            fields.append('name')
        for a_key in kwargs:
            if kwargs[a_key] is True:
                fields.append(a_key)

        db_params = config()
        conn = connect(**db_params)

        if where_values is None:
            sql = "SELECT {fields} FROM {table}"
            query = SQL(sql).format(table=Identifier(self.table),
                                    fields=SQL(', ').join(map(Identifier, fields)))
            if verbose:
                print(query.as_string(conn))
        else:
            sql = "SELECT {fields} from {table} where {pkey} IN %s"
            query = SQL(sql).format(table=Identifier(self.table),
                                    fields=SQL(', ').join(map(Identifier, fields)),
                                    pkey=Identifier(where_key)
                                    )
            if verbose:
                print(query.as_string(conn))

        cur = conn.cursor(cursor_factory=NamedTupleCursor)

        if verbose:
            print('Extracting records from Table: {aTable}'.format(aTable=self.table))

        try:
            cur.execute(query, where_values)
        except OperationalError as error:
            print(error)

        records = cur.fetchall()

        cur.close()
        conn.close()

        if as_column is True:
            records = self.as_columns(records)

        return records

    def record_count_total(self, verbose: bool = False) -> int:
        """Get the total record count for {table}""".format(table=self.table)
        sql = "SELECT COUNT(*) from {table}"

        query = SQL(sql).format(table=Identifier(self.table))

        db_params = config()
        conn = connect(**db_params)

        cur = conn.cursor(cursor_factory=NamedTupleCursor)

        if verbose:
            print('Getting Count of Records in table: {table}'.format(table=self.table))

        cur.execute(query)  # self.table))

        record_count = cur.fetchone()

        cur.close()
        conn.close()

        return record_count[0]

    def record_count_for_parent(self, parent_id: Tuple[int, ...] = None,
                                verbose: bool = False):
        """Return record count for Parent Table"""
        sql = ''

        if isinstance(parent_id, tuple):
            sql = "SELECT COUNT(*) from {table} WHERE {parent_key} IN %s"
        elif isinstance(parent_id, int):
            sql = "SELECT COUNT(*) from {table} WHERE {parent_key}= %s"
        else:
            warn("Unrecognized type for parent_id", RecordIDTypeError)

        query = SQL(sql).format(table=Identifier(self.join_table()),
                                parent_key=Identifier(self.parent_key())
                                )

        db_params = config()
        conn = connect(**db_params)

        cur = conn.cursor(cursor_factory=NamedTupleCursor)

        if verbose:
            print('Getting Count of Records in table: {table} for Group ID: {gid}'.format(table=self.join_table(),
                                                                                          gid=parent_id))
            print(query.as_string(conn))
            if isinstance(parent_id, int):
                cur.mogrify(query, parent_id)
            elif isinstance(parent_id, tuple):
                cur.mogrify(query, (parent_id, ))

        try:
            cur.execute(query, (parent_id,))
        except TypeError:
            cur.execute(query, parent_id)  # self.table))
        except OperationalError as error:
            print(error)

        record_count = cur.fetchone()

        cur.close()
        conn.close()

        return record_count[0]

    def associate_parent(self, parent_id: int = None, child_id: int = None,
                         insertion_order: int = None, inserted_by: str = None,
                         data: dict = None, verbose: bool = False):
        """Associate the parent and child tables using parent id. Insertion_order and inserted_by are optional"""
        parent_key = self.parent_table + '_id'
        self_key = self.table + '_id'

        join_table = self.table + '_' + self.parent_table

        db_params = config()

        if data is None:
            data = {}

        if inserted_by is None:
            inserted_by = db_params['user']

        data.update(
            {parent_key: parent_id, self_key: child_id},
            insertion_order=insertion_order,
            inserted_by=inserted_by
        )

        sql = 'INSERT INTO {table} ({fields}) VALUES ({values})'

        keys = data.keys()

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
            cur.execute(query, data)
        except OperationalError as error:
            print(error)

        conn.commit()

        cur.close()
        conn.close()

    def get_records_for_parent(self, parent_id: Tuple[int, ...] = None, as_columns: bool = True,
                               verbose: bool = False):
        """Get the {table} records for {parent}""".format(table=self.table, parent=self.parent_table)
        db_params = config()

        sql = "SELECT * FROM {child_table} c INNER JOIN {join_table} j " \
              " USING({id_name}) WHERE j.{parent_id_name} = %s ORDER BY insertion_order;"

        query = SQL(sql).format(
            child_table=Identifier(self.table),
            join_table=Identifier(self.join_table()),
            id_name=Identifier(self.id_name),
            parent_id_name=Identifier(self.parent_key())
        )

        conn = connect(**db_params)

        cur = conn.cursor(cursor_factory=NamedTupleCursor)

        if verbose:
            print(query.as_string(conn))
            if isinstance(parent_id, int):
                cur.mogrify(query, parent_id)
            elif isinstance(parent_id, tuple):
                cur.mogrify(query, (parent_id, ))

        try:
            cur.execute(query, (parent_id, ))
        except TypeError:
            cur.execute(query, parent_id)
        except OperationalError as error:
            print(error)

        records = cur.fetchall()

        cur.close()
        conn.close()

        if as_columns is True:
            records = self.as_columns(records)

        return records

    def records_not_in_parent(self, parent_id: Tuple[int, ...], as_columns: bool = True, verbose: bool = False):
        """Get the {table} records for {parent}""".format(table=self.table, parent=self.parent_table)
        db_params = config()
        sql = ''

        sql = "SELECT * FROM {child_table} WHERE {id_name} NOT IN" \
              " (SELECT {id_name} FROM {join_table} WHERE {parent_id_name} = %s);"

        # self_dict = dict(table='equation', join_table= lambda: 'equation_eqn_group',
        #                  id_name='equation_id', parent_key = lambda : 'eqn_group_id')
        # MyTuple = namedtuple('MyTuple', self_dict)
        # self = MyTuple(**self_dict)

        query = SQL(sql).format(
            child_table=Identifier(self.table),
            join_table=Identifier(self.join_table()),
            id_name=Identifier(self.id_name),
            parent_id_name=Identifier(self.parent_key())
        )

        conn = connect(**db_params)

        cur = conn.cursor(cursor_factory=NamedTupleCursor)

        if verbose:
            print(query.as_string(conn))
            if isinstance(parent_id, int):
                cur.mogrify(query, (parent_id, ))
            elif isinstance(parent_id, tuple):
                cur.mogrify(query, parent_id)

        try:
            cur.execute(query, (parent_id, ))
        except TypeError:
            cur.execute(query, parent_id)
        except OperationalError as error:
            print(error)

        records = cur.fetchall()

        if as_columns is True:
            records = self.as_columns(records)

        cur.close()
        conn.close()
        return records

    def parent_key(self):
        """Parent ID String to be used as a Key in the table"""
        return self.parent_table + '_id'

    def self_key(self):
        """Self ID String to be used as a Key in the table"""
        return self.table + '_id'

    def join_table(self):
        """Join table which is a concatenation of the table and the parent table"""
        return self.table + '_' + self.parent_table

    # NamedTuple uses underscores to prevent name collision _make, _replace, _asdict, _fields
    # noinspection PyProtectedMember
    @staticmethod
    def as_columns(records):
        """Helper function to turn NameTuple records into column-like dictionaries"""
        res = defaultdict(list)

        for data in records:
            record = data._asdict()
            for key, value in record.items():
                res[key].append(value)
        return res
