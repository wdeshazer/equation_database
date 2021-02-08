"""
Unit Provides helper functions for managing Unit and their associations
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

from grouped_physics_object import GroupedPhysicsObject


class Unit(GroupedPhysicsObject):
    """Unit class provides helper functions for inserting Units into the database"""

    def __init__(self, table_name='unit', parent_table_name=None):
        """Constructor for Unit. Relations are one to many"""
        super().__init__(table_name=table_name, parent_table_name=parent_table_name)

    def associate_parent(self, parent_id: int = None, child_id: int = None, new_record: dict = None,
                         insertion_order: int = None, inserted_by: str = None, verbose: bool = False):
        """This has no function Unit is one to many"""
