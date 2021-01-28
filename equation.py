from math_object import MathObject
# from config import config
# import psycopg2
# from psycopg2.extras import NamedTupleCursor
# from latex_template import compile_pattern


class Equation(MathObject):
    """"""

    def __init__(self, table='equation', join_table='equation_eqn_group'):
        """Constructor for Equation"""
        super(Equation, self).__init__(table=table)

    def insert(self, unit_id: int = 1, eq_type='Equality', *args, **kwargs):
        data = {'unit_id': unit_id, 'equation_type': eq_type}
        super(Equation, self).insert(data=data, *args, **kwargs)
