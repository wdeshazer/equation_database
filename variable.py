"""
Variable Provides helper functions for managing variables and their associations
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

from collections import namedtuple
from typing import Optional
from grouped_physics_object import GroupedPhysicsObject, add_field
from latex_data import LatexData

VariableRecord = namedtuple('VariableRecord', ['insertion_order', 'insertion_order_prev', 'insertion_date',
                                               'inserted_by', 'name', 'latex', 'notes', 'image', 'template_id',
                                               'image_is_dirty', 'created_at', 'created_by', 'modified_at',
                                               'modified_by', 'compiled_at', 'dimensions', 'unit_id', 'type_name',
                                               'latex_obj'])


class Variable(GroupedPhysicsObject):
    """Class for Managing Variable Table in Postgres database"""

    def __init__(self, *args, table_name='variable', parent_table_name='equation', verbose: bool = False, **kwargs):
        """Constructor for Equation"""
        super().__init__(*args, table_name=table_name, parent_table_name=parent_table_name, verbose=verbose, **kwargs)

        if len(self.grouped_data.index) == 0:
            # https://en.wikipedia.org/wiki/Proof_that_22/7_exceeds_%CF%80
            ltx = LatexData(latex=r'\Sigma \Nu')
            self.new_record(name='Revelation',
                            latex=ltx,
                            notes='A new heaven', dimensions=1, created_by='razor', my_conn=self.my_conn
                            )

    # pylint: disable=arguments-differ
    def new_record(self, *args, latex: Optional[LatexData] = None, unit_id: int = 1, type_name: str = 'Constant',
                   dimensions: int = 1, **kwargs):
        """Insert new Variable Record"""
        new_record = {'type_name': type_name}
        if latex is None:
            latex = self.grouped_data.iloc[0].latex_obj
        super().new_record(*args, new_record=new_record, latex=latex, **kwargs)

    def update(self, *args, type_name: str = None, **kwargs):
        data = {}
        data.update(add_field('type_name', type_name))
        super().update(*args, data=data, **kwargs)
