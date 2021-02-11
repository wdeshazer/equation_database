"""
Equation Provides helper functions for managing Equation and their associations
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

from grouped_physics_object import GroupedPhysicsObject, add_field


class Equation(GroupedPhysicsObject):
    """Equation class provides helper functions for inserting equations into the database"""

    def __init__(self, table_name='equation', parent_table_name='eqn_group'):
        """Constructor for Equation"""
        super().__init__(table_name=table_name, parent_table_name=parent_table_name)

    # pylint: disable=arguments-differ
    def new_record(self, *args, type_name='Undesignated', **kwargs):
        """Insert new Equation"""
        new_record = {'type_name': type_name}
        super().new_record(*args, new_record=new_record, **kwargs)

    def update(self, *args, type_name: str = None, **kwargs):
        """Update Equation"""
        data = {}
        data.update(add_field('type_name', type_name))
        super().update(*args, data=data, **kwargs)

    def associate_parent(self, parent_id: int = None, child_id: int = None,
                         insertion_order: int = None, inserted_by: str = None,
                         code_file_path: str = None,  new_record: dict = None, verbose: bool = False):

        # noinspection PyTypeChecker
        new_record: dict = None

        if code_file_path is not None:
            new_record = dict(code_file_path=code_file_path)

        super().associate_parent(parent_id=parent_id, child_id=child_id,
                                 insertion_order=insertion_order, inserted_by=inserted_by,
                                 new_record=new_record, verbose=verbose)
