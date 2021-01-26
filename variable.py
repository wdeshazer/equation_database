from math_object import MathObject
from config import config
import psycopg2
from psycopg2.extras import NamedTupleCursor
from latex_template import compile_pattern


class Variable(MathObject):
    """"""

    def __init__(self, table='variable', join_table='equation_variable'):
        """Constructor for Equation"""
        super(Variable, self).__init__(table=table, join_table=join_table)

    def vivify_record(self, verbose: bool = False, lpattern: str = 'm^3', unit_id = 1):

        data = {'latex': lpattern, 'unit_id': unit_id}

        records = super(Variable, self).vivify_record(verbose=verbose, data=data)

        return records

