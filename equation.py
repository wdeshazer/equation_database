from math_object import MathObject


class Equation(MathObject):
    """"""

    def __init__(self, table='equation', parent_table='eqn_group'):
        """Constructor for Equation"""
        super(Equation, self).__init__(table=table, parent_table=parent_table)

    def insert(self, unit_id: int = 1, eq_type='Equality', *args, **kwargs):
        data = {'unit_id': unit_id, 'equation_type': eq_type}
        super(Equation, self).insert(data=data, *args, **kwargs)
