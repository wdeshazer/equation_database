from math_object import MathObject


class Variable(MathObject):
    """"""

    def __init__(self, table='variable', parent_table='equation'):
        """Constructor for Equation"""
        super(Variable, self).__init__(table=table, parent_table=parent_table)

    def insert(self, unit_id: int = 1, var_type: str = 'Constant', dimensions: int = 1, *args, **kwargs):
        data = {'unit_id': unit_id, 'variable_type': var_type, 'dimensions': dimensions}
        super(Variable, self).insert(data=data, *args, **kwargs)
