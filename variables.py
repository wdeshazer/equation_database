"""
Variable Provides helper functions for managing variables and their associations
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

from collections import namedtuple
from typing import Optional, List
from grouped_physics_object import GroupedPhysicsObject, add_field
from physics_objects import PhysicsObjects, PhysicsObject
from latex_data import LatexData

GroupedVariableRecord = \
    namedtuple('VariableRecord',
               ['insertion_order', 'insertion_order_prev', 'insertion_date',
                'inserted_by', 'name', 'latex', 'notes', 'image', 'template_id',
                'image_is_dirty', 'created_at', 'created_by', 'modified_at',
                'modified_by', 'compiled_at', 'dimensions', 'unit_id', 'type_name',
                'latex_obj'])

NewVariableRecordInput = \
    namedtuple('VariableRecordInput',
               ['name', 'latex_obj', 'notes', 'created_by', 'dimensions', 'unit_id', 'type_name'])

ExistingVariableRecordInput = \
    namedtuple('ExistingVariableRecordInput',
               ['variable_id', 'name', 'latex_obj', 'modified_by', 'dimensions', 'unit_id', 'type_name'])


class VariableRecord(PhysicsObject):
    """Creates a unique Signature for an Variable Record"""


VariableRecords = List[VariableRecord]


class GroupedVariables(GroupedPhysicsObject):
    """Class for Managing Variable Table in Postgres database"""

    def __init__(self, *args, table_name='variable', parent_table_name='equation', verbose: bool = False, **kwargs):
        """Constructor for Equation"""
        super().__init__(*args, table_name=table_name, parent_table_name=parent_table_name, verbose=verbose, **kwargs)

        if len(self.grouped_data.index) == 0:
            # https://en.wikipedia.org/wiki/Proof_that_22/7_exceeds_%CF%80
            ltx = LatexData(latex=r'$\Sigma \Nu$')
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

    def new_variable_record_input(self, name: str, latex_obj: Optional[LatexData] = None, created_by: str = None,
                                  notes: str = None, dimensions: int = 1, unit_id: int = 1,
                                  type_name='Unassigned') -> NewVariableRecordInput:
        if latex_obj is None:
            latex_obj = self.grouped_data.iloc[0].latex_obj

        if created_by is None:
            created_by = self.my_conn['db_params']['user']

        rcd_input = dict(name=name, latex_obj=latex_obj, created_by=created_by, notes=notes,
                         dimensions=dimensions, unit_id=unit_id, type_name=type_name)

        vri_input = NewVariableRecordInput(**rcd_input)
        return vri_input


class Variables(PhysicsObjects):
    """Class that manages variable records, independently of how they are grouped"""
    def __init__(self, *args, table_name: str = 'variable', **kwargs):
        super().__init__(*args, table_name=table_name, **kwargs)

    def record(self, an_id: int = None):
        phy_obj = super().record(an_id)
        rcd = VariableRecord(*phy_obj)
        return rcd
