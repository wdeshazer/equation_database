"""
Variable Provides helper functions for managing variables and their associations
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

from grouped_physics_object import GroupedPhysicsObject, add_field


class Variable(GroupedPhysicsObject):
    """Class for Managing Variable Table in Postgres database"""

    def __init__(self, table_name='variable', parent_table_name='equation'):
        """Constructor for Equation"""
        super().__init__(table_name=table_name, parent_table_name=parent_table_name)

    # pylint: disable=arguments-differ
    def new_record(self, *args, unit_id: int = 1, type_name: str = 'Constant', dimensions: int = 1, **kwargs):
        """Insert new Variable Record"""
        new_record = {'type_name': type_name}
        super().new_record(*args, new_record=new_record, **kwargs)

    def update(self, *args, type_name: str = None, **kwargs):
        data = {}
        data.update(add_field('type_name', type_name))
        super().update(*args, data=data, **kwargs)
