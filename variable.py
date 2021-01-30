"""
Varible Provides helper functions for pulling the LaTeX template from the equations database
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

from math_object import MathObject


class Variable(MathObject):
    """Class for Managing Variable Table in Postgres database"""

    def __init__(self, table='variable', parent_table='equation'):
        """Constructor for Equation"""
        super().__init__(table=table, parent_table=parent_table)

    # pylint: disable=arguments-differ
    def insert(self, *args, unit_id: int = 1, var_type: str = 'Constant', dimensions: int = 1, **kwargs):
        """Insert new Variable Record"""
        data = {'unit_id': unit_id, 'variable_type': var_type, 'dimensions': dimensions}
        super().insert(*args, data=data, **kwargs)
