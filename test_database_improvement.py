from equation_database import TimeLogger
from equation import Equation
from equation_group import EquationGroup
from variable import Variable
from math import isnan
from warnings import warn
from typing import NewType, List, NamedTuple, Optional
from time import time
from pandas import DataFrame, Series, read_sql
from psycopg2.sql import SQL, Identifier, Placeholder, Composed
from psycopg2 import connect, OperationalError
from psycopg2.extras import NamedTupleCursor
from latex_data import LatexData
from config import config

t_log = TimeLogger()


sql = 'SELECT * FROM {join_table} RIGHT JOIN {table} USING({table_id})'

query1 = SQL(sql).format(
    table=Identifier('equation'),
    join_table=Identifier('equation_eqn_group'),
    table_id=Identifier('equation_id')
)

query2 = SQL(sql).format(
    table=Identifier('variable'),
    join_table=Identifier('variable_equation'),
    table_id=Identifier('variable_id')
)

db_params = config()
conn = connect(**db_params)


t_log.new_event("Equation Load Start")
eqn_df = read_sql(query1, con=conn, index_col=['eqn_group_id', 'equation_id'])
# This was a good example of loading objects to file
# data_df['latex'] = data_df['latex'].apply(loads)

eqn_df['latex_obj'] = None

for row in eqn_df.itertuples():
    eqn_df.loc[row.Index, 'latex_obj'] = \
        LatexData(latex=row.latex, template_id=row.template_id,
                  image=row.image, compiled_at=row.compiled_at)

eqn_df.sort_values(['eqn_group_id', 'insertion_order'], inplace=True)
t_log.new_event("Equation Load Complete")

t_log.new_event("Variable Load Start")
var_df = read_sql(query2, con=conn, index_col=['equation_id', 'variable_id'])

var_df['latex_obj'] = None

for row in var_df.itertuples():
    var_df.loc[row.Index, 'latex_obj'] = \
        LatexData(latex=row.latex, template_id=row.template_id,
                  image=row.image, compiled_at=row.compiled_at)

var_df.sort_values(['variable_id', 'insertion_order'], inplace=True)
t_log.new_event("Variable Load Complete")

# t_log.new_event("Unit Load")
# self.unit = Unit()
# new_event("Equation Type Load")
# eq_type = TypeTable(name='equation_type')
# t_log.new_event("Variable Type Load")
# var_type = TypeTable(name='variable_type')
# new_event("Unit Type Load")
# unit_type = TypeTable(name='unit_type')
