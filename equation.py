"""
Equation Provides helper functions for managing Equation and their associations
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

from math_object import MathObject


class Equation(MathObject):
    """Equation class provides helper functions for inserting equations into the database"""

    def __init__(self, table='equation', parent_table='eqn_group'):
        """Constructor for Equation"""
        super().__init__(table=table, parent_table=parent_table)

    # pylint: disable=arguments-differ
    def insert(self, *args, eq_type='Equality', **kwargs):
        """Insert new Equation"""
        data = {'equation_type': eq_type}
        super().insert(*args, data=data, **kwargs)

    def update(self, *args, eq_type: str = None, **kwargs):
        """Update Equation"""
        data = {}
        data.update(super()._add_field('eq_type', eq_type))
        super().update(*args, data=data, **kwargs)

    def associate_parent(self, parent_id: int = None, child_id: int = None,
                         insertion_order: int = None, inserted_by: str = None,
                         code_file_path: str = None,  data: dict = None, verbose: bool = False):

        if code_file_path is not None:
            data = dict(code_file_path=code_file_path)

        super().associate_parent(parent_id=parent_id, child_id=child_id,
                                 insertion_order=insertion_order, inserted_by=inserted_by,
                                 data=data, verbose=verbose)
