"""
Unit Provides helper functions for managing Unit and their associations
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

from math_object import MathObject


class Unit(MathObject):
    """Unit class provides helper functions for inserting Units into the database"""

    def __init__(self, table_name='unit', parent_table_name=None):
        """Constructor for Unit. Relations are one to many"""
        super().__init__(table=table_name, parent_table=parent_table_name)

    def associate_parent(self, parent_id: int = None, child_id: int = None,
                         insertion_order: int = None, inserted_by: str = None,
                         data: dict = None, verbose: bool = False):
        """There is no parent association"""
